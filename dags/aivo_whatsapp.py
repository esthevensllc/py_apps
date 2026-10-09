from __future__ import annotations

from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator


PY_APPS_DIR = '/opt/airflow/tareas/py_apps'

with DAG(
    dag_id='aivo_whatsapp',
    description='Envía diagnóstico y solución de averías a los celulares de Oracle',
    schedule='*/15 * * * *',
    start_date=pendulum.datetime(2026, 10, 9, tz='America/Lima'),
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=True,
    tags=['oracle', 'whatsapp', 'aivo'],
    params={'fecha_desde': '2026-10-08', 'batch_size': 100, 'dry_run': False},
    doc_md='''
Ejecuta ambas plantillas cada 15 minutos, en America/Lima.
Aplicar primero sql/migrate_aivo_whatsapp_production.sql y luego activar el DAG.
Cada lote consulta candidatos aún no reservados en PRODUCCION.
Mantiene el log por cliente, fecha de inicio y plantilla; no reintenta reservas.
dry_run=true consulta y muestra los mensajes sin reservar ni llamar a Aivo.
''',
) as dag:
    send_whatsapp = BashOperator(
        task_id='send_whatsapp',
        bash_command='''
args=(--from-oracle --fecha-desde "$AIVO_FECHA_DESDE" --limit "$AIVO_BATCH_SIZE")
if [ "$AIVO_DRY_RUN" = "true" ]; then args+=(--dry-run); fi
exec python3 -m src.aivo_whatsapp "${args[@]}"
''',
        cwd=PY_APPS_DIR,
        append_env=True,
        env={
            'AIVO_FECHA_DESDE': '{{ params.fecha_desde }}',
            'AIVO_BATCH_SIZE': '{{ params.batch_size }}',
            'AIVO_DRY_RUN': '{{ params.dry_run | lower }}',
        },
        retries=0,
        execution_timeout=timedelta(minutes=14),
        do_xcom_push=False,
    )
