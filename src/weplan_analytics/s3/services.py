import os
import json
import datetime as dt
import re
from src.weplan_analytics.shared.services import LOAD_WEPLANCLOUD_FROM_CONFIG
from src.shared.config import STORAGE_DIR
from src.shared.services import TempDataManager
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.shared.carga.services import EtlFromConfig
from src.shared.carga.services import (ApiDataPoller, AwsS3DataPoller, TempManagerProcessor)
from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer

class WeplanCloudDataFinder:
    def __init__(self, s3_client, cache):
        self.s3 = s3_client
        self.cache = cache
    
    def get_source_files(self, config, dt_fecha1, dt_fecha2):
        files = []
        dt_fecha_recorrido = dt_fecha1
        delta = dt.timedelta(**json.loads(config['loop_time']))
        while dt_fecha_recorrido.strftime(config['file_date_format']) < dt_fecha2.strftime(config['file_date_format']):
            str_date = dt_fecha_recorrido.strftime(config["file_date_format"])
            str_wk_date = dt_fecha_recorrido.strftime(config["wk_date_format"])
            next_date = dt_fecha_recorrido + delta

            params = {
                'Bucket': config['src_bucket'],
                "Prefix": config['work_dir'].replace("{date}", str_wk_date)
                # "Prefix": "active_cell_data/sdk_client=Weplan/year=2024/month=09/day=11/"
            }
            cache_key = f"s3_{params['Bucket']}_{params['Prefix'].replace('/','-')}"
            if self.cache.get(cache_key) is None:
                cloud_files = self.get_cloud_files(params)
                cloud_files = list(map(lambda r: {'Key': r['Key']}, cloud_files))
                self.cache.set(cache_key, cloud_files, 300)
            cloud_files = self.cache.get(cache_key)
            files = []
            for row in cloud_files:
                filename = row['Key'].replace(params['Prefix']+"/", "")
                files.append({
                    "file": f"{str_date}_{filename}" if not filename.endswith(".csv") else filename,
                    "original_file": filename,
                    "path": params['Prefix'],
                    "str_filedate": dt_fecha_recorrido.strftime('%Y-%m-%d %H:%M')+":00",
                    # "key": row['Key']
                    # "str_filedate_fin": next_date.strftime('%Y-%m-%d %H:%M')+":00",
                    # "date_field": "fecha_inicial",
                    # "query": config["src_query"].format(query_field="fecha_inicial")
                })
            dt_fecha_recorrido = next_date
            
        pattern = re.compile(config['file_pattern'])
        files_filtered = list(filter(lambda row: pattern.match(row['file']) is not None and dt_fecha1.strftime('%Y-%m-%d %H:%M')+":00" <= row['str_filedate'] and row['str_filedate'] < dt_fecha2.strftime('%Y-%m-%d %H:%M')+":00", files))
        return files_filtered

    def get_cloud_files(self, params):
        files = []
        response = self.s3.list_objects_v2(**params)
        if response.get('IsTruncated'):
            params["ContinuationToken"] = response.NextContinuationToken
            files.extend(self.get_cloud_files(params))
        else:
            files_response = response.get('Contents')
            if files_response is not None:
                files.extend(files_response)
        return files

class LoadWeplanCloudFromConfig(EtlFromConfig):
    def __init__(self, db, repository, s3_client, control_carga_repo, cache):
        super().__init__(db, repository, s3_client, control_carga_repo)
        self.s3_client = s3_client
        self.base_storage_dir = f"{STORAGE_DIR}weplan"
        self.finder = WeplanCloudDataFinder(s3_client, cache)
        self.poller = AwsS3DataPoller(s3_client)
        self.processor = TempManagerProcessor()


class WeplanCloudEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, repository, s3_client, control_carga_repo, queue_service, cache):
        super().__init__(s3_client, control_carga_repo, queue_service)
        self.repository = repository
        self.finder = WeplanCloudDataFinder(s3_client, cache)

    def get_cargas_config(self, group_id=None):
        return self.repository.get()

    def get_date_range(self, config):
        dt_fecha2 = dt.datetime.now()

        dt_fecha2 = dt_fecha2 - dt.timedelta(**json.loads(config['loop_time']))
        fecha_loop = dt_fecha2.replace(minute=0, second=0)
        if config['event_format'] == 'dxd':
            fecha_loop = fecha_loop.replace(hour=0)
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


class WeplanCloudEventConsumerFromConfig(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service, repository):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 1
        self.repository = repository
        self.loop = False
        self.config_by_queueid = {}
        self.handler_identifier = LOAD_WEPLANCLOUD_FROM_CONFIG

    def execute(self, group_id=None):
        self.execute_by_group(group_id)
