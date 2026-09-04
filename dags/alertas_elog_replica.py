from __future__ import annotations

from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator


PY_APPS_DIR = '/opt/airflow/tareas/py_apps'


def choose_sync_mode(**context):
    full_sync = context['params'].get('full_sync')
    if isinstance(full_sync, str):
        full_sync = full_sync.strip().lower() in {'1', 'true', 'yes', 'si'}
    if bool(full_sync):
        return 'sync_full'
    interval_end = context['data_interval_end'].in_timezone('America/Lima')
    if interval_end.hour == 3 and interval_end.minute == 0:
        return 'sync_full'
    return 'sync_incremental'


DOC = """
## Réplica ClickHouse → Oracle

Replica `cgnat.collector_alerts` hacia `ALERTAS_ELOG` mediante `MERGE` por `ID`.
También registra cada cinco minutos los routers únicos de
`cgnat.huawei_cgn_nat_v2_YYYY_MM_DD` en `ROUTERS_ELOG`.
Lee los cuatro orígenes configurados en `DB_CH_ELOG_HOSTS`; las alarmas se
procesan por servidor y los routers se deduplican globalmente por `router_ip`.
Antes de replicar abre una conexión TCP al puerto ClickHouse de los cuatro
servidores. Si uno no responde, guarda en `ALERTAS_ELOG` la alarma
`Servidor Caido HOSTNAME IP`; usa un ID estable por IP para no duplicarla y la
marca `CLEARED` cuando el servidor vuelve a responder.

- Ejecución incremental cada 5 minutos: filas `ACTIVE` y cambios de las últimas
  `lookback_hours` horas.
- Sincronización completa automática diariamente a las 03:00 (America/Lima).
- Para la carga inicial, dispare manualmente el DAG con `full_sync=true`.
- Puede usar `dry_run=true` para leer y validar sin escribir Oracle.
- No elimina filas de Oracle; inserta nuevas y actualiza las existentes.
"""


with DAG(
    dag_id='alertas_elog_replica',
    description='Replica alertas CGNAT de ClickHouse hacia Oracle Smart',
    schedule='*/5 * * * *',
    start_date=pendulum.datetime(2026, 7, 16, tz='America/Lima'),
    catchup=False,
    max_active_runs=1,
    tags=['clickhouse', 'oracle', 'alertas', 'elog'],
    params={
        'full_sync': False,
        'dry_run': False,
        'lookback_hours': 48,
        'batch_size': 5000,
        'monitor_port': 8123,
        'tcp_timeout_seconds': 2,
    },
    doc_md=DOC,
) as dag:
    select_mode = BranchPythonOperator(
        task_id='select_sync_mode',
        python_callable=choose_sync_mode,
    )

    sync_incremental = BashOperator(
        task_id='sync_incremental',
        bash_command='python -m src.alertas_elog',
        cwd=PY_APPS_DIR,
        append_env=True,
        env={
            'ALERTAS_ELOG_FULL_SYNC': 'false',
            'ALERTAS_ELOG_DRY_RUN': '{{ params.dry_run }}',
            'ALERTAS_ELOG_LOOKBACK_HOURS': '{{ params.lookback_hours }}',
            'ALERTAS_ELOG_BATCH_SIZE': '{{ params.batch_size }}',
            'ALERTAS_ELOG_MONITOR_PORT': '{{ params.monitor_port }}',
            'ALERTAS_ELOG_TCP_TIMEOUT_SECONDS': (
                '{{ params.tcp_timeout_seconds }}'
            ),
        },
        retries=2,
        retry_delay=timedelta(minutes=2),
        execution_timeout=timedelta(hours=1),
    )

    sync_full = BashOperator(
        task_id='sync_full',
        bash_command='python -m src.alertas_elog --full-sync',
        cwd=PY_APPS_DIR,
        append_env=True,
        env={
            'ALERTAS_ELOG_DRY_RUN': '{{ params.dry_run }}',
            'ALERTAS_ELOG_LOOKBACK_HOURS': '{{ params.lookback_hours }}',
            'ALERTAS_ELOG_BATCH_SIZE': '{{ params.batch_size }}',
            'ALERTAS_ELOG_MONITOR_PORT': '{{ params.monitor_port }}',
            'ALERTAS_ELOG_TCP_TIMEOUT_SECONDS': (
                '{{ params.tcp_timeout_seconds }}'
            ),
        },
        retries=1,
        retry_delay=timedelta(minutes=5),
        execution_timeout=timedelta(hours=4),
    )

    select_mode >> [sync_incremental, sync_full]
