import io
import json
import os
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

from src.aivo_whatsapp.cli import main


class CLITest(unittest.TestCase):
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
