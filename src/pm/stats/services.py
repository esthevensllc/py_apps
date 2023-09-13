import datetime as dt
import re
import json
import csv
from src.shared.config import STORAGE_DIR
from src.shared.carga.services import BaseCargaFromConfig

from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.pm.shared.services import LOAD_PM_FROM_CONFIG

class LoadPMFromConfig(BaseCargaFromConfig):
    def __init__(self, db, repository, sftp_service, control_carga_repo):
        super().__init__(db, repository, sftp_service, control_carga_repo)
        self.pm_api = sftp_service
        self.base_storage_dir = f"{STORAGE_DIR}pm"

    def _get_files_from_server(self, config, remote_dir, dt_fecha1, dt_fecha2):
        files = []
        str_date = dt_fecha1.strftime(config["file_date_format"])
        starttime = int(dt.datetime.timestamp(dt_fecha1 - dt.timedelta(minutes=1)))
        endtime = int(dt.datetime.timestamp(dt_fecha2 - dt.timedelta(minutes=1)))
        # print([starttime, endtime])
        url = None
        sub_url = None
        if config.get("sub_api_query") is None:
            url = f"{config['api_query']}&starttime={starttime}&endtime={endtime}"
        else:
            url = f"{config['api_query']}"
            sub_url = f"{config['sub_api_query']}&starttime={starttime}&endtime={endtime}"
        
        files.append({
            'file': f"{config['name']}_{str_date}.csv",
            'url': url,
            'sub_url': sub_url
        })
        
        pattern = re.compile(config['file_pattern'])
        files_filtered = []
        for row in files:
            str_date = pattern.search(row['file']).group(1)
            date_of_file = dt.datetime.strptime(str_date, config['file_date_format'])
            if dt_fecha1 <= date_of_file and date_of_file < dt_fecha2:
                files_filtered.append(row)
        
        for row in files_filtered:
            print(row["file"])
        return files_filtered

    def _download_files(self, storage_dir, files_filtered):
        for file in files_filtered:
            filename = file['file']
            local_path_filename = f"{storage_dir}/{filename}"
            try:
                if file.get('sub_url') is None:
                    response = self.pm_api.get(file['url'])
                    with open(local_path_filename, 'wb') as content:
                        content.write(response.content)
                else:
                    reload_fields = list(filter(lambda r: r["to_reload"] is None, self.fields_config))
                    skip_lines= 1
                    response = self.pm_api.get(file['url'])
                    result = response.json()
                    devices = result["d"]["results"]
                    csv_values = []
                    for row in devices:
                        deviceid = row["ID"]
                        response = self.pm_api.get(f"{file['sub_url']}&$filter=((device/ID eq {deviceid}))")
                        with open(f"{storage_dir}/{deviceid}_{filename}", 'wb') as content:
                            content.write(response.content)

                        with open(f"{storage_dir}/{deviceid}_{filename}", encoding='UTF-8') as content:
                            reader = csv.reader(content)
                            counter = 0 - skip_lines
                            for row in reader:
                                counter += 1
                                if counter <=0:
                                    continue
                                validation = True
                                for field in reload_fields:
                                    value = row[int(field["src_fieldname"])]
                                    if value is None or value == '':
                                        validation = False
                                        break
                                if validation == False:
                                    continue
                                csv_values.append(row)

                        with open(local_path_filename, 'w', encoding="utf-8",  newline="") as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerows(csv_values)
            except Exception as e:
                raise e


class PMEventProducerFromConfig(RemoteConnectEventProducer):
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
                'file': f"{config['name']}_{str_date}.csv"
            })
            dt_fecha_recorrido = dt_fecha_recorrido + dt.timedelta(**json.loads(config['loop_time']))
        
        files_filtered = []
        for row in files:
            str_date = pattern.search(row['file']).group(1)
            date_of_file = dt.datetime.strptime(str_date, config['file_date_format'])
            if dt_fecha1 <= date_of_file and date_of_file < dt_fecha2:
                files_filtered.append(row)
        return files_filtered


class PMEventConsumerFromConfig(SimpleEventConsumer):
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
            self.queue_handlers[queue_id] = {'handler': LOAD_PM_FROM_CONFIG, 'callback': lambda s, e: s.event_handler(map_event(e))}

        self.queue_ids = list(self.queue_handlers)
        super().execute()
