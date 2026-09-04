from __future__ import annotations

from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator


PY_APPS_DIR = "/opt/airflow/tareas/py_apps"
DOC = """
## Recarga histórica NCE

El DAG es manual y procesa el intervalo `[start, end)`.

- Ejecute primero con `dry_run=true` para validar el manifiesto.
- Ejecute luego con `dry_run=false` para cargar Oracle.
- `strict=true` detiene la carga si falta algún timestamp esperado.
- `emit_success_events=true` ejecuta `SP_NCE_FILE_SUCCESS` tras cada grupo.

Las rutas se resuelven como
`/hfs_public/nbi/text/pfm_output/YYYYMMDD/YYYYMMDD`.
"""


with DAG(
    dag_id="nce_recarga",
    description="Recarga manual de archivos históricos NCE desde SFTP hacia Oracle",
    schedule=None,
    start_date=pendulum.datetime(2026, 7, 1, tz="America/Lima"),
    catchup=False,
    tags=["nce", "recarga", "manual"],
    max_active_runs=1,
    doc_md=DOC,
    params={
        "start": "2026-07-12 21:00",
        "end": "2026-07-13 06:00",
        "dry_run": True,
        "strict": True,
        "emit_success_events": True,
    },
) as dag:
    reload_files = BashOperator(
        task_id="validate_or_reload_nce_files",
        bash_command="python -m src.nce_recarga",
        cwd=PY_APPS_DIR,
        append_env=True,
        env={
            "NCE_RECARGA_START": "{{ params.start }}",
            "NCE_RECARGA_END": "{{ params.end }}",
            "NCE_RECARGA_DRY_RUN": "{{ params.dry_run }}",
            "NCE_RECARGA_STRICT": "{{ params.strict }}",
            "NCE_RECARGA_EMIT_SUCCESS_EVENTS": (
                "{{ params.emit_success_events }}"
            ),
        },
        priority_weight=100,
        execution_timeout=timedelta(hours=12),
        retries=1,
        retry_delay=timedelta(minutes=5),
    )
