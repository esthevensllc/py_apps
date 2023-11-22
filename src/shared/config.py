import pytz
from os import getenv

BASE_DIR = getenv("PYAPP_BASE_DIR", '/index1/tareas/proyectos_python/apps/py_apps/')
STORAGE_DIR = getenv("PYAPP_STORAGE_DIR", BASE_DIR+"files/")
STORAGE_TEMP_DIR = getenv("PYAPP_STORAGE_TEMP_DIR", STORAGE_DIR+"temp")

TIMEZONE = 'America/Lima'

DTFORMAT_BY_ALIAS = {'dxd': '%Y-%m-%d', 'hxh': '%Y-%m-%d %H', 'mxm': '%Y-%m-%d %H:%M'}
TDINTERVAL_BY_ALIAS = {'dxd': {'days': 1}, 'hxh': {'hours': 1}, 'mxm': {'minutes': 1}}
