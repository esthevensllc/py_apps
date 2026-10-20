from __future__ import annotations

import logging
from contextlib import nullcontext

from .models import Notification
from .repository import OracleLogError
from .service import AivoError, TEMPLATES

logger = logging.getLogger(__name__)


def _report_error(error):
    report = logger.critical if error.account_blocked else logger.error
    report('Aivo: %s', error)  # Mensaje sanitizado; nunca el cuerpo de /auth.


def run_batch(repository, client, template_name=None, limit=100, dry_run=False):
    """Entrada Airflow: recupera autenticación sin POST, nunca un envío incierto."""
    if template_name is not None and template_name not in TEMPLATES:
        raise ValueError('Plantilla no soportada')
    if not 1 <= limit <= 1000:
        raise ValueError('El límite debe estar entre 1 y 1000')
    repository.validate_safety()
    with (nullcontext() if dry_run else client.account_session()):
        return _send_batch(repository, client, template_name, limit, dry_run)


def _send_batch(repository, client, template_name, limit, dry_run):
    summary = {'candidatos': 0, 'aceptados': 0, 'bloqueados': 0, 'invalidos': 0, 'errores': 0, 'vista_previa': []}
    templates = (template_name,) if template_name else tuple(TEMPLATES)
    for template in templates:
        for row in repository.fetch_candidates(template, limit):
            summary['candidatos'] += 1
            try:
                notification = Notification.from_row(template, row)
                payload = repository.build_payload(notification)
            except ValueError:
                summary['invalidos'] += 1
                continue  # Sin fecha/celular/nombre confiable, no se reserva ni se envía.
            if dry_run:
                summary['vista_previa'].append(payload)
                continue
            record_id = repository.reserve(notification, payload)
            if record_id is None:
                summary['bloqueados'] += 1
                continue
            try:
                token = client.authenticate()
            except AivoError as error:
                _report_error(error)
                repository.finish(record_id, 'ERROR_AUTH', 'RESERVADO', error=error, http_status=error.http_status)
                summary['errores'] += 1
                return summary  # No autenticar cientos de clientes si /auth sigue fallando.
            # Si este commit falla, no se ejecuta el POST. Si el proceso muere después,
            # ENVIANDO queda bloqueado permanentemente para evitar el segundo intento.
            repository.mark_dispatching(record_id)
            try:
                result = client.send_authenticated(payload, token)
            except AivoError as error:
                _report_error(error)
                state = 'ERROR_AUTH' if error.auth_failure else (
                    'ERROR_HTTP' if error.functional_error or (error.http_status and error.http_status >= 300) else 'INCIERTO'
                )
                repository.finish(record_id, state, 'ENVIANDO', error.http_status, error.response_body, error)
                summary['errores'] += 1
                if error.auth_failure or error.account_blocked or error.http_status == 401:
                    return summary  # Detener todo el lote ante problemas de la cuenta.
                continue
            except Exception as error:
                # Tampoco se reenvía después de un error inesperado durante el POST.
                repository.finish(record_id, 'INCIERTO', 'ENVIANDO', error='Error inesperado durante el POST')
                raise OracleLogError(f'Envío {record_id} incierto; no repetirlo') from error
            repository.finish(
                record_id, 'ACEPTADO', 'ENVIANDO', result.status_code, result.body,
                error='Token renovado una vez antes de completar el envío' if result.auth_refreshes else None,
            )
            summary['aceptados'] += 1
    return summary
