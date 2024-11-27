from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer
from src.shared.queue.SimpleEventConsumer import EventConsumerFromConfig
from src.clickhouse.shared.services import LOAD_CH_FROM_CONFIG
from src.shared.config import STORAGE_DIR
from src.shared.batch.domain import (ReactiveDataChunkStep, ItemProcessor, EventMapper, WorkingDirectoryCreator)
from src.shared.batch.writers import OracleWriter
from src.shared.batch.readers import PandasDataFrameReader, DatabaseCursorReader
from src.shared.batch.pollers import ClickhousePoller
import os
import datetime as dt
import pandas as pd
from zipfile import ZipFile
import re
import json
from shutil import rmtree, copyfileobj

class ChReplicationProcessor(ItemProcessor):
    def __init__(self):
        self.context = dict()
    
    def start(self, context):
        self.context = context
        
    def process(self, items):
        headers = [field['src_fieldname'] for field in self.context['config']['fields']]
        src_headers = self.context['poller']['columns']
        src_headers_index = {}
        for index in range(len(src_headers)):
            src_headers_index[src_headers[index]] = index
        
        return [[row[src_headers_index[header]] for header in headers] for row in items]


class ChReplicationConfigFinder:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, context):
        config = self.repo.find(context['config_id'])
        if config is not None:
            config['fields'] = self.repo.get_fields_by_id(context['config_id'])
        context['config'] = config
        return context


class ChReplicationFinder:
    def __init__(self, db):
        self.db = db

    def execute(self, config, dt_fecha1, dt_fecha2):
        files = self.db.fetch(config['src_query_finder'])
        files = list(map(lambda row: self._map_date_to_file(config, row[0]), files))
            
        pattern = re.compile(config['file_pattern'])
        files_filtered = list(filter(lambda row: pattern.match(row['file']) is not None, files))
        return files_filtered

    def _map_date_to_file(self, config, fecha):
        str_date = fecha.strftime(config["file_date_format"])
        return {
            "file": f"{config['name']}_{str_date}.json",
            "str_filedate": fecha.strftime('%Y-%m-%d %H:%M')+":00",
        }


class ChReplicationPoller:
    def __init__(self, db):
        self.db = db

    def download(self, context):
        config = context['config']

        pattern = re.compile(config['file_pattern'])
        str_date = pattern.search(context['filename']).group(1)
        context['file_date'] = dt.datetime.strptime(str_date, config['file_date_format'])

        params = {
            'fecha_ini': context['file_date'],
            'fecha_fin': context['file_date'] + dt.timedelta(**json.loads(config['loop_time']))
        }
        cursor = self.db.cursor()
        cursor.execute(config['src_query'], params)

        def fetchmany(chunk_limit):
            rows = cursor.fetchmany(chunk_limit)
            if not rows:
                cursor.close()
                return None
            return rows

        context['poller'] = {
            'cursor': fetchmany,
            'columns': [col[0] for col in cursor.description]
        }


class ChReplicationFromConfig:
    def __init__(self, db, repo, ch_db, control_repo):
        self.config_finder = ChReplicationConfigFinder(repo)
        self.poller = ClickhousePoller(ch_db)
        self.chunk_task = ReactiveDataChunkStep(DatabaseCursorReader(), ChReplicationProcessor(), OracleWriter(db.getReference(), control_repo))
        self.event_mapper = EventMapper()
        self.wk_creator = WorkingDirectoryCreator()
        self.base_storage_dir = f"{STORAGE_DIR}ch"
        self.storage_dir = None

    def execute(self, context):
        try:
            context = self.config_finder.execute(context)
            self.start(context)
            self.poller.download(context)
            context = self.chunk_task.execute(context)
            self.complete()
        except BaseException as e:
            self.error(e)

    def start(self, context):
        self.storage_dir = self.wk_creator.create(self.base_storage_dir)
        context['storage_dir'] = self.storage_dir

    def complete(self):
        self.end_time = dt.datetime.now()
        if self.storage_dir is not None:
            rmtree(self.storage_dir)

    def error(self, error):
        self.complete()
        raise error

    def event_handler(self, event):
        event_mapped = self.event_mapper.execute(event)
        self.execute(event_mapped)


class ChReplicationEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, repository, pg_db, control_carga_repo, queue_service):
        super().__init__(pg_db, control_carga_repo, queue_service)
        self.repository = repository
        self.finder = ChReplicationFinder(pg_db)

    def get_cargas_config(self, group_id=None):
        if group_id is not None:
            return self.repository.get_by_group_id(group_id)
        return self.repository.get()

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        return self.finder.execute(config, dt_fecha1, dt_fecha2)


class ChReplicationEventConsumerFromConfig(EventConsumerFromConfig):
    def __init__(self, queue_service, app_container, notification_service, repository):
        super().__init__(queue_service, app_container, notification_service, repository)
        self.handler_name = LOAD_CH_FROM_CONFIG
