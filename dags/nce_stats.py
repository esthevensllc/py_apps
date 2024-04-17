from __future__ import annotations
import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator

PY_APPS_DIR = "/opt/airflow/tareas/py_apps"

with DAG(
    dag_id="nce_stats",
    schedule="0,15,30,45 * * * *",
    start_date=pendulum.datetime(2023, 5, 17, 9, tz="America/Lima"),
    catchup=False,
    tags=["stats", "nce", "prod"],
) as dag:
    task1 = BashOperator(
        task_id="nce_producer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.nce.cargas.services.CargasEventProducer",
    )
    task2 = BashOperator(
        task_id="nce_consumer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.nce.shared.services.nce_async_event_consumer",
    )
    task1 >> task2
