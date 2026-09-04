import datetime as dt
import types
import unittest

from src.alertas_elog.models import AlertRecord, RouterMetricRecord
from src.alertas_elog.repositories import (
    ClickHouseCollectorAlertsRepository,
    ClickHouseRoutersElogRepository,
    OracleAlertasElogRepository,
    OracleRoutersElogRepository,
)


ROW_ID = 'a2254327-512e-4567-830d-a5bfe16ccbc2'


def sample_record(version=123):
    return AlertRecord.from_clickhouse_row(
        (
            ROW_ID,
            'host',
            '10.0.0.1',
            dt.datetime(2026, 7, 16, 10, 0),
            None,
            'CPU',
            80,
            90,
            'ACTIVE',
            dt.datetime(2026, 7, 16, 10, 1),
            version,
        )
    )


class FakeClickHouse:
    def __init__(self, rows=()):
        self.rows = list(rows)
        self.queries = []

    def fetch(self, query):
        self.queries.append(query)
        return self.rows


class FakeOracle:
    def __init__(self):
        self.calls = []

    def save_from_array2(self, config, rows):
        self.calls.append((config, rows))


class ClickHouseRepositoryTest(unittest.TestCase):
    def test_incremental_query_uses_final_window_and_keyset_cursor(self):
        repository = ClickHouseCollectorAlertsRepository(FakeClickHouse())
        query = repository.build_query(
            batch_size=5000,
            full_sync=False,
            lookback_hours=48,
            cursor=(122, ROW_ID),
        )

        self.assertIn('FROM cgnat.collector_alerts FINAL', query)
        self.assertIn("estado = 'ACTIVE'", query)
        self.assertIn('INTERVAL 48 HOUR', query)
        self.assertIn('version > 122', query)
        self.assertIn("id > toUUID('" + ROW_ID + "')", query)
        self.assertIn('ORDER BY version ASC, id ASC', query)

    def test_full_query_has_no_lookback_filter(self):
        repository = ClickHouseCollectorAlertsRepository(FakeClickHouse())
        query = repository.build_query(1000, True, 48)
        self.assertNotIn('INTERVAL 48 HOUR', query)
        self.assertNotIn('WHERE', query)

    def test_fetch_batch_maps_rows(self):
        clickhouse = FakeClickHouse(
            [
                (
                    ROW_ID,
                    'host',
                    '10.0.0.1',
                    dt.datetime(2026, 7, 16, 10, 0),
                    None,
                    'CPU',
                    80,
                    90,
                    'ACTIVE',
                    dt.datetime(2026, 7, 16, 10, 1),
                    123,
                )
            ]
        )
        records = ClickHouseCollectorAlertsRepository(clickhouse).fetch_batch(
            100,
            False,
            48,
        )
        self.assertEqual(1, len(records))
        self.assertEqual(ROW_ID, records[0].id)

    def test_router_query_uses_daily_table_and_five_minute_window(self):
        now = dt.datetime(2026, 7, 16, 18, 45, 13)
        repository = ClickHouseRoutersElogRepository(
            FakeClickHouse(),
            now_provider=lambda: now,
        )

        query = repository.build_query()

        self.assertIn(
            'FROM cgnat.huawei_cgn_nat_v2_2026_07_16',
            query,
        )
        self.assertIn('SELECT DISTINCT router_ip', query)
        self.assertIn('toIntervalMinute(5)', query)
        self.assertIn('2026-07-16 18:45:13.000000', query)

    def test_router_query_includes_both_daily_tables_at_midnight(self):
        now = dt.datetime(2026, 7, 17, 0, 2)
        repository = ClickHouseRoutersElogRepository(
            FakeClickHouse(),
            now_provider=lambda: now,
        )

        self.assertEqual(
            [
                'cgnat.huawei_cgn_nat_v2_2026_07_16',
                'cgnat.huawei_cgn_nat_v2_2026_07_17',
            ],
            repository.source_tables(),
        )

    def test_router_count_is_globally_unique_across_sources(self):
        now = dt.datetime(2026, 7, 16, 18, 45, 13)
        first = FakeClickHouse(
            [('router-a',), ('router-b',), ('router-c',)]
        )
        second = FakeClickHouse(
            [('router-b',), ('router-c',), ('router-d',)]
        )
        repository = ClickHouseRoutersElogRepository(
            [
                ('10.96.167.132', first),
                ('10.96.167.133', second),
            ],
            now_provider=lambda: now,
        )

        record = repository.fetch_latest()

        self.assertEqual(4, record.routers_unicos)
        self.assertEqual(
            '2026-07-16 18:45:00.000000 -05:00',
            record.fecha_medicion,
        )
        self.assertEqual(1, len(first.queries))
        self.assertEqual(1, len(second.queries))


class OracleRepositoryTest(unittest.TestCase):
    def test_upsert_uses_merge_and_object_bindings(self):
        oracle_db = FakeOracle()
        oracle_types = types.SimpleNamespace(STRING='STRING', NUMBER='NUMBER')
        repository = OracleAlertasElogRepository(
            oracle_db,
            oracle_module=oracle_types,
        )

        repository.upsert([sample_record()], batch_size=5000)

        config, rows = oracle_db.calls[0]
        self.assertIn('MERGE INTO ALERTAS_ELOG target', config['template'])
        self.assertIn('WHEN MATCHED THEN UPDATE', config['template'])
        self.assertIn('WHEN NOT MATCHED THEN INSERT', config['template'])
        self.assertIn('TO_TIMESTAMP_TZ(:fecha_inicio', config['template'])
        self.assertEqual('object', config['row_type'])
        self.assertEqual(5000, config['limit_to_commit'])
        self.assertEqual(ROW_ID, rows[0]['id'])
        self.assertNotIn('version', rows[0])

    def test_router_upsert_merges_by_measurement_time(self):
        oracle_db = FakeOracle()
        oracle_types = types.SimpleNamespace(STRING='STRING', NUMBER='NUMBER')
        repository = OracleRoutersElogRepository(
            oracle_db,
            oracle_module=oracle_types,
        )
        record = RouterMetricRecord.from_clickhouse_row(
            (24, dt.datetime(2026, 7, 16, 18, 45))
        )

        repository.upsert(record)

        config, rows = oracle_db.calls[0]
        self.assertIn('MERGE INTO ROUTERS_ELOG target', config['template'])
        self.assertIn(
            'target.fecha_medicion = source.fecha_medicion',
            config['template'],
        )
        self.assertIn(
            'TO_TIMESTAMP(',
            config['template'],
        )
        self.assertNotIn('TO_TIMESTAMP_TZ(', config['template'])
        self.assertEqual(1, config['limit_to_commit'])
        self.assertEqual(24, rows[0]['routers_unicos'])
