from __future__ import annotations
import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator

PY_APPS_DIR = "/opt/airflow/tareas/py_apps"

with DAG(
    dag_id="cdr_stats",
    schedule="*/5 * * * *",
    start_date=pendulum.datetime(2023, 5, 17, 9, tz="America/Lima"),
    catchup=False,
    tags=["stats", "cdr", "prod"],
    max_active_runs=1,
) as dag:
    task1 = BashOperator(
        task_id="cdr_producer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.cdr.reports.CdrEventProducer",
    )
    task2 = BashOperator(
        task_id="cdr_consumer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.cdr.reports.CdrEventConsumer",
    )
    task1 >> task2
