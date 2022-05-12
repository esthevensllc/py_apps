import time
import datetime
import traceback

class SimpleEventConsumer:
    def __init__(self, queue_service, app_container):
        self.queue_service = queue_service
        self.app_container = app_container
        self.queue_ids = []
        self.queue_handlers = {}
        self.sleep_time = 5
        self.sleep_time_in_work = 1
        self.loop = True

    def execute(self):
        print(self.queue_ids)
        # last_event = None
        counter_without_work = 0
        while True:
            event = self.queue_service.getLastEventOf(self.queue_ids)
            sleep_time = self.sleep_time
            if not event is None:
                fecha_inic_exec = datetime.datetime.now()
                event_data = {'id': event['id'], 'estado': 0, 'fecha_ini_exec': fecha_inic_exec.strftime('%d/%m/%Y %H:%M:%S'), 'fecha_fin_exec': None, 'message': None}
                try:
                    #self.queue_handlers[event['queue_id']](event)
                    service = self.get_queue_handler(event['queue_id'])
                    if 'callback' in self.queue_handlers[event['queue_id']].keys():
                        self.queue_handlers[event['queue_id']]['callback'](service, event)
                    else:
                        service.execute(event)

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
                counter_without_work = 0
            else:
                counter_without_work += 1
            if not self.loop and counter_without_work >=4:
                time.sleep(sleep_time)
                break
            else:
                time.sleep(sleep_time)
                print(counter_without_work)
    
    def get_queue_handler(self, queue_id):
        # return self.queue_handlers[event['queue_id']]
        bind_key = self.queue_handlers[queue_id]['handler']
        return self.app_container.getInstance(bind_key)