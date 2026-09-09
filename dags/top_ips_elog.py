from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator


PY_APPS_DIR = '/opt/airflow/tareas/py_apps'

DOC = """
## Top IPs CGNAT hacia ClickHouse elog

Ejecuta cuatro consultas de top de uso sobre cada uno de los cuatro nodos
ClickHouse CGNAT. Procesa las tablas `huawei_cgn_nat_v2_YYYY_MM_DD` del día
anterior en America/Lima y guarda los resultados en `elog`.

Cada tabla destino conserva `fecha_proceso` y `nodo_origen`; antes de insertar,
el proceso elimina solo los registros de esa fecha. Así, los reintentos no
duplican datos. Si una tabla no existe, el proceso la crea con los tipos de la
tabla fuente.

- Horario: todos los días a las 05:00, zona America/Lima.
- Registra únicamente los pasos del proceso y los errores en el log de Airflow.
- No permite ejecuciones simultáneas.
"""

with DAG(
    dag_id='top_ips_elog',
    description='Carga top IPs CGNAT de cuatro nodos hacia ClickHouse elog',
    schedule='0 5 * * *',
    start_date=pendulum.datetime(2026, 9, 9, tz='America/Lima'),
    catchup=False,
    max_active_runs=1,
    tags=['clickhouse', 'elog', 'cgnat', 'top-ips'],
    doc_md=DOC,
) as dag:
    load_top_ips = BashOperator(
        task_id='load_top_ips',
        bash_command='python -m src.top_ips_elog',
        cwd=PY_APPS_DIR,
        append_env=True,
        env={'TOP_IPS_PROCESS_DATE': "{{ data_interval_end.in_timezone('America/Lima').subtract(days=1).format('YYYY-MM-DD') }}"},
        retries=2,
        retry_delay=timedelta(minutes=10),
        execution_timeout=timedelta(hours=4),
    )
