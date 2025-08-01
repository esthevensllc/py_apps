import datetime as dt
from shutil import rmtree
import re

from src.fping.shared.services import LOAD_FPING_FROM_CONFIG
from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer
from src.shared.queue.SimpleEventConsumer import EventConsumerFromConfig
from src.shared.config import STORAGE_DIR
from src.shared.batch.domain import (CompositeWriter, ReactiveDataChunkStep, EventMapper, WorkingDirectoryCreator)
from src.shared.batch.readers import ReCsvReader
from src.shared.batch.processors import ListProcessor
from src.shared.batch.writers import ClickhouseWriter, ControlCargaWriter, OracleScriptExecutor
from src.shared.batch.pollers import SftpPoller
from src.shared.batch.finder import ConfigFinder, SftpFinder

class FpingProcessor(ListProcessor):
    
    def process(self, items):
        items = super().process([row+[self.context['semana']] for row in items])
        print(self.get_items_columns())
        print(len(items))
        return items

    def get_items_columns(self):
        return self.context['poller']['columns']+['semana']


class FpingReportFromConfig:
    def __init__(self, db, oracledb, repo, control_repo, sftp_service):
        self.config_finder = ConfigFinder(repo)
        self.poller = SftpPoller(SftpWrapper(sftp_service))
        self.chunk_task = ReactiveDataChunkStep(ReCsvReader(), FpingProcessor(), CompositeWriter([
            ClickhouseWriter(db.getReference()), ControlCargaWriter(control_repo), OracleScriptExecutor(oracledb.getReference())
        ]))
        self.event_mapper = EventMapper()
        self.wk_creator = WorkingDirectoryCreator()
        self.base_storage_dir = f"{STORAGE_DIR}fping"
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
        context['semana'] = context['fecha_ini'].strftime('%G%V')
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


class SftpWrapper:
    def __init__(self, sftp_service):
        super().__init__()
        self.sftp_service = sftp_service

    def useConnection(self, connection):
        self.sftp_service.useConnection(connection)

    def connect(self):
        return self.sftp_service.connect()

    def disconnect(self):
        self.sftp_service.disconnect()

    def getReference(self):
        return self.sftp_service.getReference()
    
    def get_filenames(self, work_dir, str_pattern):
        filenames = self.sftp_service.get_filenames(work_dir, str_pattern)
        return [filename[:-4]+"1"+filename[-4:] for filename in filenames]
    
    def get(self, remotefile, localfile):
        remotefile = remotefile[:-5]+remotefile[-4:]
        return self.sftp_service.get(remotefile, localfile)


class FpingMaestroEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, sftp_service, repository, control_carga_repo, queue_service):
        super().__init__(sftp_service, control_carga_repo, queue_service)
        self.repository = repository
        self.finder = SftpFinder(SftpWrapper(sftp_service))

    def get_cargas_config(self, group_id=None):
        if group_id is not None:
            return self.repository.get_by_group_id(group_id)
        return self.repository.get()

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        return self.finder.execute(config, dt_fecha1, dt_fecha2)


class FpingMaestroEventConsumerFromConfig(EventConsumerFromConfig):
    def __init__(self, queue_service, app_container, notification_service, repository):
        super().__init__(queue_service, app_container, notification_service, repository)
        self.handler_name = LOAD_FPING_FROM_CONFIG
        self.max_check_attemps = 1