from src.shared.queue.AsyncEventConsumer import AsyncEventConsumer
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.nce.shared.services import (LOAD_CSV)

class NCEAsyncEventConsumer(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, repository, notification_service):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.5
        self.filter_med = ['PM_IG27']
        self.repository = repository
        self.medicion_by_queue = {}
        self.loop = False

        mediciones_config = self.repository.get()
        #mediciones_config = list(filter(lambda row: row['codigo_medicion'] in self.filter_med, mediciones_config))

        def map_event(event, medicion):
            event['msg_body']['mediciones'] = [self.medicion_by_queue[event['queue_id']]]
            return event

        for row in mediciones_config:
            med_gran = f"{row['codigo_medicion']}_{row['granularidad']}"
            queue_id = f'nce.{med_gran}_min'.lower()
            self.queue_handlers[queue_id] = {'handler': LOAD_CSV, 'callback': lambda s, e: s.event_handler(map_event(e, med_gran))}
            self.medicion_by_queue[queue_id] = med_gran

        self.queue_ids = list(self.queue_handlers)
