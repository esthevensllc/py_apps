from __future__ import annotations
import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator

PY_APPS_DIR = "/opt/airflow/tareas/py_apps"

with DAG(
    dag_id="nce_alarm_tx",
    schedule="*/5 * * * *",
    start_date=pendulum.datetime(2023, 5, 17, 9, tz="America/Lima"),
    catchup=False,
    tags=["alarms", "nce", "prod"],
) as dag:
    task1 = BashOperator(
        task_id="nce_producer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.nce.alarmas.NCEEventProducer alarm_tx",
    )
    task2 = BashOperator(
        task_id="nce_consumer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.nce.alarmas.NCEEventConsumerFromConfig alarm_tx",
    )
    [task1, task2]
