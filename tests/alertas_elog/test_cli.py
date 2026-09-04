import os
import unittest
from unittest.mock import patch

from src.alertas_elog.cli import (
    clickhouse_hosts_from_environment,
    clickhouse_settings_from_environment,
    configure_clickhouse_connections,
    parse_bool,
)


class FakeSharedClickHouse:
    def __init__(self, fail=False):
        self.calls = []
        self.closed = False
        self.fail = fail

    def connectWithConfig(self, key, config):
        self.calls.append((key, config))
        if self.fail:
            raise RuntimeError('connection failed')

    def close(self):
        self.closed = True


class AlertasElogCLITest(unittest.TestCase):
    def test_builds_dedicated_clickhouse_settings(self):
        source_values = {
            'DB_CH_ELOG_HOST': '10.96.167.132',
            'DB_CH_ELOG_PORT': '8123',
            'DB_CH_ELOG_DATABASE': 'cgnat',
            'DB_CH_ELOG_USERNAME': 'admin',
            'DB_CH_ELOG_PASSWORD': 'secret',
        }
        with patch.dict(os.environ, source_values, clear=True):
            settings = clickhouse_settings_from_environment()

        self.assertEqual('10.96.167.132', settings['host'])
        self.assertEqual(8123, settings['port'])
        self.assertEqual('cgnat', settings['database'])
        self.assertEqual('admin', settings['user'])

    def test_reads_and_deduplicates_four_hosts(self):
        with patch.dict(
            os.environ,
            {
                'DB_CH_ELOG_HOSTS': (
                    '10.96.167.132,10.96.167.133,10.96.167.132,'
                    '10.96.167.134,10.96.167.135'
                ),
            },
            clear=True,
        ):
            hosts = clickhouse_hosts_from_environment()

        self.assertEqual(
            [
                '10.96.167.132',
                '10.96.167.133',
                '10.96.167.134',
                '10.96.167.135',
            ],
            hosts,
        )

    def test_registers_one_shared_connection_per_host(self):
        source_values = {
            'DB_CH_ELOG_HOSTS': (
                '10.96.167.132,10.96.167.133,'
                '10.96.167.134,10.96.167.135'
            ),
            'DB_CH_ELOG_PORT': '8123',
            'DB_CH_ELOG_DATABASE': 'cgnat',
            'DB_CH_ELOG_USERNAME': 'admin',
            'DB_CH_ELOG_PASSWORD': 'secret',
        }
        created = []

        def factory():
            clickhouse = FakeSharedClickHouse()
            created.append(clickhouse)
            return clickhouse

        with patch.dict(os.environ, source_values, clear=True):
            connections = configure_clickhouse_connections(factory)

        self.assertEqual(4, len(connections))
        self.assertEqual(4, len(created))
        self.assertEqual(
            [host for host, _ in connections],
            [
                '10.96.167.132',
                '10.96.167.133',
                '10.96.167.134',
                '10.96.167.135',
            ],
        )
        for index, clickhouse in enumerate(created, 1):
            key, config = clickhouse.calls[0]
            self.assertEqual(f'clickhouse_elog_{index}', key)
            self.assertEqual('cgnat', config['database'])
            self.assertEqual(8123, config['port'])

    def test_closes_all_connections_when_one_host_fails(self):
        source_values = {
            'DB_CH_ELOG_HOSTS': '10.96.167.132,10.96.167.133',
            'DB_CH_ELOG_PORT': '8123',
            'DB_CH_ELOG_DATABASE': 'cgnat',
            'DB_CH_ELOG_USERNAME': 'admin',
            'DB_CH_ELOG_PASSWORD': 'secret',
        }
        created = []

        def factory():
            clickhouse = FakeSharedClickHouse(fail=len(created) == 1)
            created.append(clickhouse)
            return clickhouse

        with patch.dict(os.environ, source_values, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'connection failed'):
                configure_clickhouse_connections(factory)

        self.assertEqual(2, len(created))
        self.assertTrue(all(clickhouse.closed for clickhouse in created))

    def test_parse_bool(self):
        self.assertTrue(parse_bool('true'))
        self.assertFalse(parse_bool('false'))
        with self.assertRaises(ValueError):
            parse_bool('maybe')


if __name__ == '__main__':
    unittest.main()
