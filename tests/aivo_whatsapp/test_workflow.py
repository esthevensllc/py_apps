"""Pruebas de reservas reales con dos conexiones, usando SQLite como simulador Oracle.

No sustituyen la validación de DDL y permisos en Oracle. No llaman a Aivo.
"""
import datetime as dt
import json
import re
import sqlite3
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing, nullcontext
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from src.aivo_whatsapp.models import Notification, normalize_phone
from src.aivo_whatsapp.repository import OracleRepository, OracleTestRepository, OracleLogError
from src.aivo_whatsapp.service import AivoClient, AivoSettings, AivoError, AivoResponse
from src.aivo_whatsapp.workflow import run_batch
from token_support import make_manager
from src.aivo_whatsapp.token_cache import TokenGrant


CONSTRAINTS = [
    ('PK_AIVO_WA_LOG', 'P', 'ENABLED', 'VALIDATED', None),
    ('UQ_AIVO_WA_EVENTO', 'U', 'ENABLED', 'VALIDATED', None),
    ('CK_AIVO_WA_MODO', 'C', 'ENABLED', 'VALIDATED', "MODO IN ('PRUEBA', 'PRODUCCION')"),
]
COLUMNS = [
    ('PK_AIVO_WA_LOG', 'ID_ENVIO', 1),
    ('UQ_AIVO_WA_EVENTO', 'MODO', 1),
    ('UQ_AIVO_WA_EVENTO', 'NUMERO_CLIENTE', 2),
    ('UQ_AIVO_WA_EVENTO', 'FECHA_INICIO_AVERIA', 3),
    ('UQ_AIVO_WA_EVENTO', 'PLANTILLA', 4),
]
TEST_CONSTRAINTS = [
    ('PK_AIVO_WA_TLOG', 'P', 'ENABLED', 'VALIDATED', None),
    ('UQ_AIVO_WA_TEST', 'U', 'ENABLED', 'VALIDATED', None),
    ('CK_AIVO_WA_TMODE', 'C', 'ENABLED', 'VALIDATED', "MODO = 'PRUEBA'"),
]
TEST_COLUMNS = [
    ('PK_AIVO_WA_TLOG', 'ID_ENVIO', 1),
    ('UQ_AIVO_WA_TEST', 'ID_PRUEBA', 1),
    ('UQ_AIVO_WA_TEST', 'PLANTILLA', 2),
    ('UQ_AIVO_WA_TEST', 'DESTINO_CLAVE', 3),
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
            self.result = TEST_CONSTRAINTS if params['table_name'] == 'AIVO_WHATSAPP_TEST_LOG' else self.connection.constraints
            return
        if 'FROM user_cons_columns' in query:
            self.result = TEST_COLUMNS if params['table_name'] == 'AIVO_WHATSAPP_TEST_LOG' else self.connection.columns
            return
        params = {name: value.isoformat(timespec='microseconds') if isinstance(value, dt.datetime) else value
                  for name, value in params.items()}
        if 'CLIATC.CI_FIJA_AUDIO_AVERIA' in query:
            # SQLite ignora binds sobrantes; Oracle los rechaza con ORA-01036.
            # Verificarlos antes de adaptar el SQL para no ocultar esta regresión.
            if set(params) != set(re.findall(r':([A-Za-z_][A-Za-z0-9_]*)', query)):
                raise RuntimeError(SimpleNamespace(code=1036))
            # Sustituir SOLO el origen remoto y tipos Oracle por un origen local.
            # Se ejecuta el filtro real NOT EXISTS y su límite sobre reservas reales.
            query = re.sub(r'\(SELECT DISTINCT.*?\) src',
                           '(SELECT * FROM source_averias ORDER BY fecha_inicio_averia, incidencia) src',
                           query, flags=re.DOTALL)
            query = query.replace('CAST(src.fecha_inicio_averia AS TIMESTAMP)', 'src.fecha_inicio_averia')
            query = query.replace('AND ROWNUM <= :limite', 'LIMIT :limite')
            query = query.replace('WHERE ROWNUM <= :limite', 'LIMIT :limite')
        try:
            self.cursor.execute(query.replace('SYSTIMESTAMP', 'CURRENT_TIMESTAMP'), params)
        except sqlite3.IntegrityError as error:
            code = 1 if 'UNIQUE constraint failed' in str(error) else 2290
            raise RuntimeError(SimpleNamespace(code=code)) from error
        self.rowcount = self.cursor.rowcount

    def fetchall(self):
        return self.result if self.result is not None else self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    @property
    def description(self):
        return self.cursor.description

    def fetchmany(self, size):
        columns = [entry[0] for entry in self.cursor.description]
        return [tuple(dt.datetime.fromisoformat(value) if value and column.startswith('fecha_') else value
                      for column, value in zip(columns, row)) for row in self.cursor.fetchmany(size)]

    def close(self):
        self.cursor.close()


class OracleSimulatorConnection:
    autocommit = False

    def __init__(self, path):
        self.sqlite = sqlite3.connect(path, timeout=15)
        self.sqlite.create_function('REGEXP_REPLACE', 3, lambda value, pattern, replacement: re.sub(pattern, replacement, str(value)))
        self.constraints = list(CONSTRAINTS)
        self.columns = list(COLUMNS)
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
                    id_envio TEXT PRIMARY KEY, modo TEXT DEFAULT 'PRODUCCION' NOT NULL, plantilla TEXT NOT NULL,
                    incidencia TEXT, fecha_inicio_averia TEXT NOT NULL,
                    fecha_estimada_solucion TEXT, fecha_solucion TEXT, nro_documento TEXT,
                    nombre_cliente TEXT, numero_cliente TEXT NOT NULL,
                    numero_destino TEXT NOT NULL,
                    estado TEXT, intentos INTEGER CHECK(intentos IN (0,1)),
                    solicitud_json TEXT, respuesta_json TEXT, error_detalle TEXT,
                    http_status INTEGER, fecha_actualizacion TEXT,
                    UNIQUE(modo, numero_cliente, fecha_inicio_averia, plantilla)
                )
            ''')
            connection.execute('''CREATE TABLE AIVO_WHATSAPP_TEST_LOG (
                id_envio TEXT PRIMARY KEY, id_prueba TEXT NOT NULL, destino_clave TEXT NOT NULL,
                modo TEXT CHECK(modo='PRUEBA') NOT NULL, plantilla TEXT NOT NULL,
                incidencia TEXT, fecha_inicio_averia TEXT, fecha_estimada_solucion TEXT,
                fecha_solucion TEXT, nro_documento TEXT, nombre_cliente TEXT,
                numero_cliente TEXT, numero_destino TEXT, estado TEXT,
                intentos INTEGER CHECK(intentos IN (0,1)), http_status INTEGER,
                solicitud_json TEXT, respuesta_json TEXT, error_detalle TEXT,
                fecha_actualizacion TEXT,
                UNIQUE(id_prueba, plantilla, destino_clave)
            )''')
        self.connections = []
        self.repository = self.make_repository()
        self.client = Mock()
        self.client.account_session.side_effect = nullcontext
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

    def test_many_customers_receive_each_template_once_and_repeated_runs_are_blocked(self):
        self.repository.fetch_candidates.return_value = [source_row(index) for index in range(1, 30)]
        first = run_batch(self.repository, self.client)
        second = run_batch(self.repository, self.client)
        self.assertEqual(first['aceptados'], 58)
        self.assertEqual(first['bloqueados'], 0)
        self.assertEqual(second['aceptados'], 0)
        self.assertEqual(second['bloqueados'], 58)
        self.assertEqual(self.client.send_authenticated.call_count, 58)
        destinations = [request.args[0]['to'] for request in self.client.send_authenticated.call_args_list]
        self.assertEqual(set(destinations), {str(999000000 + index) for index in range(1, 30)})
        self.assertNotIn('999876502', destinations)
        self.assertEqual({row[1:] for row in self.states()}, {('ACEPTADO', 1)})

    def test_trial_logs_do_not_block_real_customers_but_production_logs_do(self):
        with closing(sqlite3.connect(self.path)) as connection:
            for template in ('averia_diagnosticada', 'averia_solucionada'):
                connection.execute('''
                    INSERT INTO AIVO_WHATSAPP_LOG
                        (id_envio, modo, plantilla, numero_cliente, numero_destino, fecha_inicio_averia, estado, intentos)
                    VALUES (?, 'PRUEBA', ?, ?, '999876502', ?, 'ACEPTADO', 1)
                ''', ('trial-' + template, template, normalize_phone(source_row()['numero_cliente']),
                      source_row()['fecha_inicio_averia'].isoformat(timespec='microseconds')))
            connection.commit()
        first = run_batch(self.repository, self.client)
        second = run_batch(self.make_repository(), self.client)
        self.assertEqual(first['aceptados'], 2)
        self.assertEqual(second['bloqueados'], 2)
        self.assertEqual(len(self.states()), 4)
        self.assertEqual(self.client.send_authenticated.call_count, 2)

    def test_empty_tables_allow_first_attempt_and_new_connection_blocks_second(self):
        first = run_batch(self.repository, self.client)
        second = run_batch(self.make_repository(), self.client)
        self.assertEqual(first['aceptados'], 2)
        self.assertEqual(first['bloqueados'], 0)
        self.assertEqual(second['aceptados'], 0)
        self.assertEqual(second['bloqueados'], 2)
        self.assertEqual(self.client.send_authenticated.call_count, 2)
        self.assertEqual(len(self.states()), 2)

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
        self.assertEqual(self.repository.connection.bind_types[0]['fecha_inicio_averia'], 'TIMESTAMP')

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

    def test_authentication_failure_without_send_can_request_auth_again_next_run(self):
        self.client.authenticate.side_effect = AivoError('HTTP 401', 401)
        run_batch(self.repository, self.client, 'averia_solucionada')
        run_batch(self.repository, self.client, 'averia_solucionada')
        self.client.send_authenticated.assert_not_called()
        self.assertEqual(self.client.authenticate.call_count, 2)
        self.assertEqual(self.states(), [('averia_solucionada', 'ERROR_AUTH', 0)])

    def test_failed_auth_record_is_recovered_and_sent_once_when_auth_works(self):
        self.client.authenticate.side_effect = [AivoError('token ausente'), 'token']
        first = run_batch(self.repository, self.client, 'averia_solucionada')
        second = run_batch(self.make_repository(), self.client, 'averia_solucionada')
        third = run_batch(self.make_repository(), self.client, 'averia_solucionada')
        self.assertEqual((first['errores'], second['aceptados'], third['bloqueados']), (1, 1, 1))
        self.assertEqual(self.client.send_authenticated.call_count, 1)
        self.assertEqual(self.states(), [('averia_solucionada', 'ACEPTADO', 1)])

    def test_persistent_auth_failure_stops_batch_before_reserving_other_customers(self):
        self.repository.fetch_candidates.return_value = [source_row(index) for index in range(1, 20)]
        self.client.authenticate.side_effect = AivoError('token ausente')
        result = run_batch(self.repository, self.client)
        self.assertEqual(result['errores'], 1)
        self.assertEqual(self.client.authenticate.call_count, 1)
        self.assertEqual(len(self.states()), 1)
        self.client.send_authenticated.assert_not_called()

    def test_account_block_during_send_stops_entire_batch_and_emits_alert(self):
        self.repository.fetch_candidates.return_value = [source_row(index) for index in range(1, 20)]
        self.client.send_authenticated.side_effect = AivoError(
            'ALERTA AIVO: UserBlockedException', 200, auth_failure=True, account_blocked=True,
        )
        with self.assertLogs('src.aivo_whatsapp.workflow', level='CRITICAL') as messages:
            result = run_batch(self.repository, self.client)
        self.assertEqual(result['errores'], 1)
        self.assertEqual(self.client.send_authenticated.call_count, 1)
        self.assertEqual(len(self.states()), 1)
        self.assertIn('UserBlockedException', messages.output[0])

    def test_functional_error_with_http_200_is_logged_and_never_resent(self):
        self.client.send_authenticated.side_effect = AivoError(
            'error funcional', 200, '{"exception":"InvalidTemplate"}', functional_error=True,
        )
        first = run_batch(self.repository, self.client, 'averia_solucionada')
        second = run_batch(self.make_repository(), self.client, 'averia_solucionada')
        self.assertEqual((first['errores'], second['bloqueados']), (1, 1))
        self.assertEqual(self.states(), [('averia_solucionada', 'ERROR_HTTP', 1)])
        self.assertEqual(self.client.send_authenticated.call_count, 1)

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_many_customers_share_one_login_across_new_batch_clients(self, post):
        def answer(data):
            result = Mock(status_code=200, content=b'{}', text=json.dumps(data))
            result.json.return_value = data
            return result
        post.side_effect = lambda url, **kwargs: answer(
            {'Authorization': 'Bearer shared-token'} if url.endswith('/auth') else {'id': 'message'}
        )
        manager = make_manager()
        self.repository.fetch_candidates.return_value = [source_row(index) for index in range(1, 20)]
        client = AivoClient(AivoSettings('user', 'password', 'x-token'), manager)
        first = run_batch(self.repository, client)
        manager.store.now += 900
        new_repository = self.make_repository()
        new_repository.fetch_candidates.return_value = [source_row(20)]
        new_client = AivoClient(client.settings, make_manager(manager.store))
        second = run_batch(new_repository, new_client)
        self.assertEqual((first['aceptados'], second['aceptados']), (38, 2))
        self.assertEqual(sum(call.args[0].endswith('/auth') for call in post.call_args_list), 1)

    def test_auth_failure_after_dispatch_is_not_reclaimed(self):
        self.client.send_authenticated.side_effect = AivoError('falló renovación', auth_failure=True)
        run_batch(self.repository, self.client, 'averia_solucionada')
        result = run_batch(self.make_repository(), self.client, 'averia_solucionada')
        self.assertEqual(result['bloqueados'], 1)
        self.assertEqual(self.client.send_authenticated.call_count, 1)
        self.assertEqual(self.states(), [('averia_solucionada', 'ERROR_AUTH', 1)])

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_401_refresh_keeps_one_reservation_and_repeat_run_does_not_send_again(self, post):
        def answer(data, status=200):
            result = Mock(status_code=status, content=b'{}', text=json.dumps(data))
            result.json.return_value = data
            return result
        manager = make_manager()
        manager.get(lambda: TokenGrant('anterior'))
        manager.store.now += 3600
        post.side_effect = [answer({}, 401), answer({'Authorization': 'Bearer nuevo'}), answer({'id': 'mensaje'})]
        client = AivoClient(AivoSettings('usuario', 'clave', 'x-token'), manager)
        first = run_batch(self.repository, client, 'averia_solucionada')
        second = run_batch(self.make_repository(), client, 'averia_solucionada')
        self.assertEqual((first['aceptados'], second['bloqueados']), (1, 1))
        self.assertEqual(post.call_count, 3)
        self.assertEqual(self.states(), [('averia_solucionada', 'ACEPTADO', 1)])

    def test_concurrent_recovery_of_auth_failure_still_sends_only_one_message(self):
        self.client.authenticate.side_effect = AivoError('token ausente')
        run_batch(self.repository, self.client, 'averia_solucionada')
        barrier = threading.Barrier(4)
        calls = []
        lock = threading.Lock()
        def worker(_):
            connection = OracleSimulatorConnection(self.path)
            try:
                repository = OracleRepository(connection, SimpleNamespace(DB_TYPE_CLOB='CLOB', DB_TYPE_TIMESTAMP='TIMESTAMP'))
                repository.fetch_candidates = Mock(return_value=[source_row()])
                client = Mock()
                client.account_session.side_effect = nullcontext
                client.authenticate.return_value = 'token'
                def send(payload, token):
                    with lock:
                        calls.append(payload['to'])
                    return AivoResponse(200, {}, '{}')
                client.send_authenticated.side_effect = send
                barrier.wait(timeout=10)
                return run_batch(repository, client, 'averia_solucionada')
            finally:
                connection.close()
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(worker, range(4)))
        self.assertEqual(calls, ['999000001'])

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
                client.account_session.side_effect = nullcontext
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
        for key in ('UQ_AIVO_WA_EVENTO', 'CK_AIVO_WA_MODO'):
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

    def test_unmigrated_trial_constraints_block_production(self):
        self.repository.connection.constraints.append(('CK_AIVO_WA_DESTINO', 'C', 'ENABLED', 'VALIDATED', 'old'))
        with self.assertRaises(OracleLogError):
            run_batch(self.repository, self.client)
        self.client.authenticate.assert_not_called()
        self.client.send_authenticated.assert_not_called()

    def test_modified_destination_is_rejected_before_reservation(self):
        notification = Notification.from_row('averia_diagnosticada', source_row())
        payload = notification.payload()
        payload['to'] = '999876502'
        with self.assertRaises(OracleLogError):
            self.repository.reserve(notification, payload)
        self.assertEqual(self.states(), [])

    def test_query_excludes_reserved_events_before_limit_so_next_batch_advances(self):
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute('''CREATE TABLE source_averias (
                incidencia TEXT, fecha_inicio_averia TEXT, fecha_estimada_solucion TEXT,
                fecha_solucion TEXT, nro_documento TEXT, nombre_cliente TEXT, numero_cliente TEXT
            )''')
            for index in (1, 2):
                row = source_row(index)
                connection.execute('INSERT INTO source_averias VALUES (?, ?, ?, ?, ?, ?, ?)', tuple(
                    value.isoformat(timespec='microseconds') if isinstance(value, dt.datetime) else value
                    for value in row.values()
                ))
            connection.commit()
        # Usar el método real, en lugar de la fuente simulada habitual.
        del self.repository.fetch_candidates
        first = run_batch(self.repository, self.client, 'averia_solucionada', limit=1)
        second = run_batch(self.repository, self.client, 'averia_solucionada', limit=1)
        third = run_batch(self.repository, self.client, 'averia_solucionada', limit=1)
        self.assertEqual((first['aceptados'], second['aceptados'], third['candidatos']), (1, 1, 0))
        self.assertEqual([call.args[0]['to'] for call in self.client.send_authenticated.call_args_list], ['999000001', '999000002'])

    def test_real_queries_in_production_and_manual_preview_have_no_extra_oracle_binds(self):
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute('''CREATE TABLE source_averias (
                incidencia TEXT, fecha_inicio_averia TEXT, fecha_estimada_solucion TEXT,
                fecha_solucion TEXT, nro_documento TEXT, nombre_cliente TEXT, numero_cliente TEXT
            )''')
            connection.execute('INSERT INTO source_averias VALUES (?, ?, ?, ?, ?, ?, ?)', tuple(
                value.isoformat(timespec='microseconds') if isinstance(value, dt.datetime) else value
                for value in source_row().values()
            ))
            connection.commit()
        del self.repository.fetch_candidates
        test_repository = self.make_test_repository()
        del test_repository.fetch_candidates
        # Se usan las consultas reales y el simulador rechaza cualquier bind
        # sobrante antes de sustituir la fuente Oracle por la tabla SQLite.
        production = run_batch(self.repository, None, limit=1, dry_run=True)
        manual = run_batch(test_repository, None, limit=1, dry_run=True)
        self.assertEqual(len(production['vista_previa']), 2)
        self.assertEqual(len(manual['vista_previa']), 2)
        self.assertEqual({item['to'] for item in production['vista_previa']}, {'999000001'})
        self.assertEqual({item['to'] for item in manual['vista_previa']}, {'999876502'})
        self.assertEqual(self.states(), [])

    def test_query_includes_zero_attempt_auth_failures_until_recovered(self):
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute('''CREATE TABLE source_averias (
                incidencia TEXT, fecha_inicio_averia TEXT, fecha_estimada_solucion TEXT,
                fecha_solucion TEXT, nro_documento TEXT, nombre_cliente TEXT, numero_cliente TEXT
            )''')
            connection.execute('INSERT INTO source_averias VALUES (?, ?, ?, ?, ?, ?, ?)', tuple(
                value.isoformat(timespec='microseconds') if isinstance(value, dt.datetime) else value
                for value in source_row().values()
            ))
            connection.commit()
        del self.repository.fetch_candidates
        self.client.authenticate.side_effect = [AivoError('token ausente'), 'token']
        first = run_batch(self.repository, self.client, 'averia_solucionada', limit=1)
        second = run_batch(self.repository, self.client, 'averia_solucionada', limit=1)
        third = run_batch(self.repository, self.client, 'averia_solucionada', limit=1)
        self.assertEqual((first['errores'], second['aceptados'], third['candidatos']), (1, 1, 0))
        self.assertEqual(self.client.send_authenticated.call_count, 1)

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

    def make_test_repository(self, test_id='prueba_02', test_to='999876502'):
        base = self.make_repository()
        repository = OracleTestRepository(base.connection, base.driver, test_to, test_id)
        repository.fetch_candidates = Mock(return_value=[source_row(index) for index in range(1, 20)])
        return repository

    def test_manual_override_sends_two_only_to_test_phone_and_second_run_sends_none(self):
        first = run_batch(self.make_test_repository(), self.client)
        second = run_batch(self.make_test_repository(), self.client)
        self.assertEqual(first['aceptados'], 2)
        self.assertEqual(second['aceptados'], 0)
        self.assertEqual(self.client.send_authenticated.call_count, 2)
        self.assertEqual({call.args[0]['to'] for call in self.client.send_authenticated.call_args_list}, {'999876502'})
        self.assertEqual(self.states(), [])
        with closing(sqlite3.connect(self.path)) as connection:
            modes = connection.execute('SELECT modo, estado, intentos FROM AIVO_WHATSAPP_TEST_LOG').fetchall()
        self.assertEqual(modes, [('PRUEBA', 'ACEPTADO', 1), ('PRUEBA', 'ACEPTADO', 1)])

    def test_test_destination_normalization_blocks_repeated_round_with_country_prefix(self):
        run_batch(self.make_test_repository(), self.client)
        result = run_batch(self.make_test_repository(test_to='+51 999 876 502'), self.client)
        self.assertEqual(result['aceptados'], 0)
        self.assertEqual(self.client.send_authenticated.call_count, 2)

    def test_new_test_identifier_allows_new_deliberate_round_without_clearing_logs(self):
        run_batch(self.make_test_repository(), self.client)
        result = run_batch(self.make_test_repository(test_id='prueba_03'), self.client)
        self.assertEqual(result['aceptados'], 2)
        self.assertEqual(self.client.send_authenticated.call_count, 4)

    def test_test_timeout_remains_blocked_on_next_run(self):
        self.client.send_authenticated.side_effect = AivoError('timeout')
        run_batch(self.make_test_repository(), self.client, 'averia_diagnosticada')
        run_batch(self.make_test_repository(), self.client, 'averia_diagnosticada')
        self.assertEqual(self.client.send_authenticated.call_count, 1)

    def test_testing_a_customer_does_not_block_later_production_for_that_customer(self):
        run_batch(self.make_test_repository(), self.client)
        result = run_batch(self.repository, self.client)
        self.assertEqual(result['aceptados'], 2)
        self.assertEqual(self.client.send_authenticated.call_count, 4)

    def test_manual_round_can_recover_auth_failure_without_creating_duplicate_messages(self):
        self.client.authenticate.side_effect = [AivoError('token ausente'), 'token', 'token']
        first = run_batch(self.make_test_repository(), self.client)
        second = run_batch(self.make_test_repository(), self.client)
        third = run_batch(self.make_test_repository(), self.client)
        self.assertEqual((first['errores'], second['aceptados'], third['aceptados']), (1, 2, 0))
        self.assertEqual(self.client.send_authenticated.call_count, 2)

    def test_test_id_is_validated_and_cannot_alter_sql(self):
        for test_id in ('', "x'; DROP TABLE log", 'a' * 65):
            with self.subTest(test_id=test_id), self.assertRaises(ValueError):
                self.make_test_repository(test_id=test_id)

    def test_parallel_manual_tests_with_same_identifier_send_only_two_messages(self):
        barrier = threading.Barrier(4)
        sent = []
        lock = threading.Lock()
        def worker(_):
            connection = OracleSimulatorConnection(self.path)
            try:
                repository = OracleTestRepository(
                    connection, SimpleNamespace(DB_TYPE_CLOB='CLOB', DB_TYPE_TIMESTAMP='TIMESTAMP'),
                    '999876502', 'prueba_paralela',
                )
                repository.fetch_candidates = Mock(return_value=[source_row()])
                client = Mock()
                client.account_session.side_effect = nullcontext
                client.authenticate.return_value = 'token'
                def send(payload, token):
                    with lock:
                        sent.append((payload['template']['name'], payload['to']))
                    return AivoResponse(200, {}, '{}')
                client.send_authenticated.side_effect = send
                barrier.wait(timeout=10)
                return run_batch(repository, client)
            finally:
                connection.close()
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(worker, range(4)))
        self.assertEqual(sorted(sent), [('averia_diagnosticada', '999876502'), ('averia_solucionada', '999876502')])
        self.assertEqual(sum(item['aceptados'] for item in results), 2)


if __name__ == '__main__':
    unittest.main()
