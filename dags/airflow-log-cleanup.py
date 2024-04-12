from __future__ import annotations
import pendulum

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import sys
import os
import re
import datetime as dt
from shutil import rmtree

MAX_LOG_DAYS=7

def delete_logs():
    logs_dir="/opt/airflow/logs"
    str_pattern = ".+__([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}\:[0-9]{2}\:[0-9]{2}).+"
    pattern = re.compile(str_pattern)

    min_date = dt.datetime.now() - dt.timedelta(days=MAX_LOG_DAYS)

    dags = list(filter(lambda dag_dir: "dag_id=" in dag_dir, os.listdir(logs_dir)))

    for dag in dags:
        logs = os.listdir(f"{logs_dir}/{dag}")
        counter = 0
        for log in logs:
            result = pattern.match(log)
            if result is not None:
                str_datetime = result.group(1)
                dt_dag_log = dt.datetime.strptime(str_datetime, "%Y-%m-%dT%H:%M:%S")
                if min_date > dt_dag_log:
                    counter = counter + 1
                    rmtree(f"{logs_dir}/{dag}/{log}")
        print(f"{dag}({len(logs)}): {counter}")


with DAG(
    dag_id="airflow-log-cleanup",
    schedule="0 5 * * *",
    start_date=pendulum.datetime(2023, 5, 17, 9, tz="America/Lima"),
    catchup=False,
    tags=["airflow", "prod"],
    default_args={"retries": 1}
) as dag:
    task1 = PythonOperator(
        task_id="log-cleanup-worker",
        python_callable=delete_logs
    )
    task1