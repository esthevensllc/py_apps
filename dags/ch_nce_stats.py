from __future__ import annotations
import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator

PY_APPS_DIR = "/opt/airflow/tareas/py_apps"

with DAG(
    dag_id="ch_nce_stats",
    schedule="2,17,32,47 * * * *",
    start_date=pendulum.datetime(2023, 5, 17, 9, tz="America/Lima"),
    catchup=False,
    tags=["stats", "nce", "prod"],
) as dag:
    task1 = BashOperator(
        task_id="ch_nce_producer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.nce.cargas.services.ClikHouseCargasEventProducer",
    )
    task2 = BashOperator(
        task_id="ch_nce_consumer",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.nce.shared.services.ch_nce_async_event_consumer",
    )
    task3 = BashOperator(
        task_id="ch_nce_handlers",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.control_carga.ora_handlers.ResumenEventConsumer ch_ncemxm",
    )
    task1 >> task2 >> task3
