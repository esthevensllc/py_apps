"""Publica y consume las alarmas GDE cada cinco minutos."""

from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator


PY_APPS_DIR = "/opt/airflow/tareas/py_apps"

with DAG(
    dag_id="gde_alarm",
    schedule="*/5 * * * *",
    start_date=pendulum.datetime(2023, 5, 17, 9, tz="America/Lima"),
    catchup=False,
    tags=["stats", "gde", "prod"],
    max_active_runs=1,
) as dag:
    producer = BashOperator(
        task_id="event_producer",
        bash_command=(
            "python main_unique.py "
            "src.gde.stats.GdeEventProducerFromConfig"
        ),
        cwd=PY_APPS_DIR,
    )
    consumer = BashOperator(
        task_id="event_consumer",
        bash_command=(
            "python main_unique.py "
            "src.gde.stats.GdeEventConsumerFromConfig"
        ),
        cwd=PY_APPS_DIR,
    )

    producer >> consumer
