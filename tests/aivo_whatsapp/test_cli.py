import io
import json
import os
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import Mock, patch

import requests

from src.aivo_whatsapp.cli import main
from token_support import make_manager


class CLITest(unittest.TestCase):
    def setUp(self):
        factory = patch('src.aivo_whatsapp.service.build_token_coordinator', side_effect=lambda settings: make_manager())
        factory.start()
        self.addCleanup(factory.stop)
    @patch('src.aivo_whatsapp.cli.load_dotenv')
    @patch('src.aivo_whatsapp.cli.connect_oracle')
    @patch('src.aivo_whatsapp.cli.OracleTestRepository')
    @patch('src.aivo_whatsapp.cli.run_batch')
    @patch('src.aivo_whatsapp.service.requests.post')
    def test_test_flags_select_test_repository_without_network_in_preview(self, post, run, test_repository, connect, load):
        connection, driver = Mock(), Mock()
        connect.return_value = (connection, driver)
        run.return_value = {'errores': 0, 'invalidos': 0}
        with redirect_stdout(io.StringIO()):
            status = main(['--from-oracle', '--test-to', '999876502', '--test-id', 'prueba_02', '--dry-run'])
        self.assertEqual(status, 0)
        test_repository.assert_called_once_with(connection, driver, '999876502', 'prueba_02')
        self.assertIs(run.call_args.args[0], test_repository.return_value)
        post.assert_not_called()

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_manual_test_requires_number_identifier_and_oracle_mode(self, post):
        for options in (
            ['--test-to', '999876502'],
            ['--from-oracle', '--test-to', '999876502'],
            ['--from-oracle', '--test-id', 'prueba_02'],
        ):
            with self.subTest(options=options), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main(options)
        post.assert_not_called()

    @patch('src.aivo_whatsapp.cli.load_dotenv')
    @patch('src.aivo_whatsapp.service.requests.post')
    def test_check_auth_never_sends_a_message_or_prints_token(self, post, load_env):
        post.return_value = Mock(status_code=200, content=b'json')
        post.return_value.json.return_value = {'Authorization': 'Bearer private-jwt'}
        output = io.StringIO()
        with patch.dict(os.environ, {
            'AIVO_USER': 'usuario', 'AIVO_PASSWORD': 'clave', 'AIVO_X_TOKEN': 'x-token',
            'AIVO_HTTP_PROXY': 'http://claro-proxy', 'AIVO_HTTPS_PROXY': 'http://claro-proxy',
        }, clear=True), redirect_stdout(output):
            status = main(['--check-auth'])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output.getvalue()), {'autenticacion_correcta': True})
        self.assertNotIn('private-jwt', output.getvalue())
        self.assertEqual(post.call_count, 1)
        self.assertEqual(post.call_args.args[0], 'https://gateway.aivo.co/api/v1/auth')

    @patch('src.aivo_whatsapp.cli.load_dotenv')
    @patch('src.aivo_whatsapp.service.requests.post')
    def test_check_auth_returns_connection_cause_on_failure(self, post, load_env):
        post.side_effect = requests.exceptions.ProxyError('Cannot connect to proxy')
        errors = io.StringIO()
        with patch.dict(os.environ, {
            'AIVO_USER': 'usuario', 'AIVO_PASSWORD': 'clave', 'AIVO_X_TOKEN': 'x-token',
        }, clear=True), redirect_stderr(errors):
            status = main(['--check-auth'])
        self.assertEqual(status, 1)
        self.assertIn('ProxyError', errors.getvalue())
        self.assertEqual(post.call_count, 1)

    @patch('src.aivo_whatsapp.cli.load_dotenv')
    @patch('src.aivo_whatsapp.service.requests.post')
    def test_auth_status_uses_shared_cache_and_never_calls_gateway(self, post, load_env):
        manager = make_manager()
        from src.aivo_whatsapp.token_cache import TokenGrant
        manager.get(lambda: TokenGrant('private-token'))
        output = io.StringIO()
        with patch.dict(os.environ, {
            'AIVO_USER': 'usuario', 'AIVO_PASSWORD': 'clave', 'AIVO_X_TOKEN': 'x-token',
        }, clear=True), patch('src.aivo_whatsapp.service.build_token_coordinator', return_value=manager), redirect_stdout(output):
            self.assertEqual(main(['--auth-status']), 0)
        data = json.loads(output.getvalue())
        self.assertIn('+00:00', data['generated_at'])
        self.assertEqual(data['blocked'], 0)
        self.assertNotIn('private-token', output.getvalue())
        post.assert_not_called()

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_check_auth_cannot_be_combined_with_send_options(self, post):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main(['--check-auth', '--plantilla', 'averia_solucionada'])
        post.assert_not_called()

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_dry_run_needs_no_credentials_and_never_calls_network(self, post):
        output = io.StringIO()
        with patch.dict(os.environ, {}, clear=True), redirect_stdout(output):
            status = main([
                '--plantilla', 'averia_diagnosticada', '--to', '999876502',
                '--nombre', 'Daniel Muñante', '--hora', '08:00', '--periodo', 'pm', '--dry-run',
            ])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output.getvalue())['template']['name'], 'averia_diagnosticada')
        post.assert_not_called()

    @patch('src.aivo_whatsapp.cli.load_dotenv')
    @patch('src.aivo_whatsapp.service.requests.post')
    def test_missing_credentials_returns_one_without_network(self, post, load_env):
        errors = io.StringIO()
        with patch.dict(os.environ, {}, clear=True), redirect_stderr(errors):
            status = main(['--check-auth'])
        self.assertEqual(status, 1)
        self.assertIn('AIVO_USER', errors.getvalue())
        post.assert_not_called()

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_direct_send_is_disabled_even_for_test_phone(self, post):
        errors = io.StringIO()
        with redirect_stderr(errors):
            status = main(['--plantilla', 'averia_solucionada', '--to', '999876502', '--nombre', 'Daniel'])
        self.assertEqual(status, 1)
        self.assertIn('--from-oracle', errors.getvalue())
        post.assert_not_called()

    @patch('src.aivo_whatsapp.cli.load_dotenv')
    @patch('src.aivo_whatsapp.cli.connect_oracle')
    @patch('src.aivo_whatsapp.cli.run_batch')
    @patch('src.aivo_whatsapp.service.requests.post')
    def test_oracle_preview_needs_no_aivo_credentials_and_closes_connection(self, post, run, connect, load):
        connection = Mock(autocommit=False)
        connect.return_value = (connection, Mock())
        run.return_value = {'errores': 0, 'invalidos': 0, 'vista_previa': []}
        with patch.dict(os.environ, {}, clear=True), redirect_stdout(io.StringIO()):
            status = main(['--from-oracle', '--dry-run', '--limit', '1'])
        self.assertEqual(status, 0)
        self.assertIsNone(run.call_args.args[1])
        self.assertEqual(run.call_args.kwargs, {'limit': 1, 'dry_run': True})
        connection.close.assert_called_once()
        post.assert_not_called()

    @patch('src.aivo_whatsapp.cli.load_dotenv')
    @patch('src.aivo_whatsapp.cli.connect_oracle')
    @patch('src.aivo_whatsapp.cli.run_batch')
    @patch('src.aivo_whatsapp.service.requests.post')
    def test_batch_exit_status_only_fails_when_errors_leave_zero_accepted(self, post, run, connect, load):
        cases = (
            ('sin candidatos', 0, 0, 0, 0, 0),
            ('todos duplicados', 0, 0, 0, 3, 0),
            ('todos invalidos', 0, 0, 3, 0, 0),
            ('exito parcial', 1, 2, 3, 0, 0),
            ('fallo total de envios', 0, 2, 0, 0, 1),
            ('errores e invalidos sin aceptados', 0, 2, 3, 0, 1),
        )
        connect.return_value = (Mock(autocommit=False), Mock())
        with patch.dict(os.environ, {
            'AIVO_USER': 'usuario', 'AIVO_PASSWORD': 'clave', 'AIVO_X_TOKEN': 'x-token',
        }, clear=True):
            for name, accepted, errors, invalid, blocked, expected in cases:
                result = dict(aceptados=accepted, errores=errors, invalidos=invalid, bloqueados=blocked)
                run.return_value = result
                output = io.StringIO()
                with self.subTest(name=name), redirect_stdout(output):
                    self.assertEqual(main(['--from-oracle']), expected)
                self.assertEqual(json.loads(output.getvalue()), result)
        post.assert_not_called()

    @patch('src.aivo_whatsapp.cli.load_dotenv')
    @patch('src.aivo_whatsapp.cli.connect_oracle')
    def test_database_failure_before_batch_returns_error(self, connect, load):
        from src.aivo_whatsapp.repository import OracleLogError
        connect.side_effect = OracleLogError('Fallo Oracle al conectar')
        with patch.dict(os.environ, {
            'AIVO_USER': 'usuario', 'AIVO_PASSWORD': 'clave', 'AIVO_X_TOKEN': 'x-token',
        }, clear=True), redirect_stderr(io.StringIO()):
            self.assertEqual(main(['--from-oracle']), 1)

    @patch('src.aivo_whatsapp.cli.load_dotenv')
    @patch('src.aivo_whatsapp.cli.connect_oracle')
    @patch('src.aivo_whatsapp.cli.run_batch')
    def test_connection_close_failure_preserves_only_confirmed_partial_success(self, run, connect, load):
        connection = Mock(autocommit=False)
        connection.close.side_effect = RuntimeError('detalle interno')
        connect.return_value = (connection, Mock())
        with patch.dict(os.environ, {
            'AIVO_USER': 'usuario', 'AIVO_PASSWORD': 'clave', 'AIVO_X_TOKEN': 'x-token',
        }, clear=True):
            for accepted, expected in ((1, 0), (0, 1)):
                run.return_value = dict(aceptados=accepted, errores=0, invalidos=0)
                output, errors = io.StringIO(), io.StringIO()
                with self.subTest(accepted=accepted), redirect_stdout(output), redirect_stderr(errors):
                    self.assertEqual(main(['--from-oracle']), expected)
                self.assertNotIn('detalle interno', errors.getvalue())
                if accepted:
                    self.assertTrue(json.loads(output.getvalue())['interrumpido'])
