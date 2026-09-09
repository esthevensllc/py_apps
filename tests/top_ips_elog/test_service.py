import datetime as dt
import unittest

from src.top_ips_elog.models import SOURCE_COLUMNS, TOP_QUERY_DEFINITIONS
from src.top_ips_elog.service import TopIpsElogLoadService


SCHEMA = tuple((column, 'String') for column in SOURCE_COLUMNS)


class FakeSource:
    def __init__(self, rows):
        self.rows = rows
        self.queries = []

    def describe(self, process_date):
        return SCHEMA

    def fetch_top_rows(self, definition, process_date):
        self.queries.append(definition.key)
        return self.rows


class FakeTarget:
    def __init__(self):
        self.created = []
        self.deleted = []
        self.inserted = []

    def ensure_table(self, table, schema):
        self.created.append((table, schema))

    def delete_process_date(self, table, process_date):
        self.deleted.append((table, process_date))

    def insert_rows(self, table, rows, process_date, host):
        row_list = list(rows)
        self.inserted.append((table, row_list, process_date, host))
        return len(row_list)


class TopIpsElogLoadServiceTest(unittest.TestCase):
    def test_runs_each_query_on_each_node_and_replaces_process_date(self):
        row = tuple('value' for _ in SOURCE_COLUMNS)
        first, second = FakeSource([row]), FakeSource([row, row])
        target = FakeTarget()
        service = TopIpsElogLoadService(
            [('10.96.167.132', first), ('10.96.167.133', second)],
            target,
            TOP_QUERY_DEFINITIONS,
        )

        result = service.execute(dt.date(2026, 9, 8))

        self.assertEqual(4, result['query_count'])
        self.assertEqual(12, result['inserted_rows'])
        self.assertEqual(4, len(first.queries))
        self.assertEqual(4, len(second.queries))
        self.assertEqual(4, len(target.deleted))
        self.assertEqual(8, len(target.inserted))


if __name__ == '__main__':
    unittest.main()
