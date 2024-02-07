import os
import json
import datetime as dt
import re
from src.gde.shared.services import LOAD_GDE_FROM_CONFIG
from src.shared.config import STORAGE_DIR
from src.shared.services import TempDataManager
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.shared.carga.services import BaseCargaFromConfig
from src.shared.carga.services import (ApiDataPoller)
from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer

class GdeDataFinder:
    def get_source_files(self, config, dt_fecha1, dt_fecha2):
        files = []
        dt_fecha_recorrido = dt_fecha1
        delta = dt.timedelta(**json.loads(config['loop_time']))
        delta_utc = dt.timedelta(hours=4, minutes=59)
        while dt_fecha_recorrido.strftime(config['file_date_format']) < dt_fecha2.strftime(config['file_date_format']):
            str_date = dt_fecha_recorrido.strftime(config["file_date_format"])
            next_date = dt_fecha_recorrido + delta

            params = {
                "date": (next_date + delta_utc).strftime('%Y-%m-%d %H:%M')+":00",
                "substract_minutes": round(delta.seconds/60)-1,
                "configured_field": "lastoccurrence",
                "limit": 30000,
                "start": 0
            }
            # print(params["date"], params["substract_minutes"])
            
            files.append({
                'file': f"{config['name']}_{str_date}.json",
                'str_filedate': dt_fecha_recorrido.strftime('%Y-%m-%d %H:%M')+":00",
                'str_filedate_day': dt_fecha_recorrido.strftime('%Y-%m-%d')+" 00:00:00",
                'url': config["api_query"],
                'params': params
            })
            dt_fecha_recorrido = next_date
            
        pattern = re.compile(config['file_pattern'])
        files_filtered = list(filter(lambda row: pattern.match(row['file']) is not None, files))
        # for row in files_filtered:
        # print(row)
        return files_filtered


class GdeDataPoller(ApiDataPoller):
    def __init__(self, api):
        self.api = api

    def download_one(self, config, source, storage_dir):
        data = self.api.get_all(source["url"], source["params"])
        local_path = f"{storage_dir}/{source['file']}"
        data_manager = TempDataManager(config["chunk_limit"], storage_dir)
        data_manager.add_rows(data)
        source["temp_manager"] = [data_manager]


class GdeProcessor:
    def process(self, config, sources):
        for index in range(len(sources)):
            sources[index] = self.process_one(sources[index], config)
        return sources

    def process_one(self, source, config):
        mapped_manager = []
        for temp_data in source["temp_manager"]:
            envlist = {
                'str_filedate': source['str_filedate'],
                'str_filedate_day': source['str_filedate_day'],
                'filename': source['file'],
            }
            temp_manager = self.map_temp_manager(temp_data, config, env=envlist)
            mapped_manager.append(temp_manager)
        source["temp_manager"] = mapped_manager
        return source

    def map_temp_manager(self, temp_manager, config, env):
        mapped_temp_data = TempDataManager(temp_manager.limit, temp_manager.path)
        for chunk_data in temp_manager.get():
            mapped_data = []
            for index in range(len(chunk_data)):
                row = chunk_data[index]
                mapped_row = {}
                for field in config["fields"]:
                    try:
                        value = row[field["src_fieldname"]]
                        if field.get('map_with') is not None:
                            value = eval(f"f\"{field['map_with']}\"")
                        if value == '':
                            value = None
                        mapped_row[field["fieldname"]] = value
                    except BaseException as e:
                        print(row)
                        print(f"line: {counter}, field: {field['fieldname']}, value: '{value}'")
                        raise e
                chunk_data[index] = mapped_row
            mapped_temp_data.add_rows(chunk_data)
        return mapped_temp_data



class LoadGdeFromConfig(BaseCargaFromConfig):
    def __init__(self, db, repository, sftp_service, control_carga_repo):
        super().__init__(db, repository, sftp_service, control_carga_repo)
        self.nfa_api = sftp_service
        self.base_storage_dir = f"{STORAGE_DIR}gde"
        self.gde_finder = GdeDataFinder()
        self.gde_poller = GdeDataPoller(self.nfa_api)
        self.gde_processor = GdeProcessor()

    def _get_files_from_server(self, config, remote_dir, dt_fecha1, dt_fecha2):
        return self.gde_finder.get_source_files(config, dt_fecha1, dt_fecha2)

    def _download_files(self, storage_dir, files):
        self.sources = self.gde_poller.download(self.config, files, storage_dir)

    def _get_data_from_csv(self, fields_config, filename, skip_lines=0, date_of_file=None, env={}):
        self.config["fields"] = fields_config
        sources = self.gde_processor.process(self.config, self.sources)
        data = []
        for src in sources:
            for manager in src["temp_manager"]:
                for chunk_data in manager.get():
                    data += chunk_data
        return data


class GdeEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, repository, sftp_service, control_carga_repo, queue_service):
        super().__init__(sftp_service, control_carga_repo, queue_service)
        self.repository = repository
        self.gde_finder = GdeDataFinder()

    def get_cargas_config(self, group_id=None):
        return self.repository.get()

    def get_date_range(self, config):
        time_ago_delta = json.loads(config["search_time_ago"])
        dt_fecha2 = dt.datetime.now()
        dt_fecha1 = dt_fecha2 - dt.timedelta(**time_ago_delta)

        dt_fecha1 = dt_fecha1.replace(minute=0, second=0)
        dt_fecha2 = dt_fecha2 - dt.timedelta(**json.loads(config['loop_time']))
        if config.get("search_time_delay") is not None:
            dt_fecha2 = dt_fecha2 - dt.timedelta(**json.loads(config['search_time_delay']))
        return dt_fecha1, dt_fecha2

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        return self.gde_finder.get_source_files(config, dt_fecha1, dt_fecha2)


class GdeEventConsumerFromConfig(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service, repository):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 20
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
            self.queue_handlers[queue_id] = {'handler': LOAD_GDE_FROM_CONFIG, 'callback': lambda s, e: s.event_handler(map_event(e))}

        self.queue_ids = list(self.queue_handlers)
        super().execute()