import datetime as dt
from src.shared.config import STORAGE_DIR
from src.shared.carga.services import BaseCargaFromConfig

from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.zte.shared.services import LOAD_ZTE_FROM_CONFIG

class LoadZTEFromConfig(BaseCargaFromConfig):
    def __init__(self, db, repository, sftp_service, control_carga_repo):
        super().__init__(db, repository, sftp_service, control_carga_repo)
        self.base_storage_dir = f"{STORAGE_DIR}zte"


class ZTEEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, repository, sftp_service, control_carga_repo, queue_service):
        super().__init__(sftp_service, control_carga_repo, queue_service)
        self.repository = repository

    def get_cargas_config(self, group_id=None):
        if group_id is not None:
            return self.repository.get_by_group_id(group_id)
        return self.repository.get()


class ZTEEventConsumerFromConfig(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, repository, notification_service):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.1
        self.repository = repository
        self.loop = False
        self.carga_config = {}
        self.max_jobs_per_run = 10

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
            self.queue_handlers[queue_id] = {'handler': LOAD_ZTE_FROM_CONFIG, 'callback': lambda s, e: s.event_handler(map_event(e))}

        self.queue_ids = list(self.queue_handlers)
        super().execute()
