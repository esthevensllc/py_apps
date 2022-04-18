from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.shared.queue.QueueExceptions import QueueBadArguments
import datetime

class U2000SlotTempProfileEventConsumer(SimpleEventConsumer):
    def __init__(self, queue_service, service):
        super().__init__(queue_service)
        self.service = service
        self.queue_names = ['u2000.slot_temp_15min.hxh']
        self.queue_handlers = {'u2000.slot_temp_15min.hxh': self.handler_hxh}

    def handler_hxh(self, event):
        self.__guard(event)
        
        fecha = datetime.datetime.strptime(event['msg_body']['fec_ini'], '%d/%m/%Y %H')
        self.service.execute_hxh(fecha)

    def __guard(self, event):
        if 'fec_ini' not in event['msg_body'].keys():
            raise QueueBadArguments("Error no se encontro el atributo 'fec_ini'")