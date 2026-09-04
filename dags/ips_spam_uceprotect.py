from __future__ import annotations

from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator


PY_APPS_DIR = '/opt/airflow/tareas/py_apps'


DOC = """
## IPs Spam - UCEPROTECT hacia ClickHouse

Carga diariamente las listas UCEPROTECT Level 1, Level 2, Level 3,
Backscatter y Whitelist mediante rsync. La clasificación ASN se obtiene de
la tabla publicada en `l3charts.php`.

El proceso conserva únicamente el estado vigente. Cada fuente se carga primero
en tablas de preparación y se publica cuando terminó correctamente. Registra
insertados, actualizados, eliminados, registros sin cambios y errores en
`spam.UCEPRTC_AUDITORIA`.

- Horario: todos los días a las 06:00, zona `America/Lima`.
- Ejecución manual de una fuente: parámetro `source`.
- Descarga inicial forzada: parámetro `full_download=true`.
- No permite ejecuciones simultáneas.
"""


with DAG(
    dag_id='ips_spam_uceprotect',
    description='Carga UCEPROTECT hacia ClickHouse spam',
    schedule='0 6 * * *',
    start_date=pendulum.datetime(2026, 9, 4, tz='America/Lima'),
    catchup=False,
    max_active_runs=1,
    tags=['spam', 'uceprotect', 'clickhouse', 'rsync'],
    params={
        'source': 'all',
        'full_download': False,
    },
    doc_md=DOC,
) as dag:
    load_uceprotect = BashOperator(
        task_id='load_uceprotect',
        bash_command='python -m src.ips_spam',
        cwd=PY_APPS_DIR,
        append_env=True,
        env={
            'UCEPROTECT_SOURCE': '{{ params.source }}',
            'UCEPROTECT_FULL_DOWNLOAD': '{{ params.full_download }}',
        },
        retries=2,
        retry_delay=timedelta(minutes=10),
        execution_timeout=timedelta(hours=2),
    )
