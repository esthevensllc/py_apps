from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass, field
from typing import Any, Optional

import requests


AUTH_URL = 'https://gateway.aivo.co/api/v1/auth'
SEND_URL = 'https://gateway.aivo.co/api/v1/conversation-whatsapp-native-templates'
NAMESPACE = 'c44af9b7_3008_4b30_b7e8_070c35442389'
TEMPLATES = {
    'averia_diagnosticada': ('69f45f6b-31d3-4337-b6d5-b0f31997aef5', 'es_PE'),
    'averia_solucionada': ('a8a6350f-898a-4077-a20e-8b96e3731786', 'en'),
}


class AivoError(RuntimeError):
    """Error de comunicación o respuesta inválida de Aivo."""


@dataclass(frozen=True)
class AivoSettings:
    user: str = field(repr=False)
    password: str = field(repr=False)
    x_token: str = field(repr=False)
    timeout: float = 30.0
    token_field: Optional[str] = None

    def __post_init__(self):
        for name in ('user', 'password', 'x_token'):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f'Falta AIVO_{name.upper()}')
        if '\r' in self.x_token or '\n' in self.x_token:
            raise ValueError('AIVO_X_TOKEN contiene caracteres inválidos')
        if not math.isfinite(self.timeout) or self.timeout <= 0:
            raise ValueError('AIVO_TIMEOUT debe ser un número positivo finito')

    @classmethod
    def from_environment(cls) -> 'AivoSettings':
        try:
            timeout = float(os.getenv('AIVO_TIMEOUT', '30'))
        except ValueError as error:
            raise ValueError('AIVO_TIMEOUT debe ser un número positivo finito') from error
        return cls(
            user=os.getenv('AIVO_USER', ''),
            password=os.getenv('AIVO_PASSWORD', ''),
            x_token=os.getenv('AIVO_X_TOKEN', ''),
            timeout=timeout,
            token_field=os.getenv('AIVO_AUTH_TOKEN_FIELD') or None,
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
    """Autentica y solicita un envío por llamada, sin reintentos automáticos."""

    def __init__(self, settings: AivoSettings):
        self.settings = settings

    def _post(self, url: str, payload: dict, headers: dict, operation: str) -> Any:
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.settings.timeout,
                allow_redirects=False,
            )
        except requests.Timeout as error:
            detail = (
                ' El estado del envío es incierto; verifique en Aivo antes de repetirlo.'
                if operation == 'envío' else ''
            )
            raise AivoError(f'Tiempo de espera agotado durante {operation}.{detail}') from error
        except requests.RequestException as error:
            detail = (
                ' Verifique el estado en Aivo antes de repetir el envío.'
                if operation == 'envío' else ''
            )
            raise AivoError(f'Error de conexión durante {operation}.{detail}') from error
        if not 200 <= response.status_code < 300:
            # No exponer cuerpos de error: pueden contener credenciales o datos personales.
            raise AivoError(f'Aivo devolvió HTTP {response.status_code} durante {operation}')
        if operation == 'envío' and not response.content:
            return None
        try:
            return response.json()
        except ValueError as error:
            detail = (
                ' La solicitud pudo ser aceptada; verifique en Aivo antes de repetirla.'
                if operation == 'envío' else ''
            )
            raise AivoError(f'Respuesta JSON inválida durante {operation}.{detail}') from error

    def authenticate(self) -> str:
        result = self._post(
            AUTH_URL,
            {'user': self.settings.user, 'password': self.settings.password},
            {'Content-Type': 'application/json', 'Accept': 'application/json'},
            'autenticación',
        )
        # /auth devuelve {"Authorization": "Bearer <token>"}.
        # La ruta explícita permite adaptar el proceso a otra respuesta.
        paths = (
            [self.settings.token_field] if self.settings.token_field
            else ['Authorization', 'token', 'access_token', 'data.token', 'data.access_token']
        )
        for path in paths:
            value = result
            for part in path.split('.'):
                value = value.get(part) if isinstance(value, dict) else None
            if isinstance(value, str) and value.strip():
                token = value.strip()
                if token.lower().startswith('bearer '):
                    token = token[7:].strip()
                if token and not any(char.isspace() for char in token):
                    return token
        raise AivoError(
            'La respuesta de autenticación no contiene un token válido. '
            'Configure AIVO_AUTH_TOKEN_FIELD con la ruta del campo del token.'
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
        token = self.authenticate()
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
