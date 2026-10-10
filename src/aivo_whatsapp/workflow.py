from __future__ import annotations

import datetime as dt

from .models import Notification
from .repository import OracleLogError
from .service import AivoError, TEMPLATES


def run_batch(repository, client, template_name=None, fecha_desde=dt.datetime(2026, 10, 8), limit=100, dry_run=False):
    """Punto de entrada para una futura tarea Airflow. Sin reenvíos ni recuperación automática."""
    if template_name is not None and template_name not in TEMPLATES:
        raise ValueError('Plantilla no soportada')
    if not 1 <= limit <= 1000:
        raise ValueError('El límite debe estar entre 1 y 1000')
    repository.validate_safety()
    summary = {'candidatos': 0, 'aceptados': 0, 'bloqueados': 0, 'invalidos': 0, 'errores': 0, 'vista_previa': []}
    templates = (template_name,) if template_name else tuple(TEMPLATES)
    for template in templates:
        for row in repository.fetch_candidates(template, fecha_desde, limit):
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
                repository.finish(record_id, 'ERROR_AUTH', 'RESERVADO', error=error, http_status=error.http_status)
                summary['errores'] += 1
                continue
            # Si este commit falla, no se ejecuta el POST. Si el proceso muere después,
            # ENVIANDO queda bloqueado permanentemente para evitar el segundo intento.
            repository.mark_dispatching(record_id)
            try:
                result = client.send_authenticated(payload, token)
            except AivoError as error:
                state = 'ERROR_HTTP' if error.http_status and error.http_status >= 300 else 'INCIERTO'
                repository.finish(record_id, state, 'ENVIANDO', error.http_status, error.response_body, error)
                summary['errores'] += 1
                continue
            except Exception as error:
                # Tampoco se reenvía después de un error inesperado durante el POST.
                repository.finish(record_id, 'INCIERTO', 'ENVIANDO', error='Error inesperado durante el POST')
                raise OracleLogError(f'Envío {record_id} incierto; no repetirlo') from error
            repository.finish(record_id, 'ACEPTADO', 'ENVIANDO', result.status_code, result.body)
            summary['aceptados'] += 1
    return summary
