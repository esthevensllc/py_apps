import os
import json
import datetime as dt
import re
from src.mariadb.shared.services import LOAD_MARIADB_FROM_CONFIG
from src.shared.config import STORAGE_DIR
from src.shared.services import TempDataManager
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.shared.carga.services import EtlFromConfig
from src.shared.carga.services import (ApiDataPoller, DatabaseDataPoller, TempManagerProcessor)
from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer

class MariadbDataFinder:
    def get_source_files(self, config, dt_fecha1, dt_fecha2):
        files = []
        dt_fecha_recorrido = dt_fecha1
        delta = dt.timedelta(**json.loads(config['loop_time']))
        # delta_utc = dt.timedelta(hours=4, minutes=59)
        while dt_fecha_recorrido.strftime(config['file_date_format']) < dt_fecha2.strftime(config['file_date_format']):
            str_date = dt_fecha_recorrido.strftime(config["file_date_format"])
            next_date = dt_fecha_recorrido + delta

            if config["type"] == "alarms":
                files.append({
                    "file": f"{config['name']}_{str_date}_1.json",
                    "str_filedate": dt_fecha_recorrido.strftime('%Y-%m-%d %H:%M')+":00",
                    "str_filedate_fin": next_date.strftime('%Y-%m-%d %H:%M')+":00",
                    "date_field": "fecha_inicial",
                    # "query": config["src_query"].format(query_field="fecha_inicial")
                })
                
                files.append({
                    "file": f"{config['name']}_{str_date}_2.json",
                    "str_filedate": dt_fecha_recorrido.strftime('%Y-%m-%d %H:%M')+":00",
                    "str_filedate_fin": next_date.strftime('%Y-%m-%d %H:%M')+":00",
                    "date_field": "fecha_fin",
                    # "query": config["fecha_1"].format(query_field="fecha_inicial")
                })
            dt_fecha_recorrido = next_date
            
        pattern = re.compile(config['file_pattern'])
        files_filtered = list(filter(lambda row: pattern.match(row['file']) is not None, files))
        return files_filtered


class LoadMariadbFromConfig(EtlFromConfig):
    def __init__(self, db, repository, mariadb, control_carga_repo):
        super().__init__(db, repository, mariadb, control_carga_repo)
        self.mariadb = mariadb
        self.base_storage_dir = f"{STORAGE_DIR}gde"
        self.finder = MariadbDataFinder()
        self.poller = DatabaseDataPoller(self.mariadb)
        self.processor = TempManagerProcessor()


class MariadbEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, repository, sftp_service, control_carga_repo, queue_service):
        super().__init__(sftp_service, control_carga_repo, queue_service)
        self.repository = repository
        self.finder = MariadbDataFinder()

    def get_cargas_config(self, group_id=None):
        return self.repository.get()

    def get_date_range(self, config):
        dt_fecha2 = dt.datetime.now()

        dt_fecha2 = dt_fecha2 - dt.timedelta(**json.loads(config['loop_time']))
        fecha_loop = dt_fecha2.replace(minute=0, second=0)
        while fecha_loop <= dt_fecha2:
            fecha_loop = fecha_loop + dt.timedelta(**json.loads(config["loop_time"]))
        
        # fecha ini - fin
        dt_fecha2 = fecha_loop
        time_ago_delta = json.loads(config["search_time_ago"])
        dt_fecha1 = dt_fecha2 - dt.timedelta(**time_ago_delta)

        dt_fecha2 = dt_fecha2 - dt.timedelta(**json.loads(config['loop_time']))
        if config.get("search_time_delay") is not None:
            dt_fecha2 = dt_fecha2 - dt.timedelta(**json.loads(config['search_time_delay']))
        return dt_fecha1, dt_fecha2

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        return self.finder.get_source_files(config, dt_fecha1, dt_fecha2)


class MariadbEventConsumerFromConfig(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service, repository):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 1
        self.repository = repository
        self.loop = False
        self.config_by_queueid = {}
        self.handler_identifier = LOAD_MARIADB_FROM_CONFIG

    def execute(self, group_id=None):
        self.execute_by_group(group_id)
