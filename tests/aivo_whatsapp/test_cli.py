import io
import json
import os
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import Mock, patch

import requests

from src.aivo_whatsapp.cli import main


class CLITest(unittest.TestCase):
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
        self.assertTrue(run.call_args.args[-1])
        connection.close.assert_called_once()
        post.assert_not_called()
