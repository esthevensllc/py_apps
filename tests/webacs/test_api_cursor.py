import importlib
import sys
import types
from unittest import TestCase
from unittest.mock import Mock, patch


class ApiCursorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        # The cursor does not use OracleWriter; avoid requiring the Oracle and
        # ClickHouse drivers just to exercise WebACS response handling.
        writer_module = types.ModuleType('src.shared.batch.writers')
        writer_module.OracleWriter = object
        with patch.dict(sys.modules, {'src.shared.batch.writers': writer_module}):
            cls.services = importlib.import_module('src.webacs.api.services')

    def make_cursor(self, uris):
        cursor = self.services.ApiCursor('alarm', uris, 1000)
        cursor.base_url = 'https://example.invalid'
        return cursor

    def test_missing_query_response_reports_api_payload(self):
        cursor = self.make_cursor(['alarms?alarmFoundAt=range'])
        response = Mock(status_code=200)
        response.json.return_value = {'error': 'invalid query'}

        with patch.object(self.services.requests, 'get', return_value=response):
            with self.assertRaisesRegex(ValueError, 'sin queryResponse.*invalid query'):
                cursor.subscribe()

    def test_empty_first_query_does_not_skip_second_query(self):
        cursor = self.make_cursor([
            'alarms?alarmFoundAt=range', 'alarms?lastUpdatedAt=range',
        ])
        empty = Mock(status_code=200)
        empty.json.return_value = {'queryResponse': {'@first': 0, '@count': 0}}
        populated = Mock(status_code=200)
        populated.json.return_value = {
            'queryResponse': {
                '@first': 0, '@count': 1,
                'entity': [{'@dtoType': 'alarmDto', 'alarmDto': {'@id': 42}}],
            },
        }
        batches = []
        cursor.on_next(batches.append)

        with patch.object(self.services.requests, 'get', side_effect=[empty, populated]) as get:
            cursor.subscribe()

        self.assertEqual(get.call_count, 2)
        self.assertEqual(batches, [[{'@id': 42, 'src_filter_by': 'lastUpdatedAt'}]])
