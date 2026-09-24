from __future__ import annotations

from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator


PY_APPS_DIR = '/opt/airflow/tareas/py_apps'


DOC = """
## IPs Spam - UCEPROTECT hacia ClickHouse

Carga diariamente las listas UCEPROTECT Level 1, Level 2, Level 3,
Backscatter, Whitelist y la clasificación ASN. Primero recolecta una
instantánea validada desde el servidor puente `192.168.195.247` por SFTP;
luego ejecuta el cargador existente en ClickHouse.

El proceso conserva únicamente el estado vigente. Cada fuente se carga primero
en tablas de preparación y se publica cuando terminó correctamente. Registra
insertados, actualizados, eliminados, registros sin cambios y errores en
`spam.UCEPRTC_AUDITORIA`.

- Horario: todos los días a las 06:00, zona `America/Lima`.
- El servidor puente debe terminar su descarga antes de las 06:00.
- Ejecución manual de una fuente: parámetro `source`.
- `10.96.167.139` no descarga las fuentes desde Internet.
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
    },
    doc_md=DOC,
) as dag:
    collect_uceprotect_bridge = BashOperator(
        task_id='collect_uceprotect_bridge',
        bash_command='python -m src.ips_spam --collect-bridge',
        cwd=PY_APPS_DIR,
        append_env=True,
        retries=2,
        retry_delay=timedelta(minutes=5),
        execution_timeout=timedelta(minutes=15),
    )

    load_uceprotect = BashOperator(
        task_id='load_uceprotect',
        bash_command='python -m src.ips_spam --skip-download',
        cwd=PY_APPS_DIR,
        append_env=True,
        env={
            'UCEPROTECT_SOURCE': '{{ params.source }}',
        },
        retries=2,
        retry_delay=timedelta(minutes=10),
        execution_timeout=timedelta(hours=2),
    )

    collect_uceprotect_bridge >> load_uceprotect
