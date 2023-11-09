import json
import re
import requests
import datetime as dt
from src.shared.config import STORAGE_DIR
from src.shared.carga.services import BaseCargaFromConfig

from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.shared.services import SimplePaginator
from src.neteco.shared.services import LOAD_NETECO_FROM_CONFIG

class LoadNetecoFromConfig(BaseCargaFromConfig):
    def __init__(self, db, repository, sftp_service, control_carga_repo):
        super().__init__(db, repository, sftp_service, control_carga_repo)
        self.base_storage_dir = f"{STORAGE_DIR}neteco"

    # def execute(self, config_id="3", dt_fecha1=None, dt_fecha2=None):
    #     dt_fecha1 = dt.datetime.strptime("20231023", "%Y%m%d")
    #     dt_fecha2 = dt_fecha1 + dt.timedelta(hours=1)
    #     super().execute(config_id, dt_fecha1, dt_fecha2)

    def _get_files_from_server(self, config, remote_dir, dt_fecha1, dt_fecha2):
        files = []
        str_date = dt_fecha1.strftime(config["file_date_format"])
        starttime = int(dt.datetime.timestamp(dt_fecha1))
        endtime = int(dt.datetime.timestamp(dt_fecha2 - dt.timedelta(seconds=1)))
        file = {
            'file': f"{config['name']}_{str_date}.json",
            'path': config["work_dir"],
            'type': config["type"],
            'starttime': starttime,
            'endtime': endtime
        }
        if config.get('api_params') is not None:
            file["typeIds"] = config["api_params"]['typeIds']
            file["signalIds"] = config["api_params"]['signalIds']
        files.append(file)
        return files

    def _download_files(self, storage_dir, files_filtered):
        for file in files_filtered:
            filename = file['file']
            local_path_filename = f"{storage_dir}/{filename}"
            try:
                if "paginated-api" == self.config["src_type"]:
                    self._get_pagginated_data(storage_dir, files_filtered, file)
                elif "signal-statistic" == self.config["src_type"]:
                    self._get_signal_statistic(storage_dir, file)
                else:
                    response = self.sftp_service.get(file['path'])
                    json = response.json()
                    data = json["data"]
                    with open(local_path_filename, 'w') as content:
                        content.write(json.dumps(data))
            except Exception as e:
                raise e

    def _get_pagginated_data(self, storage_dir, files_filtered, file):
        params = {"pageIndex": 1, "pageSize": 4000}
        if file["type"] == "stats":
            params["startTime"] = int(file["starttime"])*1000
            params["endTime"] = int(file["endtime"])*1000
        response = self.sftp_service.get(file['path'], {"headers": {"params": json.dumps(params)}})
        rjson = response.json()
        data = rjson["data"]
        print(rjson["description"])
        while rjson["hasNextPage"]:
            params["pageIndex"] = params["pageIndex"] + 1
            response = self.sftp_service.get(file['path'], {"headers": {"params": json.dumps(params)}})
            rjson = response.json()
            data = data + rjson["data"]

        local_path_filename = f"{storage_dir}/{file['file']}"
        with open(local_path_filename, 'w') as content:
            content.write(json.dumps(data))

    def _get_signal_statistic(self, storage_dir, file):
        params = {"pageIndex": 1, "pageSize": 4000, "typeIds": file["typeIds"]}
        managed_objects = self.sftp_service.get_all_data("openapi/neteco/nbi/v2/mo", {"headers": {"params": json.dumps(params)}})
        managed_objects_dn = []
        for row in managed_objects:
            managed_objects_dn.append(row["dn"])

        paginator = SimplePaginator(managed_objects_dn, perPage=50)
        pages = paginator.get_num_pages()
        page = 1
        data = []
        while page <= pages:
            params = {
                "pageIndex": 1,
                "pageSize": 4000,
                "startTime": int(file["starttime"])*1000,
                "endTime": int(file["endtime"])*1000,
                "dns": paginator.get_page(page),
                "signalIds": file["signalIds"]
            }
            # print(params)
            data = data + self.sftp_service.get_all_data(file['path'], {"headers": {"params": json.dumps(params)}})
            # print(f"page {page}", len(data))
            page = page + 1

        # transform data
        managed_objects_by_key = {}
        for row in managed_objects:
            managed_objects_by_key[row["dn"]] = row
        
        data_by_key = {}
        for row in data:
            key = row["dn"]+"__"+str(row["signalResultTime"])
            if data_by_key.get(key) is None:
                mo = managed_objects_by_key[row["dn"]]
                data_by_key[key] = {
                    "dn": row["dn"],
                    "parentDn": mo["parentDn"],
                    "typeId": mo["typeId"],
                    "signalResultTime": row["signalResultTime"]
                }
                for signalId in file["signalIds"]:
                    data_by_key[key][signalId] = None
            data_by_key[key][row["signalId"]] = row["signalValue"]

        result = []
        for key in data_by_key.keys():
            result.append(data_by_key[key])

        local_path_filename = f"{storage_dir}/{file['file']}"
        with open(local_path_filename, 'w') as content:
            content.write(json.dumps(result))
            

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
        return data


class NetecoEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, repository, sftp_service, control_carga_repo, queue_service):
        super().__init__(sftp_service, control_carga_repo, queue_service)
        self.repository = repository

    def get_cargas_config(self, group_id=None):
        return self.repository.get()

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        files = []
        pattern = re.compile(config['file_pattern'])

        dt_fecha_recorrido = dt_fecha1.replace(minute=0, second=0)
        while dt_fecha_recorrido.strftime(config['file_date_format']) < (dt_fecha2.replace(minute=0, second=0)).strftime(config['file_date_format']):
            str_date = dt_fecha_recorrido.strftime(config["file_date_format"])
            files.append({
                'file': f"{config['name']}_{str_date}.json"
            })
            dt_fecha_recorrido = dt_fecha_recorrido + dt.timedelta(**json.loads(config['loop_time']))
        
        files_filtered = []
        for row in files:
            str_date = pattern.search(row['file']).group(1)
            date_of_file = dt.datetime.strptime(str_date, config['file_date_format'])
            if dt_fecha1 <= date_of_file and date_of_file < dt_fecha2:
                files_filtered.append(row)
        return files_filtered


class NetecoEventConsumerFromConfig(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, repository, notification_service):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.1
        self.repository = repository
        self.loop = False
        self.carga_config = {}

    def execute(self, group_id=None):
        cargas = []
        if group_id == None:
            cargas = self.repository.get()
        else:
            cargas = self.repository.get_by_group_id(group_id)

        if len(cargas) == 0:
            raise Exception(f"No existen cargas")
        
        for row in cargas:
            self.carga_config[row["queue_id"]] = row

        def map_event(event):
            event['msg_body']['config_id'] = self.carga_config[event['queue_id']]["id"]
            return event

        for row in cargas:
            queue_id = row["queue_id"]
            self.queue_handlers[queue_id] = {'handler': LOAD_NETECO_FROM_CONFIG, 'callback': lambda s, e: s.event_handler(map_event(e))}

        self.queue_ids = list(self.queue_handlers)
        super().execute()
