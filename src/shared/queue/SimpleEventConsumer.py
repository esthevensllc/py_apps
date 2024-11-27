import time
import datetime
import traceback
import os

class SimpleEventConsumer:
    def __init__(self, queue_service, app_container, notification_service):
        self.queue_service = queue_service
        self.app_container = app_container
        self.notification_service = notification_service
        self.queue_ids = []
        self.queue_handlers = {}
        self.sleep_time = 5
        self.sleep_time_in_work = 1
        self.loop = True

    def execute(self):
        self.consume_events()

    def consume_events(self):
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
                except BaseException as e:
                    fecha_fin_exec = datetime.datetime.now()
                    event_data['estado'] = -1
                    event_data['fecha_fin_exec'] = fecha_fin_exec.strftime('%d/%m/%Y %H:%M:%S')
                    event_data['message'] = traceback.format_exc()
                    if len(event_data['message']) > 2000:
                        # event_data['message'] = event_data['message'][0:2000]
                        event_data['message'] = event_data['message'][-2000:]
                    self.queue_service.updateResultOfEvent(event_data)
                    self._error_handler(event, e)
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

    def execute_by_group(self, group_id=None):
        cargas = []
        if group_id == None:
            cargas = self.repository.get()
        else:
            cargas = self.repository.get_by_group_id(group_id)

        if len(cargas) == 0:
            raise Exception(f"No existen cargas")
        
        for row in cargas:
            self.config_by_queueid[row["queue_id"]] = row
        
        self.load_queue_handlers(cargas)
        self.queue_ids = list(self.queue_handlers)
        self.consume_events()

    def load_queue_handlers(self, cargas):
        def map_event(event):
            event['msg_body']['config_id'] = self.config_by_queueid[event['queue_id']]["id"]
            return event
        
        for row in cargas:
            queue_id = row["queue_id"]
            self.queue_handlers[queue_id] = {'handler': self.handler_identifier, 'callback': lambda s, e: s.event_handler(map_event(e))}
    
    def get_queue_handler(self, queue_id):
        # return self.queue_handlers[event['queue_id']]
        bind_key = self.queue_handlers[queue_id]['handler']
        return self.app_container.getInstance(bind_key)

    def _error_handler(self, event, error):
        error_message = f"{error}"
        if len(error_message) > 1000:
            error_message = error_message[0:1000]
        subject = f"PROBLEMAS EN CARGA {event['queue_id']}"
        message = f"<div>Se presento el siguiente problema: {error_message}</div>"
        message += '<table><tbody>'
        for key in list(event):
            message += f"<tr><td><strong>{key}:</strong></td><td>{event[key]}</td></tr>"
        message += '</tbody></table>'
        
        if os.getenv("APP_ENV", "prod") == "prod":
            queue_config = self.queue_service.find_config_by_id(event['queue_id'])
            if queue_config['notify_error_to'] is None:
                queue_config['notify_error_to'] = ['SOPORTE_BD']
            for group in queue_config['notify_error_to']:
                self.notification_service.send_notification(subject, message, group)

class EventConsumerFromConfig(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service, repository):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.1
        self.repository = repository
        self.loop = False
        self.carga_config = {}
        self.handler_name = None

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
            self.queue_handlers[queue_id] = {'handler': self.handler_name, 'callback': lambda s, e: s.event_handler(map_event(e))}

        self.queue_ids = list(self.queue_handlers)
        super().execute()
