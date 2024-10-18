from __future__ import annotations

import datetime

import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
import sys

PY_APPS_DIR = "/opt/airflow/tareas/py_apps"
sys.path.append(PY_APPS_DIR)

with DAG(
    dag_id="pm_batch",
    schedule="*/5 * * * *",
    start_date=pendulum.datetime(2023, 5, 17, 9, tz="America/Lima"),
    catchup=False,
    tags=["stats", "pm", "prod"],
) as dag:
    task1 = BashOperator(
        task_id="event_producer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.pm.carga.PMEventBatchProducer",
    )
    task2 = BashOperator(
        task_id="event_consumer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.pm.carga.PMEventBatchConsumer",
    )
    task3 = BashOperator(
        task_id="event_handlers",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.control_carga.ora_handlers.ResumenEventConsumer pm_hxh",
    )
    [task1, task2] >> task3