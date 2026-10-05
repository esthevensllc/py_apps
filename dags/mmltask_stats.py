from __future__ import annotations
import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator
import sys

PY_APPS_DIR = "/opt/airflow/tareas/py_apps"
sys.path.append(PY_APPS_DIR)

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
    task1 >> task2

