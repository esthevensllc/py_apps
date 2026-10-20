from __future__ import annotations

import base64
import json
import math
import os
import re
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Optional
from urllib.parse import urlsplit

import requests

from .token_cache import TokenCacheError, TokenGrant, build_token_coordinator


AUTH_URL = 'https://gateway.aivo.co/api/v1/auth'
SEND_URL = 'https://gateway.aivo.co/api/v1/conversation-whatsapp-native-templates'
NAMESPACE = 'c44af9b7_3008_4b30_b7e8_070c35442389'
TEMPLATES = {
    'averia_diagnosticada': ('69f45f6b-31d3-4337-b6d5-b0f31997aef5', 'es_PE'),
    'averia_solucionada': ('a8a6350f-898a-4077-a20e-8b96e3731786', 'en'),
}


class AivoError(RuntimeError):
    """Error de comunicación o respuesta inválida de Aivo."""

    def __init__(self, message, http_status=None, response_body=None, auth_failure=False,
                 account_blocked=False, error_code=None, functional_error=False):
        super().__init__(message)
        self.http_status = http_status
        self.response_body = response_body
        self.auth_failure = auth_failure
        self.account_blocked = account_blocked
        self.error_code = error_code
        self.functional_error = functional_error


@dataclass(frozen=True)
class AivoResponse:
    status_code: int
    data: Any
    body: str
    auth_refreshes: int = 0


def redact_body(body: str, secrets: list) -> str:
    body = re.sub(r'(?i)\bBearer\s+[^\s\'"<>]+', 'Bearer [oculto]', body)
    body = re.sub(
        r'(?i)("(?:authorization|password|access_token|token|x-token)"\s*:\s*)"[^"\r\n]*"',
        r'\1"[oculto]"', body,
    )
    for secret in sorted((value for value in secrets if value), key=len, reverse=True):
        body = body.replace(secret, '[oculto]')
    return body


def connection_error_detail(error: requests.RequestException, secrets: list) -> str:
    """Conserva la causa de red y oculta credenciales en errores y URLs de proxy."""
    detail = str(error)
    detail = re.sub(r'(?i)(https?://)[^/\s@]+@', r'\1[oculto]@', detail)
    detail = re.sub(r'(?i)\bBearer\s+[^\s\'"<>]+', 'Bearer [oculto]', detail)
    for secret in sorted((value for value in secrets if value), key=len, reverse=True):
        detail = detail.replace(secret, '[oculto]')
    detail = ' '.join(detail.split())[:600]
    return f'{type(error).__name__}: {detail}' if detail else type(error).__name__


@dataclass(frozen=True)
class AivoSettings:
    user: str = field(repr=False)
    password: str = field(repr=False)
    x_token: str = field(repr=False)
    timeout: float = 30.0
    token_field: Optional[str] = None
    http_proxy: Optional[str] = field(default=None, repr=False)
    https_proxy: Optional[str] = field(default=None, repr=False)
    token_encryption_key: str = field(default='', repr=False)
    token_refresh_hours: float = 9.0
    auth_min_interval: float = 900.0

    def __post_init__(self):
        for name in ('user', 'password', 'x_token'):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f'Falta AIVO_{name.upper()}')
        if '\r' in self.x_token or '\n' in self.x_token:
            raise ValueError('AIVO_X_TOKEN contiene caracteres inválidos')
        if not math.isfinite(self.timeout) or self.timeout <= 0:
            raise ValueError('AIVO_TIMEOUT debe ser un número positivo finito')
        if not math.isfinite(self.token_refresh_hours) or not 1 <= self.token_refresh_hours <= 9:
            raise ValueError('AIVO_TOKEN_REFRESH_HOURS debe estar entre 1 y 9')
        if not math.isfinite(self.auth_min_interval) or not 900 <= self.auth_min_interval <= 3600:
            raise ValueError('AIVO_AUTH_MIN_INTERVAL debe estar entre 900 y 3600 segundos')
        for name in ('http_proxy', 'https_proxy'):
            proxy = getattr(self, name)
            if proxy is not None:
                try:
                    parsed = urlsplit(proxy)
                    valid = parsed.scheme in ('http', 'https') and bool(parsed.hostname)
                    valid = valid and not any(char.isspace() for char in proxy)
                    parsed.port  # Valida también el puerto, si fue especificado.
                except ValueError:
                    valid = False
                if not valid:
                    raise ValueError(f'AIVO_{name.upper()} debe ser una URL de proxy HTTP o HTTPS válida')

    @classmethod
    def from_environment(cls) -> 'AivoSettings':
        try:
            timeout = float(os.getenv('AIVO_TIMEOUT', '30'))
        except ValueError as error:
            raise ValueError('AIVO_TIMEOUT debe ser un número positivo finito') from error
        try:
            refresh_hours = float(os.getenv('AIVO_TOKEN_REFRESH_HOURS', '9'))
            minimum_interval = float(os.getenv('AIVO_AUTH_MIN_INTERVAL', '900'))
        except ValueError as error:
            raise ValueError('AIVO_TOKEN_REFRESH_HOURS y AIVO_AUTH_MIN_INTERVAL deben ser números válidos') from error
        return cls(
            user=os.getenv('AIVO_USER', ''),
            password=os.getenv('AIVO_PASSWORD', ''),
            x_token=os.getenv('AIVO_X_TOKEN', ''),
            timeout=timeout,
            token_field=os.getenv('AIVO_AUTH_TOKEN_FIELD') or None,
            http_proxy=os.getenv('AIVO_HTTP_PROXY') or None,
            https_proxy=os.getenv('AIVO_HTTPS_PROXY') or None,
            token_encryption_key=os.getenv('AIVO_TOKEN_ENCRYPTION_KEY', ''),
            token_refresh_hours=refresh_hours,
            auth_min_interval=minimum_interval,
        )


def build_payload(
    template_name: str,
    to: str,
    nombre: str,
    hora: Optional[str] = None,
    periodo: Optional[str] = None,
) -> dict:
    """Construye y valida una de las dos plantillas proporcionadas."""
    if template_name not in TEMPLATES:
        raise ValueError('Plantilla no soportada: ' + template_name)
    if not isinstance(to, str) or not re.fullmatch(r'\+?[0-9]{7,15}', to):
        raise ValueError('El celular debe contener entre 7 y 15 dígitos, con + opcional')
    if not isinstance(nombre, str) or not nombre.strip():
        raise ValueError('El nombre es obligatorio')
    parameters = [{'type': 'text', 'text': nombre.strip()}]
    if template_name == 'averia_diagnosticada':
        if not isinstance(hora, str) or not re.fullmatch(r'(0[1-9]|1[0-2]):[0-5][0-9]', hora.strip()):
            raise ValueError('La hora es obligatoria y debe usar el formato hh:mm (01:00 a 12:59)')
        if not isinstance(periodo, str) or periodo.upper() not in ('AM', 'PM'):
            raise ValueError('El periodo es obligatorio y debe ser AM o PM')
        parameters.extend([
            {'type': 'text', 'text': hora.strip()},
            {'type': 'text', 'text': periodo.upper()},
        ])
    elif hora is not None or periodo is not None:
        raise ValueError('averia_solucionada solo recibe el nombre como parámetro')
    campaign_id, language = TEMPLATES[template_name]
    return {
        'to': to,
        'type': 'template',
        'recipient_type': 'individual',
        'campaign_id': campaign_id,
        'template': {
            'namespace': NAMESPACE,
            'name': template_name,
            'language': {'policy': 'deterministic', 'code': language},
            'components': [{'type': 'body', 'parameters': parameters}],
        },
    }


class AivoClient:
    """Solicita tokens y renueva una vez ante HTTP 401; no repite envíos inciertos."""

    def __init__(self, settings: AivoSettings, token_coordinator=None):
        self.settings = settings
        self._coordinator = token_coordinator

    @property
    def coordinator(self):
        if self._coordinator is None:
            self._coordinator = build_token_coordinator(self.settings)
        return self._coordinator

    @contextmanager
    def account_session(self):
        try:
            with self.coordinator.session():
                yield
        except TokenCacheError as error:
            raise AivoError(str(error), auth_failure=True, account_blocked=error.account_blocked) from error

    def auth_status(self):
        with self.account_session():
            return self.coordinator.status()

    def _post(self, url: str, payload: dict, headers: dict, operation: str) -> Any:
        state = self.coordinator.touch()  # Verificar la exclusión antes de cada llamada externa.
        if state['blocked']:
            raise AivoError('ALERTA AIVO: cuenta bloqueada; no se autoriza otra llamada.',
                            auth_failure=True, account_blocked=True)
        options = {}
        proxies = {
            scheme: proxy for scheme, proxy in (
                ('http', self.settings.http_proxy), ('https', self.settings.https_proxy),
            ) if proxy
        }
        if proxies:
            options['proxies'] = proxies
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.settings.timeout,
                allow_redirects=False,
                **options,
            )
        except requests.Timeout as error:
            detail = (
                ' El estado del envío es incierto; verifique en Aivo antes de repetirlo.'
                if operation == 'envío' else ''
            )
            raise AivoError(f'Tiempo de espera agotado durante {operation}.{detail}') from error
        except requests.RequestException as error:
            cause = connection_error_detail(error, [
                self.settings.user, self.settings.password, self.settings.x_token,
                headers.get('Authorization', '')[7:],
                self.settings.http_proxy, self.settings.https_proxy,
            ])
            if isinstance(error, requests.exceptions.SSLError):
                hint = ' Revise el certificado TLS y las CA confiables del contenedor.'
            elif isinstance(error, requests.exceptions.ProxyError):
                hint = ' Revise AIVO_HTTP_PROXY, AIVO_HTTPS_PROXY y la conexión al proxy desde el contenedor.'
            else:
                hint = ' Revise DNS y la salida HTTPS desde el contenedor hacia gateway.aivo.co.'
            detail = (
                ' Verifique el estado en Aivo antes de repetir el envío.'
                if operation == 'envío' else ''
            )
            raise AivoError(
                f'Error de conexión durante {operation} ({cause}).{hint}{detail}'
            ) from error
        try:
            data = response.json() if response.content else None
            invalid_json = False
        except ValueError:
            data, invalid_json = None, True
        issue = self._functional_error(data)
        if issue == 'UserBlockedException':
            self.coordinator.block(issue)
            raise AivoError('ALERTA AIVO: UserBlockedException. Cuenta detenida hasta revisión del proveedor.',
                            response.status_code, auth_failure=True, account_blocked=True,
                            error_code=issue, functional_error=True)
        if not 200 <= response.status_code < 300:
            body = self._response_body(response, headers) if operation == 'envío' else None
            raise AivoError(
                f'Aivo devolvió HTTP {response.status_code} durante {operation}',
                http_status=response.status_code, response_body=body,
            )
        if operation == 'envío' and not response.content:
            return AivoResponse(response.status_code, None, '')
        if invalid_json:
            detail = (
                ' La solicitud pudo ser aceptada; verifique en Aivo antes de repetirla.'
                if operation == 'envío' else ''
            )
            body = self._response_body(response, headers) if operation == 'envío' else None
            raise AivoError(
                f'Respuesta JSON inválida durante {operation}.{detail}',
                http_status=response.status_code, response_body=body,
            )
        if issue:
            raise AivoError(f'Aivo devolvió un error funcional durante {operation}; no se reintenta.',
                            response.status_code,
                            self._response_body(response, headers) if operation == 'envío' else None,
                            auth_failure=operation != 'envío', error_code=issue, functional_error=True)
        if operation == 'envío':
            return AivoResponse(response.status_code, data, self._response_body(response, headers))
        return data

    @staticmethod
    def _functional_error(data):
        """Detecta errores de gateway aun con HTTP 200, sin exponer el cuerpo de /auth."""
        if isinstance(data, str):
            return 'UserBlockedException' if 'userblockedexception' in data.casefold() else None
        if isinstance(data, list):
            issues = [AivoClient._functional_error(item) for item in data]
            return 'UserBlockedException' if 'UserBlockedException' in issues else next(filter(None, issues), None)
        if not isinstance(data, dict):
            return None
        # Un bloqueo tiene prioridad sobre cualquier otro error/token del mismo JSON.
        if 'userblockedexception' in json.dumps(data).casefold():
            return 'UserBlockedException'
        for key, value in data.items():
            name = str(key).casefold()
            if (name in ('error', 'errors', 'exception') and value not in (None, False, '', [], {})) or (
                name == 'success' and value is False
            ) or (name in ('status', 'type') and isinstance(value, str) and value.casefold() in ('error', 'failed', 'failure')) or (
                name in ('name', 'code', 'errortype', '__type') and isinstance(value, str) and value.casefold().endswith('exception')
            ):
                return 'FunctionalError'
            if isinstance(value, (dict, list)):
                issue = AivoClient._functional_error(value)
                if issue:
                    return issue
        return None

    def _response_body(self, response, headers) -> str:
        import json

        body = getattr(response, 'text', '')
        if not isinstance(body, str):
            try:
                body = json.dumps(response.json(), ensure_ascii=False)
            except ValueError:
                body = ''
        return redact_body(body, [
            self.settings.user, self.settings.password, self.settings.x_token,
            headers.get('Authorization', '')[7:],
        ])

    @staticmethod
    def _usable_token(value) -> Optional[str]:
        if not isinstance(value, str):
            return None
        token = value.strip()
        if token.lower().startswith('bearer '):
            token = token[7:].strip()
        if not token or token.lower() == 'bearer' or any(char.isspace() for char in token):
            return None
        # Solo se consulta exp para evitar usar un JWT ya vencido. La validación
        # criptográfica y de permisos siempre corresponde a Aivo.
        parts = token.split('.')
        if len(parts) == 3:
            try:
                claims = json.loads(base64.urlsafe_b64decode(parts[1] + '=' * (-len(parts[1]) % 4)))
                expiry = claims.get('exp') if isinstance(claims, dict) else None
                if expiry is not None and (
                    not isinstance(expiry, (int, float)) or not math.isfinite(expiry) or expiry <= time.time() + 30
                ):
                    return None
            except (ValueError, UnicodeError):
                pass  # Los tokens opacos siguen siendo validados por el gateway.
        return token

    def authenticate(self) -> str:
        """Reutiliza el bearer compartido; un único POST cuando corresponde renovarlo."""
        return self._get_token()

    def _get_token(self, rejected_token=None):
        with self.account_session():
            try:
                return self.coordinator.get(self._authenticate_once, rejected_token)
            except AivoError as error:
                error.auth_failure = True
                raise

    def _authenticate_once(self) -> TokenGrant:
        result = self._post(
            AUTH_URL,
            {'user': self.settings.user, 'password': self.settings.password},
            {'Content-Type': 'application/json', 'Accept': 'application/json'},
            'autenticación',
        )
        # Un campo configurado incorrectamente no debe ocultar Authorization.
        paths = [self.settings.token_field] if self.settings.token_field else []
        paths += ['Authorization', 'token', 'access_token', 'data.Authorization',
                  'data.token', 'data.access_token', 'headers.Authorization']
        for path in paths:
            value = result
            for part in path.split('.'):
                value = next((item for key, item in value.items() if str(key).casefold() == part.casefold()), None) if isinstance(value, dict) else None
            token = self._usable_token(value)
            if token:
                expiry = None
                parts = token.split('.')
                if len(parts) == 3:
                    try:
                        claims = json.loads(base64.urlsafe_b64decode(parts[1] + '=' * (-len(parts[1]) % 4)))
                        expiry = claims.get('exp') if isinstance(claims, dict) else None
                    except (ValueError, UnicodeError):
                        pass
                return TokenGrant(token, expiry)
        raise AivoError(
            'La respuesta de autenticación no contiene un token utilizable o está vencido. '
            'Se buscó Authorization y los campos alternativos; revise AIVO_AUTH_TOKEN_FIELD.'
        )

    def send_message(
        self,
        template_name: str,
        to: str,
        nombre: str,
        hora: Optional[str] = None,
        periodo: Optional[str] = None,
    ) -> Any:
        payload = build_payload(template_name, to, nombre, hora, periodo)
        with self.account_session():
            token = self.authenticate()
            return self.send_authenticated(payload, token).data

    def send_authenticated(self, payload: dict, token: str) -> AivoResponse:
        with self.account_session():
            return self._send_authenticated(payload, token)

    def _send_authenticated(self, payload: dict, token: str) -> AivoResponse:
        """Renueva solo ante ausencia/vencimiento o rechazo explícito HTTP 401."""
        refreshes = 0
        token = self._usable_token(token)
        if token is None:
            token = self.authenticate()
            refreshes = 1
        try:
            result = self._send_once(payload, token)
        except AivoError as error:
            if error.http_status != 401 or refreshes or error.account_blocked or error.functional_error:
                raise
            # HTTP 401 rechaza la solicitud por falta de credenciales válidas.
            # Mantener la misma reserva; nunca renovar por timeout/5xx/JSON inválido.
            token = self._get_token(rejected_token=token)
            refreshes = 1
            result = self._send_once(payload, token)
        return AivoResponse(result.status_code, result.data, result.body, refreshes)

    def _send_once(self, payload: dict, token: str) -> AivoResponse:
        try:
            return self._post(
                SEND_URL,
                payload,
                {
                    'Authorization': f'Bearer {token}',
                    'X-Token': self.settings.x_token,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                'envío',
            )
        except AivoError as error:
            if error.http_status == 401 and not error.account_blocked:
                self.coordinator.reject(token)
            raise
