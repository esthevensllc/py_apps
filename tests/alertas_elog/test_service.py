import types
import unittest

from src.alertas_elog.service import (
    AlertasElogReplicationService,
    MultiSourceAlertasElogReplicationService,
    RoutersElogReplicationService,
)


def record(version, record_id):
    return types.SimpleNamespace(version=version, id=record_id)


class FakeSource:
    def __init__(self, batches):
        self.batches = list(batches)
        self.calls = []

    def fetch_batch(self, **kwargs):
        self.calls.append(kwargs)
        return self.batches.pop(0)


class FakeTarget:
    def __init__(self):
        self.calls = []

    def upsert(self, records, batch_size):
        self.calls.append((records, batch_size))


class FakeRouterSource:
    def __init__(self, record):
        self.record = record

    def fetch_latest(self):
        return self.record


class FakeRouterTarget:
    def __init__(self):
        self.calls = []

    def upsert(self, record):
        self.calls.append(record)


class AlertasElogReplicationServiceTest(unittest.TestCase):
    def test_pages_with_version_and_id_cursor(self):
        id1 = '00000000-0000-0000-0000-000000000001'
        id2 = '00000000-0000-0000-0000-000000000002'
        id3 = '00000000-0000-0000-0000-000000000003'
        source = FakeSource(
            [
                [record(10, id1), record(10, id2)],
                [record(11, id3)],
            ]
        )
        target = FakeTarget()
        service = AlertasElogReplicationService(source, target)

        result = service.execute(
            full_sync=True,
            lookback_hours=48,
            batch_size=2,
        )

        self.assertIsNone(source.calls[0]['cursor'])
        self.assertEqual((10, id2), source.calls[1]['cursor'])
        self.assertEqual(2, len(target.calls))
        self.assertEqual(3, result['processed_rows'])
        self.assertEqual(11, result['max_version'])
        self.assertEqual('full', result['mode'])

    def test_dry_run_does_not_write_oracle(self):
        source = FakeSource([[record(10, '00000000-0000-0000-0000-000000000001')]])
        target = FakeTarget()

        result = AlertasElogReplicationService(source, target).execute(
            full_sync=False,
            lookback_hours=48,
            batch_size=10,
            dry_run=True,
        )

        self.assertEqual([], target.calls)
        self.assertEqual(1, result['processed_rows'])
        self.assertTrue(result['dry_run'])


class MultiSourceAlertasElogReplicationServiceTest(unittest.TestCase):
    def test_processes_every_source_and_summarizes_rows(self):
        id1 = '00000000-0000-0000-0000-000000000001'
        id2 = '00000000-0000-0000-0000-000000000002'
        target = FakeTarget()
        service = MultiSourceAlertasElogReplicationService(
            [
                ('10.96.167.132', FakeSource([[record(10, id1)]])),
                ('10.96.167.133', FakeSource([[record(11, id2)]])),
            ],
            target,
        )

        result = service.execute(batch_size=10)

        self.assertEqual(2, result['source_count'])
        self.assertEqual(2, result['processed_rows'])
        self.assertEqual(2, len(target.calls))
        self.assertEqual(
            {'10.96.167.132', '10.96.167.133'},
            set(result['sources']),
        )


class RoutersElogReplicationServiceTest(unittest.TestCase):
    def test_writes_router_metric(self):
        metric = types.SimpleNamespace(
            routers_unicos=24,
            fecha_medicion='2026-07-16 18:45:00.000000 -05:00',
        )
        target = FakeRouterTarget()

        result = RoutersElogReplicationService(
            FakeRouterSource(metric),
            target,
        ).execute()

        self.assertEqual([metric], target.calls)
        self.assertEqual(24, result['routers_unicos'])

    def test_router_dry_run_does_not_write_oracle(self):
        metric = types.SimpleNamespace(
            routers_unicos=24,
            fecha_medicion='2026-07-16 18:45:00.000000 -05:00',
        )
        target = FakeRouterTarget()

        result = RoutersElogReplicationService(
            FakeRouterSource(metric),
            target,
        ).execute(dry_run=True)

        self.assertEqual([], target.calls)
        self.assertTrue(result['dry_run'])


if __name__ == '__main__':
    unittest.main()
