"""Pruebas de reservas reales con dos conexiones, usando SQLite como simulador Oracle.

No sustituyen la validación de DDL y permisos en Oracle. No llaman a Aivo.
"""
import datetime as dt
import json
import sqlite3
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from src.aivo_whatsapp.models import Notification, normalize_phone
from src.aivo_whatsapp.repository import OracleRepository, OracleLogError
from src.aivo_whatsapp.service import AivoError, AivoResponse
from src.aivo_whatsapp.workflow import run_batch


CONSTRAINTS = [
    ('PK_AIVO_WA_LOG', 'P', 'ENABLED', 'VALIDATED', None),
    ('UQ_AIVO_WA_EVENTO', 'U', 'ENABLED', 'VALIDATED', None),
    ('UQ_AIVO_WA_PRUEBA', 'U', 'ENABLED', 'VALIDATED', None),
    ('CK_AIVO_WA_DESTINO', 'C', 'ENABLED', 'VALIDATED', "NUMERO_DESTINO = '999876502'"),
]
COLUMNS = [
    ('PK_AIVO_WA_LOG', 'ID_ENVIO', 1),
    ('UQ_AIVO_WA_EVENTO', 'NUMERO_CLIENTE', 1),
    ('UQ_AIVO_WA_EVENTO', 'FECHA_INICIO_AVERIA', 2),
    ('UQ_AIVO_WA_EVENTO', 'PLANTILLA', 3),
    ('UQ_AIVO_WA_PRUEBA', 'PLANTILLA', 1),
    ('UQ_AIVO_WA_PRUEBA', 'NUMERO_DESTINO', 2),
]


class OracleSimulatorCursor:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.sqlite.cursor()
        self.result = None
        self.rowcount = 0

    def setinputsizes(self, **sizes):
        self.connection.bind_types.append(sizes)

    def execute(self, query, params=None, **kwargs):
        params = params or kwargs
        if 'FROM user_constraints' in query:
            self.result = self.connection.constraints if params['table_name'] == 'AIVO_WHATSAPP_LOG' else self.connection.guard_constraints
            return
        if 'FROM user_cons_columns' in query:
            self.result = self.connection.columns if params['table_name'] == 'AIVO_WHATSAPP_LOG' else self.connection.guard_columns
            return
        params = {name: value.isoformat(timespec='microseconds') if isinstance(value, dt.datetime) else value
                  for name, value in params.items()}
        try:
            self.cursor.execute(query.replace('SYSTIMESTAMP', 'CURRENT_TIMESTAMP'), params)
        except sqlite3.IntegrityError as error:
            code = 1 if 'UNIQUE constraint failed' in str(error) else 2290
            raise RuntimeError(SimpleNamespace(code=code)) from error
        self.rowcount = self.cursor.rowcount

    def fetchall(self):
        return self.result if self.result is not None else self.cursor.fetchall()

    def close(self):
        self.cursor.close()


class OracleSimulatorConnection:
    autocommit = False

    def __init__(self, path):
        self.sqlite = sqlite3.connect(path, timeout=15)
        self.constraints = list(CONSTRAINTS)
        self.columns = list(COLUMNS)
        self.guard_constraints = [('PK_AIVO_WA_GUARD', 'P', 'ENABLED', 'VALIDATED', None)]
        self.guard_columns = [('PK_AIVO_WA_GUARD', 'PLANTILLA', 1), ('PK_AIVO_WA_GUARD', 'NUMERO_DESTINO', 2)]
        self.bind_types = []
        self.commit_count = 0
        self.fail_commit = None

    def cursor(self):
        return OracleSimulatorCursor(self)

    def commit(self):
        self.commit_count += 1
        if self.commit_count == self.fail_commit:
            raise RuntimeError('simulated commit failure')
        self.sqlite.commit()

    def rollback(self):
        self.sqlite.rollback()

    def close(self):
        self.sqlite.close()


def source_row(index=1):
    return {
        'incidencia': f'INC-{index}',
        'fecha_inicio_averia': dt.datetime(2026, 10, 9, 15, 0, 0, 123456),
        'fecha_estimada_solucion': dt.datetime(2026, 10, 9, 20, 0),
        'fecha_solucion': dt.datetime(2026, 10, 9, 19, 0),
        'nro_documento': '12345678', 'nombre_cliente': 'Daniel Muñante',
        'numero_cliente': str(999000000 + index),
    }


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = str(Path(self.directory.name) / 'reservations.db')
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute('''
                CREATE TABLE AIVO_WHATSAPP_LOG (
                    id_envio TEXT PRIMARY KEY, plantilla TEXT NOT NULL,
                    incidencia TEXT, fecha_inicio_averia TEXT NOT NULL,
                    fecha_estimada_solucion TEXT, fecha_solucion TEXT, nro_documento TEXT,
                    nombre_cliente TEXT, numero_cliente TEXT NOT NULL,
                    numero_destino TEXT NOT NULL CHECK(numero_destino='999876502'),
                    estado TEXT, intentos INTEGER CHECK(intentos IN (0,1)),
                    solicitud_json TEXT, respuesta_json TEXT, error_detalle TEXT,
                    http_status INTEGER, fecha_actualizacion TEXT,
                    UNIQUE(numero_cliente, fecha_inicio_averia, plantilla),
                    UNIQUE(plantilla, numero_destino)
                )
            ''')
            connection.execute('''
                CREATE TABLE AIVO_WA_TEST_GUARD (
                    plantilla TEXT NOT NULL, numero_destino TEXT NOT NULL,
                    motivo TEXT NOT NULL, id_envio TEXT,
                    PRIMARY KEY(plantilla, numero_destino)
                )
            ''')
        self.connections = []
        self.repository = self.make_repository()
        self.client = Mock()
        self.client.authenticate.return_value = 'token'
        self.client.send_authenticated.return_value = AivoResponse(200, {'id': 'ok'}, '{"id":"ok"}')

    def tearDown(self):
        for connection in self.connections:
            connection.close()
        self.directory.cleanup()

    def make_repository(self):
        connection = OracleSimulatorConnection(self.path)
        self.connections.append(connection)
        repository = OracleRepository(connection, SimpleNamespace(DB_TYPE_CLOB='CLOB', DB_TYPE_TIMESTAMP='TIMESTAMP'))
        repository.fetch_candidates = Mock(return_value=[source_row()])
        return repository

    def states(self):
        with closing(sqlite3.connect(self.path)) as connection:
            return connection.execute('SELECT plantilla, estado, intentos FROM AIVO_WHATSAPP_LOG ORDER BY plantilla').fetchall()

    def test_many_customers_and_repeated_runs_send_only_once_per_template(self):
        self.repository.fetch_candidates.return_value = [source_row(index) for index in range(1, 30)]
        first = run_batch(self.repository, self.client)
        second = run_batch(self.repository, self.client)
        self.assertEqual(first['aceptados'], 2)
        self.assertEqual(first['bloqueados'], 56)
        self.assertEqual(second['aceptados'], 0)
        self.assertEqual(second['bloqueados'], 58)
        self.assertEqual(self.client.send_authenticated.call_count, 2)
        for request in self.client.send_authenticated.call_args_list:
            self.assertEqual(request.args[0]['to'], '999876502')
        self.assertEqual([row[1:] for row in self.states()], [('ACEPTADO', 1), ('ACEPTADO', 1)])

    def test_confirmed_previous_manual_messages_block_both_templates_without_any_post(self):
        with closing(sqlite3.connect(self.path)) as connection:
            for template in ('averia_diagnosticada', 'averia_solucionada'):
                connection.execute('''
                    INSERT INTO AIVO_WA_TEST_GUARD (plantilla, numero_destino, motivo)
                    VALUES (?, '999876502', 'Mensaje anterior confirmado por usuario')
                ''', (template,))
            connection.commit()
        first = run_batch(self.repository, self.client)
        second = run_batch(self.make_repository(), self.client)
        self.assertEqual(first['bloqueados'], 2)
        self.assertEqual(second['bloqueados'], 2)
        self.assertEqual(self.states(), [])
        self.client.authenticate.assert_not_called()
        self.client.send_authenticated.assert_not_called()

    def test_empty_tables_allow_first_attempt_and_new_connection_blocks_second(self):
        first = run_batch(self.repository, self.client)
        second = run_batch(self.make_repository(), self.client)
        self.assertEqual(first['aceptados'], 2)
        self.assertEqual(first['bloqueados'], 0)
        self.assertEqual(second['aceptados'], 0)
        self.assertEqual(second['bloqueados'], 2)
        self.assertEqual(self.client.send_authenticated.call_count, 2)
        with closing(sqlite3.connect(self.path)) as connection:
            guards = connection.execute('SELECT plantilla, id_envio FROM AIVO_WA_TEST_GUARD').fetchall()
        self.assertEqual(len(guards), 2)
        self.assertTrue(all(record_id for _, record_id in guards))

    def test_payload_hour_comes_from_estimated_solution_in_12_hour_format(self):
        run_batch(self.repository, self.client, 'averia_diagnosticada')
        parameters = self.client.send_authenticated.call_args.args[0]['template']['components'][0]['parameters']
        self.assertEqual([item['text'] for item in parameters], ['Daniel Muñante', '08:00', 'PM'])
        for hour, expected in ((0, ('12:00', 'AM')), (12, ('12:00', 'PM'))):
            row = source_row()
            row['fecha_estimada_solucion'] = row['fecha_estimada_solucion'].replace(hour=hour)
            values = Notification.from_row('averia_diagnosticada', row).payload()['template']['components'][0]['parameters']
            self.assertEqual(tuple(item['text'] for item in values[1:]), expected)

    def test_dispatch_checkpoint_is_visible_from_another_connection_before_post(self):
        def send(payload, token):
            self.assertEqual(self.states(), [('averia_diagnosticada', 'ENVIANDO', 1)])
            return AivoResponse(202, {'id': 'ok'}, '{"id":"ok"}')
        self.client.send_authenticated.side_effect = send
        run_batch(self.repository, self.client, 'averia_diagnosticada')
        self.assertEqual(self.states(), [('averia_diagnosticada', 'ACEPTADO', 1)])
        self.assertIn({'respuesta_json': 'CLOB'}, self.repository.connection.bind_types)
        self.assertEqual(self.repository.connection.bind_types[0]['fecha_inicio'], 'TIMESTAMP')

    def test_timeout_never_retries_after_restarting_process(self):
        self.client.send_authenticated.side_effect = AivoError('timeout')
        run_batch(self.repository, self.client, 'averia_diagnosticada')
        new_repository = self.make_repository()
        result = run_batch(new_repository, self.client, 'averia_diagnosticada')
        self.assertEqual(result['bloqueados'], 1)
        self.assertEqual(self.client.send_authenticated.call_count, 1)
        self.assertEqual(self.states(), [('averia_diagnosticada', 'INCIERTO', 1)])

    def test_http_failure_logs_response_but_never_retries(self):
        self.client.send_authenticated.side_effect = AivoError('HTTP 500', 500, '{"error":"fallo"}')
        run_batch(self.repository, self.client, 'averia_solucionada')
        run_batch(self.repository, self.client, 'averia_solucionada')
        self.assertEqual(self.client.send_authenticated.call_count, 1)
        self.assertEqual(self.states(), [('averia_solucionada', 'ERROR_HTTP', 1)])
        with closing(sqlite3.connect(self.path)) as connection:
            status, body = connection.execute('SELECT http_status, respuesta_json FROM AIVO_WHATSAPP_LOG').fetchone()
        self.assertEqual((status, json.loads(body)), (500, {'error': 'fallo'}))

    def test_authentication_failure_is_logged_and_blocks_future_attempts(self):
        self.client.authenticate.side_effect = AivoError('HTTP 401', 401)
        run_batch(self.repository, self.client, 'averia_solucionada')
        run_batch(self.repository, self.client, 'averia_solucionada')
        self.client.send_authenticated.assert_not_called()
        self.assertEqual(self.client.authenticate.call_count, 1)
        self.assertEqual(self.states(), [('averia_solucionada', 'ERROR_AUTH', 0)])

    def test_commit_failure_before_reservation_prevents_auth_and_send(self):
        self.repository.connection.fail_commit = 1
        with self.assertRaises(OracleLogError):
            run_batch(self.repository, self.client, 'averia_solucionada')
        self.client.authenticate.assert_not_called()
        self.client.send_authenticated.assert_not_called()

    def test_commit_failure_before_dispatch_prevents_send_and_later_retry(self):
        self.repository.connection.fail_commit = 2
        with self.assertRaises(OracleLogError):
            run_batch(self.repository, self.client, 'averia_solucionada')
        self.client.send_authenticated.assert_not_called()
        self.assertEqual(self.states(), [('averia_solucionada', 'RESERVADO', 0)])
        run_batch(self.make_repository(), self.client, 'averia_solucionada')
        self.client.send_authenticated.assert_not_called()

    def test_commit_failure_after_post_prevents_second_post(self):
        self.repository.connection.fail_commit = 3
        with self.assertRaises(OracleLogError):
            run_batch(self.repository, self.client, 'averia_solucionada')
        self.assertEqual(self.states(), [('averia_solucionada', 'ENVIANDO', 1)])
        run_batch(self.make_repository(), self.client, 'averia_solucionada')
        self.assertEqual(self.client.send_authenticated.call_count, 1)

    def test_interruption_during_post_leaves_reservation_blocked(self):
        self.client.send_authenticated.side_effect = KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            run_batch(self.repository, self.client, 'averia_solucionada')
        run_batch(self.make_repository(), self.client, 'averia_solucionada')
        self.assertEqual(self.client.send_authenticated.call_count, 1)
        self.assertEqual(self.states(), [('averia_solucionada', 'ENVIANDO', 1)])

    def test_parallel_processes_with_separate_connections_send_only_once(self):
        barrier = threading.Barrier(4)
        calls = []
        lock = threading.Lock()

        def worker(_):
            connection = OracleSimulatorConnection(self.path)
            try:
                repository = OracleRepository(connection, SimpleNamespace(DB_TYPE_CLOB='CLOB', DB_TYPE_TIMESTAMP='TIMESTAMP'))
                repository.fetch_candidates = Mock(return_value=[source_row()])
                client = Mock()
                client.authenticate.return_value = 'token'
                def send(payload, token):
                    with lock:
                        calls.append(payload['template']['name'])
                    return AivoResponse(200, {}, '{}')
                client.send_authenticated.side_effect = send
                barrier.wait(timeout=10)
                return run_batch(repository, client)
            finally:
                connection.close()
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(worker, range(4)))
        self.assertEqual(sorted(calls), ['averia_diagnosticada', 'averia_solucionada'])
        self.assertEqual(sum(result['aceptados'] for result in results), 2)

    def test_invalid_source_data_never_reserves_or_calls_aivo(self):
        rows = []
        for field in ('numero_cliente', 'fecha_inicio_averia', 'nombre_cliente', 'fecha_estimada_solucion'):
            row = source_row()
            row[field] = None
            rows.append(row)
        self.repository.fetch_candidates.return_value = rows
        result = run_batch(self.repository, self.client, 'averia_diagnosticada')
        self.assertEqual(result['invalidos'], 4)
        self.assertEqual(self.states(), [])
        self.client.authenticate.assert_not_called()

    def test_dry_run_does_not_reserve_or_call_aivo(self):
        result = run_batch(self.repository, None, dry_run=True)
        self.assertEqual(len(result['vista_previa']), 2)
        self.assertEqual(self.states(), [])

    def test_disabled_or_wrong_constraints_block_all_sends(self):
        for key in ('UQ_AIVO_WA_PRUEBA', 'UQ_AIVO_WA_EVENTO', 'CK_AIVO_WA_DESTINO'):
            self.repository.connection.constraints = [row for row in CONSTRAINTS if row[0] != key]
            with self.subTest(key=key), self.assertRaises(OracleLogError):
                run_batch(self.repository, self.client)
        self.repository.connection.constraints = list(CONSTRAINTS)
        self.repository.connection.columns = [row for row in COLUMNS if row[0] != 'UQ_AIVO_WA_EVENTO']
        with self.assertRaises(OracleLogError):
            run_batch(self.repository, self.client)
        self.client.authenticate.assert_not_called()

    def test_phone_normalization_avoids_different_keys_for_local_and_country_prefix(self):
        self.assertEqual(normalize_phone('999876502'), normalize_phone('+51 999 876 502'))

    def test_missing_guard_primary_key_blocks_all_sends(self):
        self.repository.connection.guard_constraints = []
        with self.assertRaises(OracleLogError):
            run_batch(self.repository, self.client)
        self.client.authenticate.assert_not_called()
        self.client.send_authenticated.assert_not_called()

    def test_unique_event_key_ignores_incidence_and_estimated_time_changes(self):
        notification = Notification.from_row('averia_diagnosticada', source_row())
        first = self.repository.reserve(notification, notification.payload())
        changed = source_row()
        changed['incidencia'] = 'INC-OTRA'
        changed['fecha_estimada_solucion'] = dt.datetime(2026, 10, 9, 22)
        changed['numero_cliente'] = '+51 ' + changed['numero_cliente']
        second_notification = Notification.from_row('averia_diagnosticada', changed)
        self.assertIsNotNone(first)
        self.assertIsNone(self.repository.reserve(second_notification, second_notification.payload()))
        self.assertEqual(len(self.states()), 1)


if __name__ == '__main__':
    unittest.main()
