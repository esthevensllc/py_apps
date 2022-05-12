import time
import datetime
import traceback
from concurrent.futures import ThreadPoolExecutor

class AsyncEventConsumer:
    def __init__(self, queue_service, app_container):
        self.queue_service = queue_service
        self.app_container = app_container
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.queue_ids = []
        self.queue_handlers = {}
        self.queue_works = {}
        self.sleep_time = 5
        self.sleep_time_in_work = 1

    def execute(self):
        print("Event consumer")
        print(self.queue_ids)
        while True:
            queue_filtered = []
            for queue_id in self.queue_ids:
                if not self.queue_is_in_work(queue_id):
                    queue_filtered.append(queue_id)
            
            event = self.queue_service.getLastEventOf(queue_filtered)
            sleep_time = self.sleep_time if len(queue_filtered) == len(self.queue_ids) else self.sleep_time_in_work
            if not event is None:
                self.queue_works[event['queue_id']] = self.executor.submit(self.exec_queue_handler, event['queue_id'], event)
                sleep_time = self.sleep_time_in_work
            if sleep_time == self.sleep_time_in_work:
                print(f"*[{len(queue_filtered)}]")
            time.sleep(sleep_time)


    
    def queue_is_in_work(self, queue_id):
        keys = self.queue_works.keys()
        if queue_id in keys:
            return not self.queue_works[queue_id].done()
        else:
            return False
    
    def exec_queue_handler(self, queue_id, event):
        fecha_inic_exec = datetime.datetime.now()
        event_data = {'id': event['id'], 'estado': 0, 'fecha_ini_exec': fecha_inic_exec.strftime('%d/%m/%Y %H:%M:%S'), 'fecha_fin_exec': None, 'message': None}
        
        try:
            # self.exec_queue_handler(event['queue_id'], event)
            # self.queue_works[event['queue_id']] = self.executor.submit(self.exec_queue_handler, event['queue_id'], event)
            service = self.get_queue_handler(queue_id)
            #print("")
            if 'callback' in self.queue_handlers[event['queue_id']].keys():
                #print('callback')
                self.queue_handlers[event['queue_id']]['callback'](service, event)
            else:
                #print('execute')
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

    def get_queue_handler(self, queue_id):
        # return self.queue_handlers[event['queue_id']]
        bind_key = self.queue_handlers[queue_id]['handler']
        return self.app_container.getInstance(bind_key)