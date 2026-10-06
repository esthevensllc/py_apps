"""Comparte el límite GDE entre procesos que usan el mismo almacenamiento."""

from contextlib import contextmanager
import os
from pathlib import Path
import time


class GdeRateLimiter:
    INTERVAL_SECONDS = 21

    def __init__(self, path=None):
        storage = os.getenv('PYAPP_STORAGE_DIR') or (
            os.getenv('PYAPP_BASE_DIR', '/index1/tareas/proyectos_python/apps/py_apps/')
            + 'files/'
        )
        self.path = Path(path or os.getenv('PYAPP_GDE_RATE_LIMIT_FILE')
                         or str(Path(storage) / 'gde' / '.api_rate_limit'))

    @contextmanager
    def request_slot(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('a+b') as state:
            if os.name == 'nt':
                import msvcrt
                while True:
                    try:
                        state.seek(0)
                        msvcrt.locking(state.fileno(), msvcrt.LK_NBLCK, 1)
                        break
                    except OSError:
                        time.sleep(0.1)
            else:
                import fcntl
                fcntl.flock(state.fileno(), fcntl.LOCK_EX)
            try:
                state.seek(0)
                stored = state.read().decode('ascii').strip()
                previous = float(stored) if stored else 0
                delay = self.INTERVAL_SECONDS - (time.time() - previous)
                if delay > 0:
                    print(f'GDE_API_RATE_WAIT seconds={delay:.1f}', flush=True)
                    time.sleep(delay)
                state.seek(0)
                state.truncate()
                state.write(str(time.time()).encode('ascii'))
                state.flush()
                # Hold the lock during HTTP so requests remain sequential.
                yield
            finally:
                if os.name == 'nt':
                    state.seek(0)
                    msvcrt.locking(state.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(state.fileno(), fcntl.LOCK_UN)
