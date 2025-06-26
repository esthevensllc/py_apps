import requests
import pytz
import datetime as dt
import json
import re
import os
from requests.auth import HTTPBasicAuth
from shutil import rmtree

from src.cdr.shared.services import LOAD_CDR_FROM_CONFIG
from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer
from src.shared.queue.SimpleEventConsumer import EventConsumerFromConfig
from src.shared.config import STORAGE_DIR, TIMEZONE
from src.shared.batch.domain import (ItemWriter, ReactiveDataChunkStep, ItemProcessor, EventMapper, WorkingDirectoryCreator)
from src.shared.batch.readers import ReCsvReader
from src.shared.batch.processors import ListProcessor
from src.shared.batch.writers import OracleWriter
from src.shared.batch.pollers import SftpPoller
from src.shared.batch.finder import ConfigFinder

class CdrProcessor(ListProcessor):
    def __init__(self):
        super().__init__()
        self.tzlocal = pytz.timezone(TIMEZONE)
        self.mapper_by_type["date"] = lambda value: self.map_utc_to_local(value) if value is not None else None
    
    def process(self, items):
        items = super().process([row+[self.context['filename'], self.context['server_ip']] for row in items])
        # for row in items:
        #     print(row)
        return items

    def get_items_columns(self):
        return self.context['poller']['columns']+['filename','server_ip']
    
    def map_utc_to_local(self, str_date):
        fecha = dt.datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S')
        utc_date = pytz.utc.localize(fecha)
        return utc_date.astimezone(self.tzlocal)


class CdrReportFromConfig:
    def __init__(self, db, repo, control_repo, sftp_service):
        self.config_finder = ConfigFinder(repo)
        self.poller = SftpPoller(sftp_service)
        self.chunk_task = ReactiveDataChunkStep(ReCsvReader(), CdrProcessor(), OracleWriter(db.getReference(), control_repo))
        self.event_mapper = EventMapper()
        self.wk_creator = WorkingDirectoryCreator()
        self.base_storage_dir = f"{STORAGE_DIR}cdr"
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
        context['server_ip'] = context['config']['server_ip']
        print(context['config']['name'])

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


class CdrEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, sftp_service, repository, control_carga_repo, queue_service):
        super().__init__(sftp_service, control_carga_repo, queue_service)
        self.repository = repository
        # self.finder = WebacsReportFinder()

    def get_cargas_config(self, group_id=None):
        if group_id is not None:
            return self.repository.get_by_group_id(group_id)
        return self.repository.get()

    """def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        return self.finder.execute(config, dt_fecha1, dt_fecha2)

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

        # dt_fecha2 = dt_fecha2 - dt.timedelta(**json.loads(config['loop_time']))
        if config.get("search_time_delay") is not None:
            dt_fecha2 = dt_fecha2 - dt.timedelta(**json.loads(config['search_time_delay']))
        return dt_fecha1, dt_fecha2
    """


class CdrEventConsumerFromConfig(EventConsumerFromConfig):
    def __init__(self, queue_service, app_container, notification_service, repository):
        super().__init__(queue_service, app_container, notification_service, repository)
        self.handler_name = LOAD_CDR_FROM_CONFIG
        self.max_check_attemps = 1