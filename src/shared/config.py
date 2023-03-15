import pytz

# BASE_DIR = 'C:/Users/E708412/Documents/desarrollo/alarmas/'
BASE_DIR = '/index1/tareas/proyectos_python/apps/py_apps/'
STORAGE_DIR = BASE_DIR+'files/'

TIMEZONE = 'America/Lima'

DTFORMAT_BY_ALIAS = {'dxd': '%Y-%m-%d', 'hxh': '%Y-%m-%d %H', 'mxm': '%Y-%m-%d %H:%M'}
TDINTERVAL_BY_ALIAS = {'dxd': {'days': 1}, 'hxh': {'hours': 1}, 'mxm': {'minutes': 1}}
