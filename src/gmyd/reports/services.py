import requests
import datetime as dt
import json

import datetime as dt
from src.shared.config import STORAGE_DIR
from src.shared.carga.services import BaseCargaFromConfig

from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.gmyd.shared.services import LOAD_GMYD_FROM_CONFIG

class LoadGMyDFromConfig(BaseCargaFromConfig):
    def __init__(self, db, repository, sftp_service, control_carga_repo):
        super().__init__(db, repository, sftp_service, control_carga_repo)
        self.base_storage_dir = f"{STORAGE_DIR}gmyd"

    def _get_files_from_server(self, config, remote_dir, dt_fecha1, dt_fecha2):
        files = []
        str_date = dt_fecha1.strftime(config["file_date_format"])
        files.append({
            'file': f"{config['name']}_{str_date}.json",
            'path': config['work_dir'].replace("\n", "").replace("\t", "").split(",") if "," in config['work_dir'] else [config['work_dir']]
        })
        return files

    def _download_files(self, storage_dir, files_filtered):
        for file in files_filtered:
            filename = file['file']
            local_path_filename = f"{storage_dir}/{filename}"
            try:
                data = []
                for path in file['path']:
                    response = requests.get(f"http://172.19.84.74:3002{path}")
                    data = data + response.json()["data"]
                with open(local_path_filename, 'w') as content:
                    content.write(json.dumps(data))
            except Exception as e:
                raise e

    def _get_data_from_csv(self, fields_config, filename, skip_lines=0, date_of_file=None, env={}):
        fields_to_reload = list(filter(lambda f: f['to_reload'] is not None, fields_config))
        data = []

        with open(f"{filename}", newline='', encoding='UTF-8') as file:
            file_data = json.loads(file.read())
            counter = 0
            for row in file_data:
                counter = counter + 1
                row_to_add = {}
                for field in fields_config:
                    value = None
                    try:
                        value = row[field["src_fieldname"]]
                        if field.get('map_with') is not None:
                            value = eval(f"f\"{field['map_with']}\"")
                        if value == '':
                            value = None
                        row_to_add[field["fieldname"]] = value
                    except BaseException as e:
                        print(row)
                        print(f"line: {counter}, field: {field['fieldname']}, value: '{value}'")
                        raise e
                data.append(row_to_add)
        
        min_date = None
        max_date = None
        for field in fields_to_reload:
            date_fields = list(map(lambda r: r[field["fieldname"]], data))
            min_date = min(date_fields)
            max_date = max(date_fields)
            break

        if env["str_filedate"] != min_date or env["str_filedate"] != max_date:
            raise Exception(f"Los datos obtenidos ({min_date}, {max_date}) no corresponden a la fecha {env['str_filedate']}")
        return data


class GMyDEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, repository, sftp_service, control_carga_repo, queue_service):
        super().__init__(sftp_service, control_carga_repo, queue_service)
        self.repository = repository
        self.speedtest_api = sftp_service

    def get_cargas_config(self, group_id=None):
        return self.repository.get()

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        fields = self.repository.get_fields_by_id(config["id"])
        fields_to_reload = list(filter(lambda f: f['to_reload'] is not None, fields))

        first_work_dir = config['work_dir'].replace("\n", "").replace("\t", "").split(",")[0] if "," in config['work_dir'] else config['work_dir']
        response = requests.get(f"http://172.19.84.74:3002{first_work_dir}")
        file_data = response.json()["data"]
        data = []
        counter = 0
        env = {
            "str_filedate": dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        for row in file_data:
            counter = counter + 1
            row_to_add = {}
            for field in fields:
                value = None
                try:
                    value = row[field["src_fieldname"]]
                    if field.get('map_with') is not None:
                        value = eval(f"f\"{field['map_with']}\"")
                    if value == '':
                        value = None
                    row_to_add[field["fieldname"]] = value
                except BaseException as e:
                    print(row)
                    print(f"line: {counter}, field: {field['fieldname']}, value: '{value}'")
                    raise e
            data.append(row_to_add)

        str_date = ""
        for field in fields_to_reload:
            date_fields = list(map(lambda r: r[field["fieldname"]], data))
            min_date = min(date_fields)
            max_date = max(date_fields)
            str_date = dt.datetime.strptime(min_date, '%Y-%m-%d %H:%M:%S').strftime(config["file_date_format"])
            break

        return [{
            'file': f"{config['name']}_{str_date}.json",
            'path': config["work_dir"]
        }]


class GMyDEventConsumerFromConfig(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service, repository):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.1
        self.repository = repository
        self.loop = False
        self.config_by_queueid = {}

    def execute(self, group_id=None):
        cargas = []
        if group_id == None:
            cargas = self.repository.get()
        else:
            cargas = self.repository.get_by_group_id(group_id)

        if len(cargas) == 0:
            raise Exception(f"No existen cargas")
        
        for row in cargas:
            self.config_by_queueid[row["queue_id"]] = row

        def map_event(event):
            event['msg_body']['config_id'] = self.config_by_queueid[event['queue_id']]["id"]
            return event

        for row in cargas:
            queue_id = row["queue_id"]
            self.queue_handlers[queue_id] = {'handler': LOAD_GMYD_FROM_CONFIG, 'callback': lambda s, e: s.event_handler(map_event(e))}

        self.queue_ids = list(self.queue_handlers)
        super().execute()
