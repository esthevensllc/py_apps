from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer
from src.shared.queue.SimpleEventConsumer import EventConsumerFromConfig
from src.zte.shared.services import LOAD_CH_ZTE_STATS_FROM_CONFIG
from src.shared.config import STORAGE_DIR
from src.shared.batch.finder import ConfigFinder, SftpFinder
from src.shared.batch.domain import (ItemReader, CompositeWriter, ReactiveDataChunkStep, EventMapper, WorkingDirectoryCreator)
from src.shared.batch.writers import ClickhouseWriter, ControlCargaWriter, OracleScriptExecutor
from src.shared.batch.readers import ReCsvReader
from src.shared.batch.processors import ListProcessor
from src.shared.batch.pollers import SftpPoller
from shutil import rmtree
import os
import datetime as dt
from zipfile import ZipFile

class ReZteReader(ItemReader):
    def __init__(self):
        self.csv_reader = ReCsvReader()
        self.chunk_limit = 0
        self.context = None
        self.on_next_callback = None

    def start(self, context: dict):
        self.context = context
        self.chunk_limit = context['config']['chunk_limit']
        self.context['file_count'] = 0

    def read(self):
        pass

    def on_next(self, callback):
        def on_next_callback_decorator(chunk):
            self.context['file_count'] += len(chunk)
            callback(chunk)
        self.on_next_callback = on_next_callback_decorator

    def subscribe(self):
        csv_files = self._extrac_files(self.context['storage_dir'], self.context['filename'])

        for filename in csv_files:
            sub_context = {
                'config': {'chunk_limit': self.chunk_limit},
                'poller': self.context['poller'],
                'storage_dir': self.context['storage_dir'],
                'filename': filename,
            }
            self.csv_reader.start(sub_context)
            self.csv_reader.on_next(self.on_next_callback)
            self.csv_reader.subscribe()

    def _extrac_files(self, storage_dir, filename):
        zf = ZipFile(f'{storage_dir}/{filename}', 'r')
        zf.extractall(storage_dir)
        unzip_files = zf.namelist()
        zf.close()
        os.unlink(f"{storage_dir}/{filename}")
        return unzip_files
    
class ChZteProcessor(ListProcessor):
    def __init__(self):
        super().__init__()
        self.mapper_by_type["date"] = lambda value: self.map_to_datetime(value) if value is not None else None
    
    def process(self, items):
        items = super().process(items)
        return items

    def get_items_columns(self):
        return self.context['poller']['columns']
    
    def map_to_datetime(self, str_date):
        fecha = dt.datetime.strptime(str_date, '%Y%m%d%H%M%S')
        return fecha


class ZteConfigFinder:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, context):
        config = self.repo.find(context['config_id'])
        context['config'] = config
        return context


class ChZteStatsFromConfig:
    def __init__(self, clickhouse, repo, sftp, control_repo):
        self.config_finder = ConfigFinder(repo)
        self.poller = SftpPoller(sftp)
        self.chunk_task = ReactiveDataChunkStep(
            ReZteReader(),
            ChZteProcessor(),
            CompositeWriter([
                ClickhouseWriter(clickhouse.getReference()),
                ControlCargaWriter(control_repo),
                # OracleScriptExecutor(db.getReference())
            ])
        )
        self.event_mapper = EventMapper()
        self.wk_creator = WorkingDirectoryCreator()
        self.base_storage_dir = f"{STORAGE_DIR}ch_zte_stats"
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
        context['str_filedate'] = context['fecha_ini'].strftime('%Y-%m-%d %H:%M')+":00"

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


class ChZteEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, repository, sftp_service, control_carga_repo, queue_service):
        super().__init__(sftp_service, control_carga_repo, queue_service)
        self.repository = repository
        self.finder = SftpFinder(sftp_service)

    def get_cargas_config(self, group_id=None):
        if group_id is not None:
            return self.repository.get_by_group_id(group_id)
        return self.repository.get()
    
    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        return self.finder.execute(config, dt_fecha1, dt_fecha2)


class ChZteEventConsumerFromConfig(EventConsumerFromConfig):
    def __init__(self, queue_service, app_container, notification_service, repository):
        super().__init__(queue_service, app_container, notification_service, repository)
        self.handler_name = LOAD_CH_ZTE_STATS_FROM_CONFIG
        self.max_check_attemps = 1
