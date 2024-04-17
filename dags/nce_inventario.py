from __future__ import annotations
import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator

PY_APPS_DIR = "/opt/airflow/tareas/py_apps"

with DAG(
    dag_id="nce_inventario",
    schedule="0 * * * *",
    start_date=pendulum.datetime(2023, 5, 17, 9, tz="America/Lima"),
    catchup=False,
    tags=["inventario", "nce", "prod"],
) as dag:
    task1 = BashOperator(
        task_id="nce_producer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.nce.inventario.NCEInventarioEventProducer",
    )
    task2 = BashOperator(
        task_id="nce_consumer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.nce.inventario.NCEInventarioEventConsumerFromConfig",
    )
    task1 >> task2
