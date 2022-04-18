from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.shared.queue.QueueExceptions import QueueBadArguments
import datetime

class U2000NeReportEventConsumer(SimpleEventConsumer):
    def __init__(self, queue_service, service):
        super().__init__(queue_service)
        self.service = service
        self.queue_names = ['u2000.ne_rep_dia.dxd']
        self.queue_handlers = {'u2000.ne_rep_dia.dxd': self.handler_dxd}

    def handler_dxd(self, event):
        self.__guard(event)
        
        fecha = datetime.datetime.strptime(event['msg_body']['fec_ini'], '%d/%m/%Y')
        self.service.execute_dxd(fecha)

    def __guard(self, event):
        if 'fec_ini' not in event['msg_body'].keys():
            raise QueueBadArguments("Error no se encontro el atributo 'fec_ini'")
