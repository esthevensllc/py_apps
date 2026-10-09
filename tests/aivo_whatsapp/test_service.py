import os
import unittest
from unittest.mock import Mock, call, patch

import requests

from src.aivo_whatsapp import AivoClient, AivoError, AivoSettings


def response(data=None, status=200, content=b'{}'):
    result = Mock(status_code=status, content=content)
    result.json.return_value = data
    return result


class AivoClientTest(unittest.TestCase):
    def setUp(self):
        self.settings = AivoSettings('usuario', 'clave', 'x-token')
        self.client = AivoClient(self.settings)

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_corporate_proxies_are_used_for_auth_and_send(self, post):
        with patch.dict(os.environ, {
            'AIVO_USER': 'usuario', 'AIVO_PASSWORD': 'clave', 'AIVO_X_TOKEN': 'x-token',
            'AIVO_HTTP_PROXY': 'http://claro-proxy',
            'AIVO_HTTPS_PROXY': 'http://claro-proxy',
        }, clear=True):
            client = AivoClient(AivoSettings.from_environment())
        post.side_effect = [response({'Authorization': 'Bearer jwt'}), response({'id': 'ok'})]
        client.send_message('averia_solucionada', '999876502', 'Daniel')
        self.assertEqual(post.call_count, 2)
        for request in post.call_args_list:
            self.assertEqual(request.kwargs['proxies'], {
                'http': 'http://claro-proxy', 'https': 'http://claro-proxy',
            })
            self.assertNotIn('verify', request.kwargs)  # TLS habilitado por defecto.

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_network_errors_explain_cause_without_exposing_credentials(self, post):
        cases = [
            (requests.exceptions.SSLError('CERTIFICATE_VERIFY_FAILED clave'), 'SSLError', 'TLS'),
            (requests.exceptions.ProxyError('https://proxyuser:proxypass@claro-proxy'), 'ProxyError', 'proxy'),
            (requests.ConnectionError('NameResolutionError usuario'), 'ConnectionError', 'DNS'),
        ]
        for error, expected_type, expected_hint in cases:
            with self.subTest(error=expected_type):
                post.side_effect = error
                with self.assertRaises(AivoError) as raised:
                    self.client.authenticate()
                message = str(raised.exception)
                self.assertIn(expected_type, message)
                self.assertIn(expected_hint, message)
                for secret in ('clave', 'usuario', 'proxyuser', 'proxypass'):
                    self.assertNotIn(secret, message)

    def test_invalid_proxy_is_rejected_without_exposing_its_value(self):
        for proxy in ('claro-proxy', 'ftp://claro-proxy', 'http://claro-proxy:invalid'):
            with self.subTest(proxy=proxy), self.assertRaisesRegex(ValueError, 'AIVO_HTTPS_PROXY'):
                AivoSettings('usuario', 'clave', 'x-token', https_proxy=proxy)

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_send_response_keeps_status_and_body_without_tokens(self, post):
        answer = response({'id': 'ok'}, 202)
        answer.text = '{"id":"ok","Authorization":"Bearer private-jwt","password":"clave"}'
        post.return_value = answer
        result = self.client.send_authenticated({'to': '999876502'}, 'private-jwt')
        self.assertEqual(result.status_code, 202)
        self.assertIn('"id":"ok"', result.body)
        self.assertNotIn('private-jwt', result.body)
        self.assertNotIn('clave', result.body)

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_http_error_exposes_status_and_safe_body_to_log(self, post):
        answer = response({}, 400)
        answer.text = '{"error":"invalid","token":"secret-other-token"}'
        post.return_value = answer
        with self.assertRaises(AivoError) as raised:
            self.client.send_authenticated({'to': '999876502'}, 'private-jwt')
        self.assertEqual(raised.exception.http_status, 400)
        self.assertIn('invalid', raised.exception.response_body)
        self.assertNotIn('secret-other-token', raised.exception.response_body)

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_diagnosticada_posts_auth_then_exact_message_contract(self, post):
        post.side_effect = [response({'Authorization': 'Bearer jwt'}), response({'id': 'mensaje'})]
        result = self.client.send_message(
            'averia_diagnosticada', '999876502', 'Daniel Muñante', '08:00 ', 'PM'
        )
        self.assertEqual(result, {'id': 'mensaje'})
        self.assertEqual(post.call_count, 2)
        self.assertEqual(post.call_args_list[0], call(
            'https://gateway.aivo.co/api/v1/auth',
            json={'user': 'usuario', 'password': 'clave'},
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
            timeout=30.0,
            allow_redirects=False,
        ))
        self.assertEqual(post.call_args_list[1], call(
            'https://gateway.aivo.co/api/v1/conversation-whatsapp-native-templates',
            json={
                'to': '999876502', 'type': 'template', 'recipient_type': 'individual',
                'campaign_id': '69f45f6b-31d3-4337-b6d5-b0f31997aef5',
                'template': {
                    'namespace': 'c44af9b7_3008_4b30_b7e8_070c35442389',
                    'name': 'averia_diagnosticada',
                    'language': {'policy': 'deterministic', 'code': 'es_PE'},
                    'components': [{'type': 'body', 'parameters': [
                        {'type': 'text', 'text': 'Daniel Muñante'},
                        {'type': 'text', 'text': '08:00'},
                        {'type': 'text', 'text': 'PM'},
                    ]}],
                },
            },
            headers={'Authorization': 'Bearer jwt', 'X-Token': 'x-token',
                     'Content-Type': 'application/json', 'Accept': 'application/json'},
            timeout=30.0,
            allow_redirects=False,
        ))

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_authorization_field_takes_priority_and_does_not_duplicate_bearer(self, post):
        post.side_effect = [
            response({'Authorization': 'Bearer jwt', 'token': 'otro-token'}),
            response({'id': 'ok'}),
        ]
        self.client.send_message('averia_solucionada', '999876502', 'Daniel')
        self.assertEqual(post.call_args.kwargs['headers']['Authorization'], 'Bearer jwt')

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_each_send_obtains_a_new_token(self, post):
        post.side_effect = [
            response({'Authorization': 'Bearer token-1'}), response({'id': 'mensaje-1'}),
            response({'Authorization': 'Bearer token-2'}), response({'id': 'mensaje-2'}),
        ]
        for _ in range(2):
            self.client.send_message('averia_solucionada', '999876502', 'Daniel')
        self.assertEqual(post.call_count, 4)
        self.assertEqual(post.call_args_list[1].kwargs['headers']['Authorization'], 'Bearer token-1')
        self.assertEqual(post.call_args_list[3].kwargs['headers']['Authorization'], 'Bearer token-2')

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_solucionada_uses_its_campaign_language_and_one_parameter(self, post):
        post.side_effect = [response({'data': {'access_token': 'Bearer jwt'}}), response({'id': 'ok'})]
        self.client.send_message('averia_solucionada', '999876502', 'Daniel Muñante')
        payload = post.call_args.kwargs['json']
        self.assertEqual(payload['campaign_id'], 'a8a6350f-898a-4077-a20e-8b96e3731786')
        self.assertEqual(payload['template']['name'], 'averia_solucionada')
        self.assertEqual(payload['template']['language']['code'], 'en')
        self.assertEqual(payload['template']['components'][0]['parameters'], [
            {'type': 'text', 'text': 'Daniel Muñante'}
        ])
        self.assertEqual(post.call_args.kwargs['headers']['Authorization'], 'Bearer jwt')

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_custom_token_path(self, post):
        post.return_value = response({'result': {'bearer': 'jwt'}})
        client = AivoClient(AivoSettings('usuario', 'clave', 'x-token', token_field='result.bearer'))
        self.assertEqual(client.authenticate(), 'jwt')

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_bad_auth_never_sends_and_never_exposes_response(self, post):
        for auth in [response({'password': 'secreto'}, 401), response({'unexpected': 'secreto'}),
                     response({'token': 'invalid\nheader'})]:
            with self.subTest(auth=auth):
                post.reset_mock()
                post.return_value = auth
                with self.assertRaises(AivoError) as raised:
                    self.client.send_message('averia_solucionada', '999876502', 'Daniel')
                self.assertEqual(post.call_count, 1)
                self.assertNotIn('secreto', str(raised.exception))

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_invalid_parameters_never_call_network(self, post):
        cases = [
            ('averia_solucionada', 'abc', 'Daniel', None, None),
            ('averia_solucionada', '999876502', '', None, None),
            ('averia_diagnosticada', '999876502', 'Daniel', None, None),
            ('averia_diagnosticada', '999876502', 'Daniel', '20:00', 'PM'),
            ('averia_diagnosticada', '999876502', 'Daniel', '08:00', 'INVALID'),
            ('averia_solucionada', '999876502', 'Daniel', '08:00', 'PM'),
        ]
        for values in cases:
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.client.send_message(*values)
        post.assert_not_called()

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_send_failures_are_not_retried(self, post):
        for failure in [requests.Timeout(), requests.ConnectionError(), response({}, 500),
                        response({}, 302), response({}, 429)]:
            with self.subTest(failure=failure):
                post.reset_mock()
                post.side_effect = [response({'token': 'jwt'}), failure]
                with self.assertRaises(AivoError):
                    self.client.send_message('averia_solucionada', '999876502', 'Daniel')
                self.assertEqual(post.call_count, 2)

    @patch('src.aivo_whatsapp.service.requests.post')
    def test_invalid_json_and_empty_success(self, post):
        bad_json = response()
        bad_json.json.side_effect = ValueError('datos privados')
        post.side_effect = [response({'token': 'jwt'}), bad_json]
        with self.assertRaisesRegex(AivoError, 'pudo ser aceptada'):
            self.client.send_message('averia_solucionada', '999876502', 'Daniel')
        post.side_effect = [response({'token': 'jwt'}), response(status=204, content=b'')]
        self.assertIsNone(self.client.send_message('averia_solucionada', '999876502', 'Daniel'))

    def test_settings_reject_missing_secrets_and_invalid_timeout(self):
        for timeout in [0, -1, float('nan'), float('inf')]:
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                AivoSettings('usuario', 'clave', 'x-token', timeout=timeout)
        with self.assertRaises(ValueError):
            AivoSettings('usuario', '', 'x-token')
        self.assertNotIn('clave', repr(self.settings))


if __name__ == '__main__':
    unittest.main()
