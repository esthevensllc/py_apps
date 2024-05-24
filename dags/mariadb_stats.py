from __future__ import annotations
import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator

PY_APPS_DIR = "/opt/airflow/tareas/py_apps"

with DAG(
    dag_id="mariadb_stats",
    schedule="*/10 * * * *",
    start_date=pendulum.datetime(2023, 5, 17, 9, tz="America/Lima"),
    catchup=False,
    tags=["stats", "mariadb", "prod"],
) as dag:
    task1 = BashOperator(
        task_id="event_producer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.mariadb.reports.MariadbEventProducer alarms",
    )
    task2 = BashOperator(
        task_id="event_consumer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.mariadb.reports.MariadbEventConsumer alarms",
    )
    task1 >> task2
