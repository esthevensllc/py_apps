from __future__ import annotations
import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator

PY_APPS_DIR = "/opt/airflow/tareas/py_apps"

with DAG(
    dag_id="factibilidad_fija",
    schedule="*/5 * * * *",
    start_date=pendulum.datetime(2023, 5, 17, 9, tz="America/Lima"),
    catchup=False,
    tags=["stats", "factibilidad_fija", "prod"],
) as dag:
    task1 = BashOperator(
        task_id="search_coordinates",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.factibilidad_fija.sots.UpdateInfoSots",
    )
    task1
