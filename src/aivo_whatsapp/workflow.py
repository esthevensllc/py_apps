from __future__ import annotations

import logging
import uuid
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
    summary = {'id_ejecucion': str(uuid.uuid4()), 'candidatos': 0, 'aceptados': 0, 'bloqueados': 0, 'invalidos': 0, 'errores': 0, 'vista_previa': []}
    try:
        with (nullcontext() if dry_run else client.account_session()):
            return _send_batch(repository, client, template_name, limit, dry_run, summary)
    except Exception as error:
        if not summary['aceptados']:
            raise
        # Conservar los aceptados confirmados si falla después la consulta del
        # siguiente grupo, el log o el cierre de la conexión de cuenta. Se detiene
        # el lote: este resultado parcial no autoriza reintentar ningún mensaje.
        summary['errores'] += 1
        summary['interrumpido'] = True
        summary['error_proceso'] = (
            str(error) if isinstance(error, (AivoError, OracleLogError, ValueError, OSError))
            else f'Error inesperado: {type(error).__name__}'
        )
        logger.error('Lote Aivo interrumpido con %s aceptados: %s', summary['aceptados'], summary['error_proceso'])
        return summary


def _send_batch(repository, client, template_name, limit, dry_run, summary):
    templates = (template_name,) if template_name else tuple(TEMPLATES)
    for template in templates:
        for row in repository.fetch_candidates(template, limit):
            summary['candidatos'] += 1
            try:
                notification = Notification.from_row(template, row)
                payload = repository.build_payload(notification)
            except ValueError as error:
                summary['invalidos'] += 1
                record_id = 'vista_previa' if dry_run else 'sin_confirmar'
                try:
                    if not dry_run:
                        record_id = repository.log_invalid(summary['id_ejecucion'], template, row, error)
                finally:
                    logger.warning('INVALIDO ejecución=%s registro=%s plantilla=%s incidencia=%r motivo=%s%s',
                                   summary['id_ejecucion'], record_id, template,
                                   str(row.get('incidencia'))[:128], error,
                                   ' (sin persistencia por --dry-run)' if dry_run else '')
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
