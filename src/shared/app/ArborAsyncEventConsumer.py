from src.shared.queue.AsyncEventConsumer import AsyncEventConsumer
from src.arbor_os.app_peer_traffic.services.ArborAppPeerTrafficAppProvider import LOAD_APP_PEER_TRAFFIC
from src.arbor_os.app_int_traffic.services.LoadAppInterfaceTrafficAppProvider import LOAD_APP_INT_TRAFFIC
from src.arbor_os.router_customer_traffic.services.RouterCustomerTrafficAppProvider import LOAD_ROUTER_CUST_TRAFFIC
from src.arbor_os.shared.services import (LOAD_APP_CUST_TRAFFIC, LOAD_CUST_TRAFFIC, LOAD_ALERTS)

class ArborAsyncEventConsumer(AsyncEventConsumer):
    def __init__(self, queue_service, app_container):
        super().__init__(queue_service, app_container)
        self.loop = True

        def LOAD_APP_PEER_TRAFFIC_handler(service, event):
            service.event_handler(event)
        self.queue_handlers['arbor.app_peer'] = {'handler': LOAD_APP_PEER_TRAFFIC, 'callback': LOAD_APP_PEER_TRAFFIC_handler}

        def LOAD_APP_INT_TRAFFIC_handler(service, event):
            service.event_handler(event)
        self.queue_handlers['arbor.app_int'] = {'handler': LOAD_APP_INT_TRAFFIC, 'callback': LOAD_APP_INT_TRAFFIC_handler}

        def LOAD_ROUTER_CUST_TRAFFIC_handler(service, event):
            service.event_handler(event)
        self.queue_handlers['arbor.router_customer'] = {'handler': LOAD_ROUTER_CUST_TRAFFIC, 'callback': LOAD_ROUTER_CUST_TRAFFIC_handler}

        def LOAD_APP_CUST_TRAFFIC_handler(service, event):
            service.event_handler(event)
        self.queue_handlers['arbor.app_customer'] = {'handler': LOAD_APP_CUST_TRAFFIC, 'callback': LOAD_APP_CUST_TRAFFIC_handler}

        def LOAD_CUST_TRAFFIC_handler(service, event):
            service.event_handler(event)
        self.queue_handlers['arbor.customer'] = {'handler': LOAD_CUST_TRAFFIC, 'callback': LOAD_CUST_TRAFFIC_handler}

        def LOAD_ALERTS_handler(service, event):
            service.event_handler(event)
        self.queue_handlers['arbor.alerts'] = {'handler': LOAD_ALERTS, 'callback': LOAD_ALERTS_handler}

        self.queue_ids = self.queue_handlers.keys()