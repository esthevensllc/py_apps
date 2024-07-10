from __future__ import annotations
import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator

PY_APPS_DIR = "/opt/airflow/tareas/py_apps"

with DAG(
    dag_id="pronatel_log_cleanup",
    schedule="55 4 * * 1",
    start_date=pendulum.datetime(2023, 5, 17, 9, tz="America/Lima"),
    catchup=False,
    tags=["logs", "pronatel"],
) as dag:
    task1 = BashOperator(
        task_id="cleanup-log",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.soporteclientes.logs.DepurarLogsPronatel",
    )
    task1
