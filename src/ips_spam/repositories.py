from __future__ import annotations

import re
from datetime import datetime
from typing import Iterable, Sequence

from src.ips_spam.models import AsnRecord, SyncMetrics


IDENTIFIER_PATTERN = re.compile(
    r'^[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)?$'
)


def validate_identifier(value: str, field: str) -> str:
    if IDENTIFIER_PATTERN.fullmatch(value) is None:
        raise ValueError(f'{field} contiene un identificador no válido: {value}')
    return value


class ClickHouseSpamRepository:
    SIMPLE_COLUMNS = ('VALOR',)
    ASN_COLUMNS = (
        'POSICION',
        'TENDENCIA',
        'SPAM_SCORE',
        'IMPACTOS',
        'PROVEEDOR',
        'ASN',
    )

    def __init__(
        self,
        db,
        audit_table: str = 'spam.UCEPRTC_AUDITORIA',
        batch_size: int = 10000,
    ):
        if batch_size < 1 or batch_size > 1000000:
            raise ValueError('batch_size debe estar entre 1 y 1000000')
        self.db = db
        self.client = db.getReference()
        self.audit_table = validate_identifier(audit_table, 'audit_table')
        self.batch_size = int(batch_size)

    def sync_values(
        self,
        target_table: str,
        values: Sequence[str],
        load_time: datetime,
    ) -> SyncMetrics:
        target = validate_identifier(target_table, 'target_table')
        incoming = self._derived_table(target, '__INCOMING')
        next_table = self._derived_table(target, '__NEXT')
        self._truncate(incoming)
        self._truncate(next_table)
        self._insert_batches(
            incoming,
            ((value,) for value in values),
            self.SIMPLE_COLUMNS,
        )

        inserted = self._scalar(
            f'SELECT count() FROM {incoming} i LEFT ANTI JOIN {target} t '
            'ON i.VALOR = t.VALOR'
        )
        deleted = self._scalar(
            f'SELECT count() FROM {target} t LEFT ANTI JOIN {incoming} i '
            'ON i.VALOR = t.VALOR'
        )
        unchanged = self._scalar(
            f'SELECT count() FROM {incoming} i INNER JOIN {target} t '
            'ON i.VALOR = t.VALOR'
        )
        timestamp = self._timestamp_expression(load_time)
        self.db.query(
            f'''
            INSERT INTO {next_table}
            SELECT
                i.VALOR,
                if(t.VALOR = '', {timestamp}, t.FECHA_INSERCION),
                if(t.VALOR = '', {timestamp}, t.FECHA_MODIFICACION)
            FROM {incoming} i
            LEFT JOIN {target} t ON i.VALOR = t.VALOR
            '''.strip()
        )
        self._publish(target, next_table, incoming)
        return SyncMetrics(
            source_rows=len(values),
            inserted=inserted,
            updated=0,
            deleted=deleted,
            unchanged=unchanged,
        )

    def sync_asn(
        self,
        target_table: str,
        records: Sequence[AsnRecord],
        load_time: datetime,
    ) -> SyncMetrics:
        target = validate_identifier(target_table, 'target_table')
        incoming = self._derived_table(target, '__INCOMING')
        next_table = self._derived_table(target, '__NEXT')
        self._truncate(incoming)
        self._truncate(next_table)
        self._insert_batches(
            incoming,
            (record.to_clickhouse_row() for record in records),
            self.ASN_COLUMNS,
        )

        difference = self._asn_difference('i', 't')
        inserted = self._scalar(
            f'SELECT count() FROM {incoming} i LEFT ANTI JOIN {target} t '
            'ON i.ASN = t.ASN'
        )
        deleted = self._scalar(
            f'SELECT count() FROM {target} t LEFT ANTI JOIN {incoming} i '
            'ON i.ASN = t.ASN'
        )
        updated = self._scalar(
            f'SELECT count() FROM {incoming} i INNER JOIN {target} t '
            f'ON i.ASN = t.ASN WHERE {difference}'
        )
        unchanged = len(records) - inserted - updated
        timestamp = self._timestamp_expression(load_time)
        self.db.query(
            f'''
            INSERT INTO {next_table}
            SELECT
                i.POSICION,
                i.TENDENCIA,
                i.SPAM_SCORE,
                i.IMPACTOS,
                i.PROVEEDOR,
                i.ASN,
                if(t.ASN = '', {timestamp}, t.FECHA_INSERCION),
                if(t.ASN = '' OR {difference},
                   {timestamp}, t.FECHA_MODIFICACION)
            FROM {incoming} i
            LEFT JOIN {target} t ON i.ASN = t.ASN
            '''.strip()
        )
        self._publish(target, next_table, incoming)
        return SyncMetrics(
            source_rows=len(records),
            inserted=inserted,
            updated=updated,
            deleted=deleted,
            unchanged=unchanged,
        )

    def insert_audit(
        self,
        run_id,
        source: str,
        target_table: str,
        started_at: datetime,
        finished_at: datetime,
        status: str,
        metrics: SyncMetrics,
        error_detail: str = '',
    ) -> None:
        self.client.insert(
            self.audit_table,
            [
                (
                    run_id,
                    source,
                    target_table,
                    started_at,
                    finished_at,
                    status,
                    metrics.source_rows,
                    metrics.inserted,
                    metrics.updated,
                    metrics.deleted,
                    metrics.unchanged,
                    error_detail,
                )
            ],
            column_names=[
                'ID_EJECUCION',
                'FUENTE',
                'TABLA_DESTINO',
                'FECHA_INICIO',
                'FECHA_FIN',
                'ESTADO',
                'REGISTROS_FUENTE',
                'INSERTADOS',
                'ACTUALIZADOS',
                'ELIMINADOS',
                'SIN_CAMBIOS',
                'DETALLE_ERROR',
            ],
        )

    def _publish(self, target: str, next_table: str, incoming: str) -> None:
        self.db.query(f'EXCHANGE TABLES {target} AND {next_table}')
        self._truncate(next_table)
        self._truncate(incoming)

    def _truncate(self, table: str) -> None:
        self.db.query(f'TRUNCATE TABLE {table}')

    def _insert_batches(
        self,
        table: str,
        rows: Iterable[Sequence[object]],
        columns: Sequence[str],
    ) -> None:
        batch = []
        for row in rows:
            batch.append(tuple(row))
            if len(batch) >= self.batch_size:
                self.client.insert(table, batch, column_names=list(columns))
                batch = []
        if batch:
            self.client.insert(table, batch, column_names=list(columns))

    def _scalar(self, query: str) -> int:
        rows = self.db.fetch(query)
        return int(rows[0][0]) if rows else 0

    @staticmethod
    def _derived_table(target: str, suffix: str) -> str:
        return validate_identifier(target + suffix, 'staging_table')

    @staticmethod
    def _timestamp_expression(value: datetime) -> str:
        normalized = value.strftime('%Y-%m-%d %H:%M:%S.%f')
        return (
            f"toDateTime64('{normalized}', 6, 'America/Lima')"
        )

    @staticmethod
    def _asn_difference(incoming_alias: str, target_alias: str) -> str:
        pairs = (
            ('POSICION', 'POSICION'),
            ('TENDENCIA', 'TENDENCIA'),
            ('SPAM_SCORE', 'SPAM_SCORE'),
            ('IMPACTOS', 'IMPACTOS'),
            ('PROVEEDOR', 'PROVEEDOR'),
        )
        return ' OR '.join(
            f'{incoming_alias}.{incoming} != {target_alias}.{target}'
            for incoming, target in pairs
        )
