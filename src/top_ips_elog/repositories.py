import datetime as dt
import re
from typing import Iterable, Mapping, Sequence

from src.top_ips_elog.models import DNS_IPS, SOURCE_COLUMNS, TopQueryDefinition


SOURCE_TABLE_PATTERN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?$')
TABLE_PART_PATTERN = re.compile(r'^[A-Za-z_][A-Za-z0-9_-]*$')


def validate_source_table_prefix(value: str) -> str:
    if SOURCE_TABLE_PATTERN.fullmatch(value) is None:
        raise ValueError(f'source_table_prefix no es válido: {value}')
    return value


def quote_identifier(value: str, field: str) -> str:
    if TABLE_PART_PATTERN.fullmatch(value) is None:
        raise ValueError(f'{field} no es válido: {value}')
    return f'`{value}`'


def quote_table(database: str, table: str) -> str:
    return f'{quote_identifier(database, "target_database")}.{quote_identifier(table, "target_table")}'


def row_value(row: object, index: int, name: str) -> object:
    if isinstance(row, Mapping):
        return row[name]
    return row[index]  # type: ignore[index]


class ClickHouseTopIpsSourceRepository:
    def __init__(self, db, table_prefix: str = 'cgnat.huawei_cgn_nat_v2'):
        self.db = db
        self.table_prefix = validate_source_table_prefix(table_prefix)

    def source_table(self, process_date: dt.date) -> str:
        return f'{self.table_prefix}_{process_date:%Y_%m_%d}'

    def describe(self, process_date: dt.date) -> Sequence[Sequence[str]]:
        rows = self.db.fetch(f'DESCRIBE TABLE {self.source_table(process_date)}')
        schema = tuple((str(row_value(row, 0, 'name')), str(row_value(row, 1, 'type'))) for row in rows)
        by_name = dict(schema)
        missing = [column for column in SOURCE_COLUMNS if column not in by_name]
        if missing:
            raise RuntimeError('La tabla origen no contiene las columnas requeridas: ' + ', '.join(missing))
        return tuple((column, by_name[column]) for column in SOURCE_COLUMNS)

    def fetch_top_rows(self, definition: TopQueryDefinition, process_date: dt.date) -> Sequence[Sequence[object]]:
        rows = self.db.fetch(self.build_query(definition, process_date))
        for row in rows:
            if len(row) != len(SOURCE_COLUMNS):
                raise RuntimeError(f'La consulta {definition.key} devolvió {len(row)} columnas; se esperaban {len(SOURCE_COLUMNS)}')
        return rows

    def build_query(self, definition: TopQueryDefinition, process_date: dt.date) -> str:
        table = self.source_table(process_date)
        selected_columns = ',\n    '.join(f't.{column}' for column in SOURCE_COLUMNS)
        dns_ips = ', '.join(f"'{ip}'" for ip in DNS_IPS)
        if definition.key == 'destination_no_dns':
            top_column, inner_filter, outer_filter, limit = 'destination_ip', f'destination_ip NOT IN ({dns_ips})', '', 20
        elif definition.key == 'private_dns':
            top_column, inner_filter, outer_filter, limit = 'private_ip', f'destination_ip IN ({dns_ips})', f'WHERE t.destination_ip IN ({dns_ips})', 10
        elif definition.key == 'private_smtp_25':
            top_column, inner_filter, outer_filter, limit = 'private_ip', 'destination_port = 25', 'WHERE t.destination_port = 25', 50
        elif definition.key == 'private_usage':
            top_column, inner_filter, outer_filter, limit = 'private_ip', 'destination_port != 25', 'WHERE t.destination_port != 25', 100
        else:
            raise ValueError(f'Consulta top no soportada: {definition.key}')
        return f"""
        SELECT
            {selected_columns}
        FROM {table} AS t
        INNER JOIN
        (
            SELECT {top_column}
            FROM {table}
            WHERE {inner_filter}
            GROUP BY {top_column}
            ORDER BY count() DESC
            LIMIT {limit}
        ) AS top ON t.{top_column} = top.{top_column}
        {outer_filter}
        """.strip()


class ClickHouseTopIpsTargetRepository:
    METADATA_COLUMNS = (('fecha_proceso', 'Date'), ('nodo_origen', 'LowCardinality(String)'))

    def __init__(self, db, database: str = 'elog', batch_size: int = 10000):
        if batch_size < 1 or batch_size > 100000:
            raise ValueError('batch_size debe estar entre 1 y 100000')
        self.db = db
        self.client = db.getReference()
        self.database = quote_identifier(database, 'target_database')[1:-1]
        self.batch_size = int(batch_size)

    def ensure_table(self, target_table: str, source_schema: Sequence[Sequence[str]]) -> None:
        table = quote_table(self.database, target_table)
        columns = list(source_schema) + list(self.METADATA_COLUMNS)
        column_sql = ',\n    '.join(f'{quote_identifier(name, "column")} {column_type}' for name, column_type in columns)
        self.db.query(f"""
            CREATE TABLE IF NOT EXISTS {table}
            (
                {column_sql}
            )
            ENGINE = MergeTree
            PARTITION BY fecha_proceso
            ORDER BY (fecha_proceso, nodo_origen, event_time, router_ip, private_ip, public_ip, destination_ip, destination_port)
            """.strip())
        expected = dict(columns)
        actual = dict(self._describe(table))
        incompatible = [name for name, column_type in expected.items() if actual.get(name) != column_type]
        if incompatible:
            raise RuntimeError(f'La tabla destino {target_table} tiene un esquema incompatible en: {", ".join(incompatible)}')

    def delete_process_date(self, target_table: str, process_date: dt.date) -> None:
        table = quote_table(self.database, target_table)
        self.db.query(f"ALTER TABLE {table} DELETE WHERE fecha_proceso = toDate('{process_date.isoformat()}') SETTINGS mutations_sync = 2")

    def insert_rows(self, target_table: str, rows: Iterable[Sequence[object]], process_date: dt.date, source_host: str) -> int:
        table = quote_table(self.database, target_table)
        columns = list(SOURCE_COLUMNS) + [name for name, _ in self.METADATA_COLUMNS]
        batch, total = [], 0
        for row in rows:
            batch.append(tuple(row) + (process_date, source_host))
            if len(batch) >= self.batch_size:
                self.client.insert(table, batch, column_names=columns)
                total += len(batch)
                batch = []
        if batch:
            self.client.insert(table, batch, column_names=columns)
            total += len(batch)
        return total

    def _describe(self, quoted_table: str) -> Sequence[Sequence[str]]:
        rows = self.db.fetch(f'DESCRIBE TABLE {quoted_table}')
        return tuple((str(row_value(row, 0, 'name')), str(row_value(row, 1, 'type'))) for row in rows)
