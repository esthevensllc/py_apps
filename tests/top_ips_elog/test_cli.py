import datetime as dt
import os
import unittest
from unittest.mock import patch

from src.top_ips_elog.cli import (
    clickhouse_hosts_from_environment,
    clickhouse_settings_from_environment,
    configure_source_connections,
    resolve_process_date,
)


class FakeClickHouse:
    def __init__(self, fail=False):
        self.fail = fail
        self.closed = False

    def connectWithConfig(self, key, config):
        if self.fail:
            raise RuntimeError('connection failed')

    def close(self):
        self.closed = True


class TopIpsCliTest(unittest.TestCase):
    def test_reads_and_deduplicates_source_hosts(self):
        with patch.dict(os.environ, {'TOP_IPS_SOURCE_HOSTS': '10.1.1.1, 10.1.1.2,10.1.1.1'}, clear=True):
            self.assertEqual(['10.1.1.1', '10.1.1.2'], clickhouse_hosts_from_environment())

    def test_builds_distinct_source_and_target_settings(self):
        values = {
            'TOP_IPS_SOURCE_PORT': '8123', 'TOP_IPS_SOURCE_DATABASE': 'cgnat',
            'TOP_IPS_SOURCE_USERNAME': 'reader', 'TOP_IPS_SOURCE_PASSWORD': 'secret',
            'TOP_IPS_TARGET_HOST': '172.19.242.107', 'TOP_IPS_TARGET_PORT': '8123',
            'TOP_IPS_TARGET_DATABASE': 'elog', 'TOP_IPS_TARGET_USERNAME': 'writer',
            'TOP_IPS_TARGET_PASSWORD': 'secret',
        }
        with patch.dict(os.environ, values, clear=True):
            source = clickhouse_settings_from_environment('TOP_IPS_SOURCE', '10.96.167.132')
            target = clickhouse_settings_from_environment('TOP_IPS_TARGET')
        self.assertEqual('10.96.167.132', source['host'])
        self.assertEqual('cgnat', source['database'])
        self.assertEqual('172.19.242.107', target['host'])
        self.assertEqual('elog', target['database'])

    def test_parses_process_date(self):
        self.assertEqual(dt.date(2026, 9, 8), resolve_process_date('2026-09-08'))
        with self.assertRaisesRegex(ValueError, 'YYYY-MM-DD'):
            resolve_process_date('08/09/2026')

    def test_closes_all_source_connections_after_a_connection_error(self):
        values = {
            'TOP_IPS_SOURCE_HOSTS': '10.1.1.1,10.1.1.2',
            'TOP_IPS_SOURCE_PORT': '8123', 'TOP_IPS_SOURCE_DATABASE': 'cgnat',
            'TOP_IPS_SOURCE_USERNAME': 'reader', 'TOP_IPS_SOURCE_PASSWORD': 'secret',
        }
        created = []

        def factory():
            connection = FakeClickHouse(fail=len(created) == 1)
            created.append(connection)
            return connection

        with patch.dict(os.environ, values, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'connection failed'):
                configure_source_connections(factory)
        self.assertTrue(all(connection.closed for connection in created))


if __name__ == '__main__':
    unittest.main()
