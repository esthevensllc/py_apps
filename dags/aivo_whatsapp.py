from __future__ import annotations

from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator


PY_APPS_DIR = '/opt/airflow/tareas/py_apps'

with DAG(
    dag_id='aivo_whatsapp',
    description='Envía diagnóstico y solución de averías a los celulares de Oracle',
    schedule='*/15 8-22 * * *',
    start_date=pendulum.datetime(2026, 10, 9, tz='America/Lima'),
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=True,
    tags=['oracle', 'whatsapp', 'aivo'],
    params={'batch_size': 100, 'dry_run': False},
    doc_md='''
Ejecuta ambas plantillas cada 15 minutos, de 08:00 a 22:45 en America/Lima.
Diagnóstico consulta las últimas 24 horas mediante SYSDATE - 1 de Oracle.
Aplicar primero sql/migrate_aivo_whatsapp_production.sql y luego activar el DAG.
Crear sql/create_aivo_auth_cache.sql y configurar AIVO_TOKEN_ENCRYPTION_KEY.
Crear sql/create_aivo_audit_logs.sql para historial de autenticación y candidatos inválidos.
Reutiliza el bearer cifrado entre ejecuciones y renueva preventivamente a las 9 horas.
UserBlockedException detiene la cuenta; sin reintentos consecutivos de /auth.
Cada lote consulta candidatos aún no reservados en PRODUCCION.
Mantiene el log por cliente, inicio y plantilla; no repite envíos inciertos.
Recupera fallos de autenticación solo si no hubo POST de mensaje (intentos=0).
Con al menos un mensaje aceptado, termina correctamente aunque existan incidencias.
Datos inválidos, duplicados y ausencia de pendientes son omisiones, no fallos.
Falla si hay errores de ejecución/envío y no se confirmó ningún mensaje aceptado.
dry_run=true consulta y muestra los mensajes sin reservar ni llamar a Aivo.
''',
) as dag:
    send_whatsapp = BashOperator(
        task_id='send_whatsapp',
        bash_command='''
args=(--from-oracle --limit "$AIVO_BATCH_SIZE")
if [ "$AIVO_DRY_RUN" = "true" ]; then args+=(--dry-run); fi
exec python3 -m src.aivo_whatsapp "${args[@]}"
''',
        cwd=PY_APPS_DIR,
        append_env=True,
        env={
            'AIVO_BATCH_SIZE': '{{ params.batch_size }}',
            'AIVO_DRY_RUN': '{{ params.dry_run | lower }}',
        },
        retries=0,
        execution_timeout=timedelta(minutes=14),
        do_xcom_push=False,
    )
