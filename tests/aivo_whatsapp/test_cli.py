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
            status = main(['--plantilla', 'averia_solucionada', '--to', '999876502', '--nombre', 'Daniel'])
        self.assertEqual(status, 1)
        self.assertIn('AIVO_USER', errors.getvalue())
        post.assert_not_called()
