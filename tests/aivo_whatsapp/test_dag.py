import datetime as dt
import runpy
import sys
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch


class DagDefinitionTest(unittest.TestCase):
    def test_dag_schedule_and_execution_preserve_duplicate_controls(self):
        captured = {}

        class Dag:
            def __init__(self, **kwargs):
                captured['dag'] = kwargs
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False

        class Operator:
            def __init__(self, **kwargs):
                captured['task'] = kwargs

        airflow = ModuleType('airflow')
        airflow.DAG = Dag
        bash = ModuleType('airflow.operators.bash')
        bash.BashOperator = Operator
        pendulum = ModuleType('pendulum')
        def lima_datetime(year, month, day, tz):
            self.assertEqual(tz, 'America/Lima')
            return dt.datetime(year, month, day, tzinfo=dt.timezone(dt.timedelta(hours=-5)))
        pendulum.datetime = lima_datetime
        modules = {'airflow': airflow, 'airflow.operators': ModuleType('airflow.operators'),
                   'airflow.operators.bash': bash, 'pendulum': pendulum}
        path = Path(__file__).resolve().parents[2] / 'dags' / 'aivo_whatsapp.py'
        with patch.dict(sys.modules, modules), patch('requests.post') as post:
            runpy.run_path(str(path))
        post.assert_not_called()
        dag = captured['dag']
        task = captured['task']
        self.assertEqual(dag['schedule'], '*/15 * * * *')
        self.assertEqual(dag['max_active_runs'], 1)
        self.assertFalse(dag['catchup'])
        self.assertTrue(dag['is_paused_upon_creation'])
        self.assertEqual(task['retries'], 0)
        self.assertEqual(task['execution_timeout'], dt.timedelta(minutes=14))
        self.assertEqual(task['cwd'], '/opt/airflow/tareas/py_apps')
        self.assertIn('--from-oracle', task['bash_command'])
        self.assertIn('exec python3 -m src.aivo_whatsapp', task['bash_command'])
        self.assertNotIn('--to', task['bash_command'])
        self.assertNotIn('--test-to', task['bash_command'])
        self.assertNotIn('--test-id', task['bash_command'])
