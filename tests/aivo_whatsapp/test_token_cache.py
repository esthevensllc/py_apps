"""Persistencia del almacén Oracle con SQL adaptado a SQLite; sin llamadas reales.

SQLite no reproduce bloqueos de fila Oracle. La exclusión de AIVO_AUTH_GUARD
se simula con locks por cuenta y conexión; debe validarse además en Oracle.
"""
import json
import sqlite3
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from cryptography.fernet import Fernet

from src.aivo_whatsapp.service import AivoClient, AivoError, AivoSettings
from src.aivo_whatsapp.token_cache import OracleTokenStore, TokenCacheError, TokenCoordinator, TokenGrant
from token_support import KEY, make_manager


def answer(data, status=200):
    result = Mock(status_code=status, content=b'{}', text=json.dumps(data))
    result.json.return_value = data
    return result


class Cursor:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.db.cursor()

    def setinputsizes(self, **kwargs):
        pass

    def execute(self, query, params=None, **kwargs):
        params = params or kwargs
        if 'SYS_EXTRACT_UTC' in query:
            self.cursor.execute('SELECT ?', (self.connection.fixture.now,))
            return
        if 'AIVO_AUTH_GUARD' in query and 'FOR UPDATE NOWAIT' in query:
            lock = self.connection.fixture.guards[params['account_key']]
            if self.connection.held is not lock and not lock.acquire(blocking=False):
                raise Exception(SimpleNamespace(code=54))
            self.connection.held = lock
        elif 'FOR UPDATE WAIT 5' in query:
            self.connection.db.execute('BEGIN IMMEDIATE')
        query = query.replace(' FOR UPDATE WAIT 5', '').replace(' FOR UPDATE NOWAIT', '')
        try:
            self.cursor.execute(query, params)
        except sqlite3.IntegrityError as error:
            raise Exception(SimpleNamespace(code=1)) from error

    def fetchone(self):
        return self.cursor.fetchone()

    @property
    def rowcount(self):
        return self.cursor.rowcount

    def close(self):
        self.cursor.close()


class Connection:
    autocommit = False

    def __init__(self, fixture):
        self.fixture = fixture
        self.db = sqlite3.connect(fixture.path, timeout=10)
        self.held = None

    def cursor(self):
        return Cursor(self)

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()
        if self.held:
            self.held.release()
            self.held = None

    def close(self):
        self.rollback()
        self.db.close()


class PersistentCacheTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = str(Path(self.directory.name) / 'auth.db')
        self.now = 1_800_000_000
        self.guards = {'account': threading.Lock(), 'other': threading.Lock()}
        with closing(sqlite3.connect(self.path)) as connection, connection:
            # Mismos campos y restricciones relevantes que el DDL distribuido.
            connection.execute('CREATE TABLE AIVO_AUTH_GUARD (account_key TEXT PRIMARY KEY)')
            connection.executemany('INSERT INTO AIVO_AUTH_GUARD VALUES (?)', [('account',), ('other',)])
            connection.execute('''CREATE TABLE AIVO_AUTH_CACHE (
                account_key TEXT PRIMARY KEY, token_encrypted TEXT,
                generated_at REAL, refresh_at REAL, expires_at REAL,
                last_auth_at REAL, next_auth_at REAL, blocked INTEGER DEFAULT 0 NOT NULL CHECK(blocked IN (0,1)),
                last_error_code TEXT, lock_owner TEXT)''')

    def factory(self):
        return Connection(self), SimpleNamespace(DB_TYPE_CLOB='CLOB')

    def manager(self, key=KEY, account='account'):
        return TokenCoordinator(OracleTokenStore(self.factory, account), key)

    def state(self):
        with closing(sqlite3.connect(self.path)) as connection:
            connection.row_factory = sqlite3.Row
            return dict(connection.execute('SELECT * FROM AIVO_AUTH_CACHE WHERE account_key=?', ('account',)).fetchone())

    def test_new_workers_reuse_encrypted_token_and_renew_at_nine_hours(self):
        issuer = Mock(side_effect=[TokenGrant('sensitive-bearer-1'), TokenGrant('sensitive-bearer-2')])
        start = self.now
        for minutes in range(0, 601, 15):
            self.now = start + minutes * 60
            result = self.manager().get(issuer)
            self.assertEqual(result, 'sensitive-bearer-1' if minutes < 540 else 'sensitive-bearer-2')
        self.assertEqual(issuer.call_count, 2)
        state = self.state()
        self.assertNotIn('sensitive-bearer', state['token_encrypted'])
        self.assertEqual(state['generated_at'], start + 9 * 3600)
        self.assertEqual(state['expires_at'], start + 19 * 3600)
        self.assertIsNone(state['lock_owner'])
        self.assertEqual(Fernet(KEY).decrypt(state['token_encrypted'].encode()), b'sensitive-bearer-2')

    def test_jwt_expiration_shortens_refresh_time(self):
        issuer = Mock(side_effect=lambda: TokenGrant('short-token', self.now + 3600))
        self.manager().get(issuer)
        self.assertEqual(self.state()['refresh_at'], self.now + 3300)
        self.now += 3300
        self.manager().get(issuer)
        self.assertEqual(issuer.call_count, 2)

    def test_wrong_encryption_key_fails_without_another_login(self):
        issuer = Mock(return_value=TokenGrant('private-token'))
        self.manager().get(issuer)
        with self.assertRaisesRegex(TokenCacheError, 'descifrar'):
            self.manager(key=Fernet.generate_key()).get(issuer)
        self.assertEqual(issuer.call_count, 1)

    def test_parallel_workers_never_authenticate_simultaneously(self):
        barrier = threading.Barrier(6)
        issuer = Mock(return_value=TokenGrant('shared-token'))
        def worker(_):
            barrier.wait(timeout=10)
            try:
                return self.manager().get(issuer)
            except TokenCacheError:
                return 'busy'
        with ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(worker, range(6)))
        self.assertIn('shared-token', results)
        self.assertEqual(issuer.call_count, 1)

    def test_guard_remains_exclusive_during_long_query_or_http_wait(self):
        first = self.manager()
        with first.session():
            self.now += 121
            with self.assertRaisesRegex(TokenCacheError, 'exclusión'):
                with self.manager().session():
                    self.fail('La segunda ejecución no debe entrar')
            first.touch()  # Una consulta lenta no libera el bloqueo real ni invalida al propietario.
        with self.manager().session():
            pass

    def test_auth_timeout_persists_cooldown_across_restarts(self):
        issuer = Mock(side_effect=AivoError('timeout'))
        with self.assertRaises(AivoError):
            self.manager().get(issuer)
        self.now += 600
        with self.assertRaisesRegex(TokenCacheError, 'espera de seguridad'):
            self.manager().get(issuer)
        self.assertEqual(issuer.call_count, 1)
        self.now += 300
        issuer.side_effect = None
        issuer.return_value = TokenGrant('recovered')
        self.assertEqual(self.manager().get(issuer), 'recovered')
        self.assertEqual(issuer.call_count, 2)

    def test_process_interrupted_after_auth_reservation_preserves_cooldown(self):
        with self.manager().session() as manager:
            manager.store.begin_auth(manager.owner, 900)
        issuer = Mock(return_value=TokenGrant('unused'))
        with self.assertRaises(TokenCacheError):
            self.manager().get(issuer)
        issuer.assert_not_called()

    def test_blocked_account_persists_until_explicit_operator_intervention(self):
        issuer = Mock(side_effect=AivoError('ALERTA', account_blocked=True, error_code='UserBlockedException'))
        with self.assertRaises(AivoError):
            self.manager().get(issuer)
        self.now += 20 * 3600
        with self.assertRaises(TokenCacheError) as raised:
            self.manager().get(issuer)
        self.assertTrue(raised.exception.account_blocked)
        self.assertEqual(issuer.call_count, 1)
        self.assertEqual(self.state()['last_error_code'], 'UserBlockedException')

    def test_newer_shared_token_is_reused_after_an_old_401(self):
        issuer = Mock(return_value=TokenGrant('new-token'))
        self.manager().get(issuer)
        self.assertEqual(self.manager().get(issuer, rejected_token='old-token'), 'new-token')
        self.assertEqual(issuer.call_count, 1)

    def test_rejected_just_generated_token_does_not_trigger_another_login(self):
        issuer = Mock(return_value=TokenGrant('bad-token'))
        self.manager().get(issuer)
        with self.assertRaisesRegex(TokenCacheError, 'espera de seguridad'):
            self.manager().get(issuer, rejected_token='bad-token')
        self.assertEqual(issuer.call_count, 1)
        self.assertIsNone(self.state()['token_encrypted'])

    def test_distinct_accounts_do_not_share_token(self):
        first, second = Mock(return_value=TokenGrant('first')), Mock(return_value=TokenGrant('second'))
        self.manager().get(first)
        self.assertEqual(self.manager(account='other').get(second), 'second')
        self.assertEqual(self.manager().get(first), 'first')

    def test_status_exposes_no_token_or_ciphertext(self):
        self.manager().get(lambda: TokenGrant('private-bearer'))
        status = self.manager().status()
        self.assertIsNotNone(status['generated_at'])
        self.assertNotIn('token', json.dumps(status))
        self.assertNotIn('private-bearer', json.dumps(status))

    def test_missing_tables_fail_before_any_gateway_call(self):
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute('DROP TABLE AIVO_AUTH_GUARD')
        issuer = Mock()
        with self.assertRaises(TokenCacheError):
            self.manager().get(issuer)
        issuer.assert_not_called()

    def test_failure_to_commit_auth_reservation_prevents_login(self):
        manager, issuer = self.manager(), Mock(return_value=TokenGrant('unused'))
        with manager.session():
            with patch.object(manager.store.connection, 'commit', side_effect=RuntimeError('commit failed')):
                with self.assertRaises(TokenCacheError):
                    manager.get(issuer)
        issuer.assert_not_called()

    def test_failure_to_save_generated_token_does_not_allow_immediate_new_login(self):
        manager, issuer = self.manager(), Mock(return_value=TokenGrant('private-token'))
        save = manager.store.save
        calls = []
        def fail_once(owner, updates):
            calls.append(updates)
            if len(calls) == 1:
                raise TokenCacheError('No se pudo guardar el token')
            return save(owner, updates)
        with patch.object(manager.store, 'save', side_effect=fail_once):
            with self.assertRaises(TokenCacheError):
                manager.get(issuer)
        with self.assertRaisesRegex(TokenCacheError, 'espera de seguridad'):
            self.manager().get(issuer)
        self.assertEqual(issuer.call_count, 1)


class FunctionalResponseTest(unittest.TestCase):
    def setUp(self):
        self.manager = make_manager()
        self.client = AivoClient(AivoSettings('user', 'password', 'x-token'), self.manager)

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_200_auth_exceptions_never_accept_token_or_retry(self, post):
        for data in ({'error': 'failed'}, {'exception': 'BadCredentials'}, {'success': False},
                     {'data': {'errors': ['invalid']}}, {'status': 'error'},
                     {'name': 'NotAuthorizedException'}, {'type': 'error'}):
            with self.subTest(data=data):
                manager = make_manager()
                client = AivoClient(self.client.settings, manager)
                post.reset_mock()
                post.return_value = answer(dict(data, Authorization='Bearer should-not-use'))
                with self.assertRaises(AivoError) as raised:
                    client.authenticate()
                self.assertTrue(raised.exception.functional_error)
                self.assertIsNone(raised.exception.response_body)
                self.assertEqual(post.call_count, 1)

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_user_blocked_even_200_stops_future_runs(self, post):
        post.return_value = answer({'Authorization': 'Bearer unusable', 'message': 'UserBlockedException'})
        with self.assertRaises(AivoError) as raised:
            self.client.authenticate()
        self.assertTrue(raised.exception.account_blocked)
        self.manager.store.now += 36000
        another = AivoClient(self.client.settings, make_manager(self.manager.store))
        with self.assertRaisesRegex(AivoError, 'bloqueada'):
            another.authenticate()
        self.assertEqual(post.call_count, 1)

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_200_send_functional_error_is_not_success_or_retried(self, post):
        post.return_value = answer({'exception': 'InvalidTemplate'})
        with self.assertRaises(AivoError) as raised:
            self.client.send_authenticated({'to': '999876502'}, 'old-token')
        self.assertTrue(raised.exception.functional_error)
        self.assertEqual(raised.exception.http_status, 200)
        self.assertEqual(post.call_count, 1)

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_block_on_send_is_persisted_even_with_http_401(self, post):
        post.return_value = answer({'error': 'UserBlockedException'}, 401)
        with self.assertRaises(AivoError) as raised:
            self.client.send_authenticated({}, 'old-token')
        self.assertTrue(raised.exception.account_blocked)
        self.assertEqual(self.manager.status()['blocked'], 1)
        self.assertEqual(post.call_count, 1)
        with self.assertRaisesRegex(AivoError, 'bloqueada'):
            self.client.send_authenticated({}, 'any-token')
        self.assertEqual(post.call_count, 1)

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_first_401_renews_once_but_a_recent_new_token_does_not_reauthenticate(self, post):
        self.manager.get(lambda: TokenGrant('old-token'))
        self.manager.store.now += 3600
        post.side_effect = [answer({}, 401), answer({'Authorization': 'Bearer new-token'}), answer({'id': 'ok'})]
        self.assertEqual(self.client.send_authenticated({}, 'old-token').auth_refreshes, 1)
        post.side_effect = [answer({}, 401)]
        with self.assertRaisesRegex(AivoError, 'espera de seguridad'):
            self.client.send_authenticated({}, 'new-token')
        self.assertEqual(post.call_count, 4)
