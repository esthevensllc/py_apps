import datetime as dt
import unittest

from src.top_ips_elog.models import SOURCE_COLUMNS, TOP_QUERY_DEFINITIONS
from src.top_ips_elog.repositories import (
    ClickHouseTopIpsSourceRepository,
    ClickHouseTopIpsTargetRepository,
)


SOURCE_SCHEMA = tuple((column, 'String') for column in SOURCE_COLUMNS)


class FakeSourceDb:
    def __init__(self, rows=()):
        self.rows = list(rows)
        self.queries = []

    def fetch(self, query):
        self.queries.append(query)
        if query.startswith('DESCRIBE'):
            return SOURCE_SCHEMA
        return self.rows


class FakeTargetClient:
    def __init__(self):
        self.inserts = []

    def insert(self, table, rows, column_names):
        self.inserts.append((table, list(rows), column_names))


class FakeTargetDb:
    def __init__(self):
        self.client = FakeTargetClient()
        self.commands = []

    def getReference(self):
        return self.client

    def query(self, query):
        self.commands.append(query)

    def fetch(self, query):
        self.commands.append(query)
        return SOURCE_SCHEMA + (
            ('fecha_proceso', 'Date'),
            ('nodo_origen', 'LowCardinality(String)'),
        )


class TopIpsSourceRepositoryTest(unittest.TestCase):
    def test_queries_use_requested_daily_table_and_limits(self):
        repository = ClickHouseTopIpsSourceRepository(FakeSourceDb())
        process_date = dt.date(2026, 9, 8)
        expected = {
            'destination_no_dns': ('destination_ip NOT IN', 'LIMIT 20'),
            'private_dns': ('destination_ip IN', 'LIMIT 10'),
            'private_smtp_25': ('destination_port = 25', 'LIMIT 50'),
            'private_usage': ('destination_port != 25', 'LIMIT 100'),
        }
        for definition in TOP_QUERY_DEFINITIONS:
            query = repository.build_query(definition, process_date)
            filter_text, limit = expected[definition.key]
            self.assertIn('FROM cgnat.huawei_cgn_nat_v2_2026_09_08 AS t', query)
            self.assertIn(filter_text, query)
            self.assertIn(limit, query)
            self.assertIn('ORDER BY count() DESC', query)

    def test_describe_keeps_selected_columns_in_requested_order(self):
        schema = ClickHouseTopIpsSourceRepository(FakeSourceDb()).describe(dt.date(2026, 9, 8))
        self.assertEqual(SOURCE_SCHEMA, schema)


class TopIpsTargetRepositoryTest(unittest.TestCase):
    def test_creates_target_with_tracking_columns_and_replaces_day(self):
        db = FakeTargetDb()
        repository = ClickHouseTopIpsTargetRepository(db, batch_size=2)
        repository.ensure_table('Top_IPs_Priv_con_Dst-DNS', SOURCE_SCHEMA)
        repository.delete_process_date('Top_IPs_Priv_con_Dst-DNS', dt.date(2026, 9, 8))

        create_sql = db.commands[0]
        delete_sql = db.commands[-1]
        self.assertIn('CREATE TABLE IF NOT EXISTS `elog`.`Top_IPs_Priv_con_Dst-DNS`', create_sql)
        self.assertIn('`fecha_proceso` Date', create_sql)
        self.assertIn('`nodo_origen` LowCardinality(String)', create_sql)
        self.assertIn("toDate('2026-09-08')", delete_sql)
        self.assertIn('mutations_sync = 2', delete_sql)

    def test_inserts_in_batches_with_process_date_and_source_host(self):
        db = FakeTargetDb()
        repository = ClickHouseTopIpsTargetRepository(db, batch_size=2)
        rows = [tuple(str(index) for _ in SOURCE_COLUMNS) for index in range(3)]

        inserted = repository.insert_rows('Top_IPs_Dst_NO_DNS', rows, dt.date(2026, 9, 8), '10.96.167.132')

        self.assertEqual(3, inserted)
        self.assertEqual([2, 1], [len(call[1]) for call in db.client.inserts])
        self.assertEqual(dt.date(2026, 9, 8), db.client.inserts[0][1][0][-2])
        self.assertEqual('10.96.167.132', db.client.inserts[0][1][0][-1])


if __name__ == '__main__':
    unittest.main()
