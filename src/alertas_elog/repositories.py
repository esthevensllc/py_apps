from __future__ import annotations

import datetime as dt
import re
import uuid
from typing import List, Mapping, Optional, Sequence, Tuple

from src.alertas_elog.models import (
    AlertRecord,
    LIMA_TZ,
    RouterMetricRecord,
    ServerAvailabilityRecord,
)


IDENTIFIER_PATTERN = re.compile(
    r'^[A-Za-z][A-Za-z0-9_$#]*(?:\.[A-Za-z][A-Za-z0-9_$#]*)?$'
)


def validate_identifier(value: str, field: str) -> str:
    if IDENTIFIER_PATTERN.fullmatch(value) is None:
        raise ValueError(f'{field} contiene un identificador no válido: {value}')
    return value


class ClickHouseCollectorAlertsRepository:
    SELECT_COLUMNS = (
        'id, hostname, ip, fecha_inicio, fecha_fin, nombre, umbral, '
        'porcentaje_indicador, estado, fecha_envio, version'
    )

    def __init__(self, db, table: str = 'cgnat.collector_alerts'):
        self.db = db
        self.table = validate_identifier(table, 'source_table')

    def fetch_batch(
        self,
        batch_size: int,
        full_sync: bool,
        lookback_hours: int,
        cursor: Optional[Tuple[int, str]] = None,
    ) -> List[AlertRecord]:
        query = self.build_query(
            batch_size=batch_size,
            full_sync=full_sync,
            lookback_hours=lookback_hours,
            cursor=cursor,
        )
        rows = self.db.fetch(query)
        return [AlertRecord.from_clickhouse_row(row) for row in rows]

    def build_query(
        self,
        batch_size: int,
        full_sync: bool,
        lookback_hours: int,
        cursor: Optional[Tuple[int, str]] = None,
    ) -> str:
        if batch_size < 1 or batch_size > 100000:
            raise ValueError('batch_size debe estar entre 1 y 100000')
        if lookback_hours < 1 or lookback_hours > 8760:
            raise ValueError('lookback_hours debe estar entre 1 y 8760')

        conditions = []
        if not full_sync:
            conditions.append(
                "(estado = 'ACTIVE' "
                "OR fecha_envio >= now64(6, 'America/Lima') "
                f'- INTERVAL {int(lookback_hours)} HOUR '
                "OR fecha_fin >= now64(6, 'America/Lima') "
                f'- INTERVAL {int(lookback_hours)} HOUR)'
            )

        if cursor is not None:
            version, record_id = cursor
            normalized_id = str(uuid.UUID(record_id))
            conditions.append(
                f'(version > {int(version)} OR '
                f"(version = {int(version)} AND id > toUUID('{normalized_id}')))"
            )

        where_clause = ''
        if conditions:
            where_clause = 'WHERE ' + ' AND '.join(conditions)

        return f"""
        SELECT {self.SELECT_COLUMNS}
        FROM {self.table} FINAL
        {where_clause}
        ORDER BY version ASC, id ASC
        LIMIT {int(batch_size)}
        """.strip()


class ClickHouseRoutersElogRepository:
    def __init__(
        self,
        sources,
        table_prefix: str = 'cgnat.huawei_cgn_nat_v2',
        now_provider=None,
    ):
        self.sources = self._normalize_sources(sources)
        self.table_prefix = validate_identifier(
            table_prefix,
            'routers_source_prefix',
        )
        self.now_provider = now_provider or (lambda: dt.datetime.now(LIMA_TZ))

    def fetch_latest(self) -> RouterMetricRecord:
        reference = self.reference_time()
        query = self.build_query(reference)
        router_ips = set()
        for source_name, db in self.sources:
            rows = db.fetch(query)
            for row in rows:
                value = (
                    row.get('router_ip')
                    if isinstance(row, Mapping)
                    else row[0]
                )
                if value is not None and str(value).strip():
                    router_ips.add(str(value))
            print(
                f'ROUTERS_SOURCE host={source_name} '
                f'rows={len(rows)} unique_total={len(router_ips)}'
            )

        fecha_medicion = reference.replace(
            minute=(reference.minute // 5) * 5,
            second=0,
            microsecond=0,
        )
        return RouterMetricRecord.from_clickhouse_row(
            (len(router_ips), fecha_medicion)
        )

    def build_query(self, reference=None) -> str:
        reference = self.reference_time(reference)
        tables = self.source_tables(reference)
        sources = '\nUNION ALL\n'.join(
            'SELECT router_ip, event_time FROM ' + table
            for table in tables
        )
        reference_value = reference.strftime('%Y-%m-%d %H:%M:%S.%f')
        return f"""
        WITH toDateTime64(
            '{reference_value}',
            6,
            'America/Lima'
        ) AS fecha_consulta
        SELECT DISTINCT router_ip
        FROM (
            {sources}
        )
        WHERE event_time >= (fecha_consulta - toIntervalMinute(5))
          AND event_time <= fecha_consulta
          AND router_ip IS NOT NULL
          AND toString(router_ip) != ''
        """.strip()

    def source_tables(self, reference=None) -> List[str]:
        reference = self.reference_time(reference)
        window_start = reference - dt.timedelta(minutes=5)
        dates = sorted({window_start.date(), reference.date()})
        return [
            f'{self.table_prefix}_{date:%Y_%m_%d}'
            for date in dates
        ]

    def reference_time(self, reference=None):
        reference = reference or self.now_provider()
        if reference.tzinfo is None:
            reference = reference.replace(tzinfo=LIMA_TZ)
        else:
            reference = reference.astimezone(LIMA_TZ)
        return reference

    @staticmethod
    def _normalize_sources(sources):
        if isinstance(sources, (list, tuple)):
            candidates = list(sources)
        else:
            candidates = [('clickhouse_1', sources)]

        normalized = []
        for index, source in enumerate(candidates, 1):
            if isinstance(source, tuple) and len(source) == 2:
                source_name, db = source
            else:
                source_name, db = f'clickhouse_{index}', source
            normalized.append((str(source_name), db))
        if not normalized:
            raise ValueError('Debe configurarse al menos un origen de routers')
        return normalized


class OracleAlertasElogRepository:
    TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF6 TZH:TZM'

    def __init__(self, db, table: str = 'ALERTAS_ELOG', oracle_module=None):
        self.db = db
        self.table = validate_identifier(table, 'target_table')
        if oracle_module is None:
            import cx_Oracle as oracle_module
        self.oracle = oracle_module

    def upsert(self, records: Sequence[AlertRecord], batch_size: int) -> None:
        if not records:
            return
        config = {
            'template': self.merge_sql(),
            'bindings': self.bindings(),
            'row_type': 'object',
            'limit_to_commit': batch_size,
        }
        self.db.save_from_array2(
            config,
            [record.to_oracle_row() for record in records],
        )

    def merge_sql(self) -> str:
        timestamp_format = self.TIMESTAMP_FORMAT
        return f"""
        MERGE INTO {self.table} target
        USING (
            SELECT
                :id id,
                :hostname hostname,
                :ip ip,
                TO_TIMESTAMP_TZ(:fecha_inicio, '{timestamp_format}') fecha_inicio,
                TO_TIMESTAMP_TZ(:fecha_fin, '{timestamp_format}') fecha_fin,
                :nombre nombre,
                :umbral umbral,
                :porcentaje_indicador porcentaje_indicador,
                :estado estado,
                TO_TIMESTAMP_TZ(:fecha_envio, '{timestamp_format}') fecha_envio
            FROM dual
        ) source
        ON (target.id = source.id)
        WHEN MATCHED THEN UPDATE SET
            target.hostname = source.hostname,
            target.ip = source.ip,
            target.fecha_inicio = source.fecha_inicio,
            target.fecha_fin = source.fecha_fin,
            target.nombre = source.nombre,
            target.umbral = source.umbral,
            target.porcentaje_indicador = source.porcentaje_indicador,
            target.estado = source.estado,
            target.fecha_envio = source.fecha_envio
        WHEN NOT MATCHED THEN INSERT (
            id, hostname, ip, fecha_inicio, fecha_fin, nombre,
            umbral, porcentaje_indicador, estado, fecha_envio
        ) VALUES (
            source.id, source.hostname, source.ip, source.fecha_inicio,
            source.fecha_fin, source.nombre, source.umbral,
            source.porcentaje_indicador, source.estado, source.fecha_envio
        )
        """.strip()

    def bindings(self):
        return {
            'id': self.oracle.STRING,
            'hostname': self.oracle.STRING,
            'ip': self.oracle.STRING,
            'fecha_inicio': self.oracle.STRING,
            'fecha_fin': self.oracle.STRING,
            'nombre': self.oracle.STRING,
            'umbral': self.oracle.NUMBER,
            'porcentaje_indicador': self.oracle.NUMBER,
            'estado': self.oracle.STRING,
            'fecha_envio': self.oracle.STRING,
        }


class OracleServerAvailabilityRepository:
    TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF6 TZH:TZM'

    def __init__(self, db, table: str = 'ALERTAS_ELOG', oracle_module=None):
        self.db = db
        self.table = validate_identifier(table, 'target_table')
        if oracle_module is None:
            import cx_Oracle as oracle_module
        self.oracle = oracle_module

    def upsert(self, records: Sequence[ServerAvailabilityRecord]) -> None:
        if not records:
            return
        config = {
            'template': self.merge_sql(),
            'bindings': {
                'id': self.oracle.STRING,
                'hostname': self.oracle.STRING,
                'ip': self.oracle.STRING,
                'nombre': self.oracle.STRING,
                'umbral': self.oracle.NUMBER,
                'porcentaje_indicador': self.oracle.NUMBER,
                'estado': self.oracle.STRING,
                'fecha_envio': self.oracle.STRING,
            },
            'row_type': 'object',
            'limit_to_commit': len(records),
        }
        self.db.save_from_array2(
            config,
            [record.to_oracle_row() for record in records],
        )

    def merge_sql(self) -> str:
        timestamp_format = self.TIMESTAMP_FORMAT
        return f"""
        MERGE INTO {self.table} target
        USING (
            SELECT
                :id id,
                :hostname hostname,
                :ip ip,
                :nombre nombre,
                :umbral umbral,
                :porcentaje_indicador porcentaje_indicador,
                :estado estado,
                TO_TIMESTAMP_TZ(
                    :fecha_envio,
                    '{timestamp_format}'
                ) fecha_envio
            FROM dual
        ) source
        ON (target.id = source.id)
        WHEN MATCHED THEN UPDATE SET
            target.hostname = source.hostname,
            target.ip = source.ip,
            target.nombre = source.nombre,
            target.umbral = source.umbral,
            target.porcentaje_indicador = source.porcentaje_indicador,
            target.fecha_inicio = CASE
                WHEN target.estado = 'ACTIVE' AND source.estado = 'ACTIVE'
                    THEN target.fecha_inicio
                WHEN source.estado = 'ACTIVE'
                    THEN source.fecha_envio
                ELSE target.fecha_inicio
            END,
            target.fecha_fin = CASE
                WHEN target.estado = 'ACTIVE' AND source.estado = 'CLEARED'
                    THEN source.fecha_envio
                WHEN source.estado = 'ACTIVE'
                    THEN NULL
                ELSE target.fecha_fin
            END,
            target.estado = source.estado,
            target.fecha_envio = source.fecha_envio
        WHEN NOT MATCHED THEN INSERT (
            id, hostname, ip, fecha_inicio, fecha_fin, nombre,
            umbral, porcentaje_indicador, estado, fecha_envio
        ) VALUES (
            source.id, source.hostname, source.ip, source.fecha_envio,
            NULL, source.nombre, source.umbral,
            source.porcentaje_indicador, source.estado, source.fecha_envio
        )
        WHERE source.estado = 'ACTIVE'
        """.strip()


class OracleRoutersElogRepository:
    TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF6'

    def __init__(self, db, table: str = 'ROUTERS_ELOG', oracle_module=None):
        self.db = db
        self.table = validate_identifier(table, 'routers_target_table')
        if oracle_module is None:
            import cx_Oracle as oracle_module
        self.oracle = oracle_module

    def upsert(self, record: RouterMetricRecord) -> None:
        config = {
            'template': self.merge_sql(),
            'bindings': {
                'routers_unicos': self.oracle.NUMBER,
                'fecha_medicion': self.oracle.STRING,
            },
            'row_type': 'object',
            'limit_to_commit': 1,
        }
        self.db.save_from_array2(config, [record.to_oracle_row()])

    def merge_sql(self) -> str:
        return f"""
        MERGE INTO {self.table} target
        USING (
            SELECT
                :routers_unicos routers_unicos,
                TO_TIMESTAMP(
                    SUBSTR(:fecha_medicion, 1, 26),
                    '{self.TIMESTAMP_FORMAT}'
                ) fecha_medicion
            FROM dual
        ) source
        ON (target.fecha_medicion = source.fecha_medicion)
        WHEN MATCHED THEN UPDATE SET
            target.routers_unicos = source.routers_unicos,
            target.fecha_carga = SYSTIMESTAMP
        WHEN NOT MATCHED THEN INSERT (
            routers_unicos, fecha_medicion, fecha_carga
        ) VALUES (
            source.routers_unicos, source.fecha_medicion, SYSTIMESTAMP
        )
        """.strip()
