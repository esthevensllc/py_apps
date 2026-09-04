import datetime as dt
import unittest
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.alertas_elog.models import AlertRecord, RouterMetricRecord


ROW_ID = 'a2254327-512e-4567-830d-a5bfe16ccbc2'


class AlertRecordTest(unittest.TestCase):
    def test_maps_clickhouse_types_to_oracle_values(self):
        record = AlertRecord.from_clickhouse_row(
            (
                ROW_ID,
                'LIMSTELOGF01',
                '10.96.167.132',
                dt.datetime(2026, 7, 16, 10, 0, 1, 123456),
                None,
                'CPU_USAGE',
                80.5,
                92.125,
                'active',
                dt.datetime(
                    2026,
                    7,
                    16,
                    15,
                    0,
                    tzinfo=ZoneInfo('UTC'),
                ),
                123,
            )
        )

        self.assertEqual(ROW_ID, record.id)
        self.assertEqual('ACTIVE', record.estado)
        self.assertEqual(Decimal('80.5'), record.umbral)
        self.assertEqual(Decimal('92.125'), record.porcentaje_indicador)
        self.assertEqual('2026-07-16 10:00:01.123456 -05:00', record.fecha_inicio)
        self.assertEqual('2026-07-16 10:00:00.000000 -05:00', record.fecha_envio)
        self.assertIsNone(record.fecha_fin)

    def test_rejects_state_not_allowed_by_oracle_constraint(self):
        row = [
            ROW_ID,
            'host',
            '10.0.0.1',
            '2026-07-16 10:00:00',
            None,
            'CPU',
            1,
            2,
            'UNKNOWN',
            '2026-07-16 10:00:00',
            1,
        ]
        with self.assertRaisesRegex(ValueError, 'Estado no permitido'):
            AlertRecord.from_clickhouse_row(row)

    def test_rejects_values_larger_than_oracle_columns(self):
        row = [
            ROW_ID,
            'h' * 256,
            '10.0.0.1',
            '2026-07-16 10:00:00',
            None,
            'CPU',
            1,
            2,
            'ACTIVE',
            '2026-07-16 10:00:00',
            1,
        ]
        with self.assertRaisesRegex(ValueError, 'hostname supera'):
            AlertRecord.from_clickhouse_row(row)


class RouterMetricRecordTest(unittest.TestCase):
    def test_maps_router_count_and_timestamp(self):
        record = RouterMetricRecord.from_clickhouse_row(
            (
                24,
                dt.datetime(2026, 7, 16, 18, 45),
            )
        )

        self.assertEqual(24, record.routers_unicos)
        self.assertEqual(
            '2026-07-16 18:45:00.000000 -05:00',
            record.fecha_medicion,
        )
