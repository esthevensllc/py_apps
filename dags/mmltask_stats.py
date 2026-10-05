from __future__ import annotations
import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import sys

PY_APPS_DIR = "/opt/airflow/tareas/py_apps"
sys.path.append(PY_APPS_DIR)


def execute_vswr_procedure():
    from dotenv import load_dotenv
    from src.shared.database.OracleDB import OracleDB

    load_dotenv(f"{PY_APPS_DIR}/.env")
    oracle = OracleDB()
    try:
        oracle.query("begin pk_carga_vswr.SP_CARGA_TOTAL_VSWR; end;", {})
    finally:
        oracle.close()


with DAG(
    dag_id="mmltask_stats",
    schedule="15 * * * *",
    start_date=pendulum.datetime(2023, 5, 17, 9, tz="America/Lima"),
    catchup=False,
    tags=["stats", "mmltask", "prod"],
    max_active_runs=1
) as dag:
    task1 = BashOperator(
        task_id="event_producer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.mmltask.reports.MmltaskEventProducer",
    )
    task2 = BashOperator(
        task_id="event_consumer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.mmltask.reports.MmltaskEventConsumer",
    )
    rss_reporte_diario_vswr = PythonOperator(
        task_id="rss_reporte_diario_vswr",
        python_callable=execute_vswr_procedure,
    )
    task1 >> task2 >> rss_reporte_diario_vswr

