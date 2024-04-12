from __future__ import annotations
import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator

PY_APPS_DIR = "/opt/airflow/tareas/py_apps"

with DAG(
    dag_id="arbor_inventario",
    schedule="15 * * * *",
    start_date=pendulum.datetime(2023, 5, 17, 9, tz="America/Lima"),
    catchup=False,
    tags=["stats", "apic", "prod"],
    default_args={"retries": 1}
) as dag:
    task1 = BashOperator(
        task_id="LoadMitigations",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py arbor_os.mitigations.LoadMitigations",
    )
    task2 = BashOperator(
        task_id="ReloadManagedObject",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py arbor_os.managed_object.ReloadManagedObject",
    )
    task1 >> task2
