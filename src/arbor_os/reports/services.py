import datetime as dt
import re
import json
import pytz
from src.shared.config import STORAGE_DIR, TIMEZONE
from src.shared.carga.services import BaseCargaFromConfig

from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.arbor_os.shared.services import LOAD_ARBOR_FROM_CONFIG

class LoadArborFromConfig(BaseCargaFromConfig):
    def __init__(self, db, repository, sftp_service, control_carga_repo):
        super().__init__(db, repository, sftp_service, control_carga_repo)
        self.arbor_api = sftp_service
        self.base_storage_dir = f"{STORAGE_DIR}arbor"
        self.tzlocal = pytz.timezone(TIMEZONE)

    def _get_files_from_server(self, config, remote_dir, dt_fecha1, dt_fecha2):
        files = []
        pattern = re.compile(config['file_pattern'])
        dt_recorrido = dt_fecha1
        timedelta = dt.timedelta(**json.loads(config["loop_time"]))
        while dt_recorrido.strftime(config["file_date_format"]) < dt_fecha2.strftime(config["file_date_format"]):
            next_date = dt_recorrido + timedelta
            str_date = dt_recorrido.strftime(config["file_date_format"])
            files.append({
                'file': f"{config['name']}_{str_date}.json",
                'url': config['work_dir'],
                'datetime_ini': dt_recorrido,
                'datetime_fin': next_date - dt.timedelta(minutes=1)
            })
            dt_recorrido = next_date

        files = list(filter(lambda row: pattern.match(row["file"]) is not None, files))
        
        for row in files:
            print(row["file"])
        return files

    def _download_files(self, storage_dir, files_filtered):
        for file in files_filtered:
            filename = file['file']
            local_path_filename = f"{storage_dir}/{filename}"
            try:
                req_params = {
                    "datetime_ini_utc": file["datetime_ini"].astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S%z'),
                    "datetime_fin_utc": file["datetime_fin"].astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S%z')
                }
                body = self.config["request_body"].replace("[datetime_ini_utc]", req_params["datetime_ini_utc"])
                body = body.replace("[datetime_fin_utc]", req_params["datetime_fin_utc"])
                response = None
                if self.config["request_type"] == "POST":
                    response = self.arbor_api.post(file['url'], {'data': body})
                elif self.config["request_type"] == "GET":
                    response = self.arbor_api.get(file['url'])

                result = response.json()

                if self.config.get("result_type") is not None:
                    if self.config["result_type"] == "traffic_queries":
                        result = self.__map_result_traffic_queries(result)
                    else:
                        raise Exception(f"El result_type {self.config['result_type']} no es valido")

                with open(local_path_filename, 'w') as content:
                    content.write(json.dumps(result))
            except Exception as e:
                raise e

    def __map_result_traffic_queries(self, result):
        result_traffic = result['data']['attributes']['results']
        traffic_to_insert = []
        for traffic in result_traffic:
            row = traffic['traffic_classes']

            row_to_add = {}
            
            for item in traffic['facet_values']:
                row_to_add[item['facet'].lower()] = item['name']
                row_to_add["facet_"+item['facet'].lower()] = item
            
            row_to_add["step"]= row['in']['step']/60
            row_to_add["unit"] = result['data']['attributes']["unit"]
            
            fecha_recorrido = dt.datetime.strptime(row["in"]["timeseries_start"], "%Y-%m-%dT%H:%M:%S%z")
            fecha_recorrido = fecha_recorrido.astimezone(self.tzlocal)
            for index in range(len(row['in']['timeseries'])):
                row_to_add['timeserie'] = fecha_recorrido.strftime('%Y-%m-%d %H:%M:%S')
                row_to_add[f"in_{row_to_add['unit']}"] = row['in']['timeseries'][index]
                row_to_add[f"out_{row_to_add['unit']}"] = row['out']['timeseries'][index]
                traffic_to_insert.append(row_to_add.copy())

                fecha_recorrido = fecha_recorrido + dt.timedelta(minutes=(row['in']['step']/60))
        return traffic_to_insert

    def _get_data_from_csv(self, fields_config, filename, skip_lines=0, date_of_file=None, env={}):
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
        return data


class ArborEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, repository, sftp_service, control_carga_repo, queue_service):
        super().__init__(sftp_service, control_carga_repo, queue_service)
        self.repository = repository
        self.pm_api = sftp_service

    def get_cargas_config(self, group_id=None):
        return self.repository.get()

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        files = []
        pattern = re.compile(config['file_pattern'])

        dt_fecha_recorrido = dt_fecha1.replace(minute=0, second=0)
        while dt_fecha_recorrido.strftime(config['file_date_format']) < (dt_fecha2.replace(minute=0, second=0)).strftime(config['file_date_format']):
            str_date = dt_fecha_recorrido.strftime(config["file_date_format"])
            files.append({
                'file': f"{config['name']}_{str_date}.json",
            })
            dt_fecha_recorrido = dt_fecha_recorrido + dt.timedelta(**json.loads(config['loop_time']))
        
        files_filtered = []
        for row in files:
            str_date = pattern.search(row['file']).group(1)
            date_of_file = dt.datetime.strptime(str_date, config['file_date_format'])
            if dt_fecha1 <= date_of_file and date_of_file < dt_fecha2:
                files_filtered.append(row)
        return files_filtered


class ArborEventConsumerFromConfig(SimpleEventConsumer):
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
            self.queue_handlers[queue_id] = {'handler': LOAD_ARBOR_FROM_CONFIG, 'callback': lambda s, e: s.event_handler(map_event(e))}

        self.queue_ids = list(self.queue_handlers)
        super().execute()