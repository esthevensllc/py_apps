import os
import sys
import datetime
import psutil
import re
from src.shared.app.AppContainer import AppContainer

service_to_exec = sys.argv[1]

start_time = datetime.datetime.now()

app_container = AppContainer()

def __get_process():
    process = {}
    keys = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline', 'create_time']):
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'username', 'cmdline', 'create_time'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        else:
            start_time = datetime.datetime.fromtimestamp(pinfo['create_time']).strftime("%Y%m%d%H%M%S")
            pinfo['cmdline'] = " ".join(pinfo["cmdline"]) if pinfo["cmdline"] is not None else None
            pinfo['create_time'] = start_time
            pinfo['end_time'] = None
            process[pinfo["pid"]] = pinfo
            keys.append(pinfo["pid"])
    return process, keys

def process_is_running(service):
    is_running = False
    process, keys = __get_process()
    pattern = re.compile(f".*{service}.*")
    current_pid = os.getpid()
    for pid in keys:
        # if service in f'{process[pid]["cmdline"]}':
        if process[pid]["cmdline"] is not None:
            if pattern.match(f'{process[pid]["cmdline"]}') is not None and pid != current_pid:
                print("proccess is already running")
                print(process[pid])
                is_running = True
                break
    return is_running

try:
    def get_params():
        args = sys.argv.copy()
        if len(args) > 2:
            return args[2:len(args)]
        return []

    extra_params = get_params()

    script = f".py {service_to_exec}"
    if len(extra_params) > 0:
        script = f"{script} {' '.join(extra_params)}"
    print(script)

    is_running = process_is_running(script)
    if not is_running:
        service = app_container.getInstance(service_to_exec)
        service.execute(*extra_params)
except BaseException as error:
    import traceback
    notification_service = app_container.getInstance('notification_service')
    subject = f"Error en la ejecucion de {service_to_exec}"
    message = f"Se presento el siguiente problema: {error}\n" + traceback.format_exc()
    if len(message) > 4000:
        message = message[0:4000]
    notification_service.send_notification(subject, message, 'ALARMA_CARGAS')
    raise error

app_container.close_connections()

end_time = datetime.datetime.now()
print("Fecha (inicio - fin) ejecucion ({} - {})".format(start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S')))