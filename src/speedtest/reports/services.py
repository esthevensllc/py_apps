import datetime as dt
import re
from src.shared.config import STORAGE_DIR
from src.shared.carga.services import BaseCargaFromConfig

from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.speedtest.shared.services import LOAD_SPEEDTEST_FROM_CONFIG

class LoadSeedTestFromConfig(BaseCargaFromConfig):
    def __init__(self, db, repository, sftp_service, control_carga_repo):
        super().__init__(db, repository, sftp_service, control_carga_repo)
        self.speedtest_api = sftp_service
        self.base_storage_dir = f"{STORAGE_DIR}speedtest"

    def _get_files_from_server(self, config, remote_dir, dt_fecha1, dt_fecha2):
        result = self.speedtest_api.get(config["work_dir"])
        result = result.json()
        files = []
        pattern = re.compile(config['file_pattern'])
        for row in result:
            name = row["name"]
            if config.get("file_date_added_from_mtime") == True:
                filename_parts = row["name"].split(".")
                strfiledate = dt.datetime.fromtimestamp(row["mtime"]/1000).strftime(config['file_date_format'])
                name = f"{filename_parts[0]}_{strfiledate}.{filename_parts[1]}"
            if pattern.match(name) is not None:
                files.append({
                    'file': name,
                    'path': config["work_dir"],
                    'url': row["url"]
                })
        
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
                response = self.speedtest_api.get(file['url'], base_url=False)
                with open(local_path_filename, 'wb') as content:
                    content.write(response.content)
            except Exception as e:
                raise e


class SeedTestEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, repository, sftp_service, control_carga_repo, queue_service):
        super().__init__(sftp_service, control_carga_repo, queue_service)
        self.repository = repository
        self.speedtest_api = sftp_service

    def get_cargas_config(self, group_id=None):
        return self.repository.get()

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        result = self.speedtest_api.get(config["work_dir"])
        result = result.json()
        files = []
        pattern = re.compile(config['file_pattern'])
        for row in result:
            name = row["name"]
            if config.get("file_date_added_from_mtime") == True:
                filename_parts = row["name"].split(".")
                strfiledate = dt.datetime.fromtimestamp(row["mtime"]/1000).strftime(config['file_date_format'])
                name = f"{filename_parts[0]}_{strfiledate}.{filename_parts[1]}"
            if pattern.match(name) is not None:
                files.append({
                    'file': name,
                    'path': config["work_dir"],
                    'url': row["url"]
                })
        
        files_filtered = []
        for row in files:
            str_date = pattern.search(row['file']).group(1)
            date_of_file = dt.datetime.strptime(str_date, config['file_date_format'])
            if dt_fecha1 <= date_of_file and date_of_file < dt_fecha2:
                files_filtered.append(row)
        return files_filtered


class SpeedTestEventConsumerFromConfig(SimpleEventConsumer):
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
            self.queue_handlers[queue_id] = {'handler': LOAD_SPEEDTEST_FROM_CONFIG, 'callback': lambda s, e: s.event_handler(map_event(e))}

        self.queue_ids = list(self.queue_handlers)
        super().execute()
