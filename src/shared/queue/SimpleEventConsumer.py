import time
import datetime
import traceback

class SimpleEventConsumer:
    def __init__(self, queue_service):
        self.queue_service = queue_service
        self.queue_names = []
        self.queue_handlers = {}
        self.sleep_time = 5
        self.sleep_time_in_work = 1

    def execute(self):
        print(self.queue_names)
        # last_event = None
        while True:
            event = self.queue_service.getLastEventOf(self.queue_names)
            sleep_time = self.sleep_time
            if not event is None:
                fecha_inic_exec = datetime.datetime.now()
                event_data = {'id': event['id'], 'estado': 0, 'fecha_ini_exec': fecha_inic_exec.strftime('%d/%m/%Y %H:%M:%S'), 'fecha_fin_exec': None, 'message': None}
                try:
                    self.queue_handlers[event['queue_id']](event)
                    fecha_fin_exec = datetime.datetime.now()
                    event_data['estado'] = 1
                    event_data['fecha_fin_exec'] = fecha_fin_exec.strftime('%d/%m/%Y %H:%M:%S')
                    self.queue_service.updateResultOfEvent(event_data)
                except Exception as e:
                    fecha_fin_exec = datetime.datetime.now()
                    event_data['estado'] = -1
                    event_data['fecha_fin_exec'] = fecha_fin_exec.strftime('%d/%m/%Y %H:%M:%S')
                    event_data['message'] = traceback.format_exc()
                    self.queue_service.updateResultOfEvent(event_data)
                    print(e)
                sleep_time = self.sleep_time_in_work
            time.sleep(sleep_time)
