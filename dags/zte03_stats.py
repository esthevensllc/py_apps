from __future__ import annotations
import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator

PY_APPS_DIR = "/opt/airflow/tareas/py_apps"

with DAG(
    dag_id="zte03_stats",
    schedule="*/15 * * * *",
    start_date=pendulum.datetime(2023, 5, 17, 9, tz="America/Lima"),
    catchup=False,
    tags=["stats", "zte", "prod"],
) as dag:
    task1 = BashOperator(
        task_id="zte_producer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.zte.stats.ZTEEventStatsProducerFromConfig",
    )
    task2 = BashOperator(
        task_id="zte_consumer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.zte.stats.ZTEEventStatsConsumerFromConfig",
    )
    task1 >> task2
