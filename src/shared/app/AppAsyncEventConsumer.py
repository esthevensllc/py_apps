from src.shared.queue.AsyncEventConsumer import AsyncEventConsumer
from src.U2000.alarmas.services.U2000AlarmasAppProvider import LOAD_ALARMAS_U2000
from src.U2000.cpu_occ_profile.services.U2000CPU_OCC_ProfileAppProvider import LOAD_CPU_OCC_PROF
from src.U2000.mem_occ_profile.services.U2000MEM_OCC_ProfileAppProvider import LOAD_MEM_OCC_PROF
from src.U2000.slot_temp_profile.services.U2000SlotTempProfileAppProvider import LOAD_SLOT_TEMP_PROF
from src.U2000.board_report.services.U2000BoardReportAppProvider import LOAD_BOARD_REPORT
from src.U2000.subrack_report.services.U2000SubrackReportAppProvider import LOAD_SUBRACK_REPORT
from src.U2000.ne_report.services.U2000NeReportAppProvider import LOAD_NE_REPORT
from src.pm.shared.services import LOAD_INTERFACE_TRAFFIC

class AppAsyncEventConsumer(AsyncEventConsumer):
    def __init__(self, queue_service, app_container):
        super().__init__(queue_service, app_container)
        # app_container.getInstance('remote_connect').useConnection('default')
        
        # handlers
        def alarmas_u2000_handler(service, event):
            service.event_handler_hxh(event)
        self.queue_handlers['u2000.alarm_5min.hxh'] = {'handler': LOAD_ALARMAS_U2000, 'callback': alarmas_u2000_handler}

        def alarmas_u2000_handler_2(service, event):
            service.event_handler(event)
        self.queue_handlers['fija.alarm_5min'] = {'handler': LOAD_ALARMAS_U2000, 'callback': alarmas_u2000_handler_2}

        def CPU_OCC_Profile_handler(service, event):
            service.event_handler_hxh(event)
        self.queue_handlers['u2000.cpu_occ_15min.hxh'] = {'handler': LOAD_CPU_OCC_PROF, 'callback': CPU_OCC_Profile_handler}

        def CPU_OCC_Profile_handler_2(service, event):
            service.event_handler(event)
        self.queue_handlers['fija.cpu_occ_15min'] = {'handler': LOAD_CPU_OCC_PROF, 'callback': CPU_OCC_Profile_handler_2}

        def MEM_OCC_Profile_handler(service, event):
            service.event_handler_hxh(event)
        self.queue_handlers['u2000.mem_occ_15min.hxh'] = {'handler': LOAD_MEM_OCC_PROF, 'callback': MEM_OCC_Profile_handler}

        def MEM_OCC_Profile_handler_2(service, event):
            service.event_handler(event)
        self.queue_handlers['fija.mem_occ_15min'] = {'handler': LOAD_MEM_OCC_PROF, 'callback': MEM_OCC_Profile_handler_2}

        def LOAD_SLOT_TEMP_PROF_handler(service, event):
            service.event_handler_hxh(event)
        self.queue_handlers['u2000.slot_temp_15min.hxh'] = {'handler': LOAD_SLOT_TEMP_PROF, 'callback': LOAD_SLOT_TEMP_PROF_handler}

        def LOAD_SLOT_TEMP_PROF_handler_2(service, event):
            service.event_handler(event)
        self.queue_handlers['fija.slot_temp_15min'] = {'handler': LOAD_SLOT_TEMP_PROF, 'callback': LOAD_SLOT_TEMP_PROF_handler_2}

        def LOAD_BOARD_REPORT_handler(service, event):
            service.event_handler_dxd(event)
        self.queue_handlers['u2000.board_rep_dia.dxd'] = {'handler': LOAD_BOARD_REPORT, 'callback': LOAD_BOARD_REPORT_handler}

        def LOAD_SUBRACK_REPORT_handler(service, event):
            service.event_handler_dxd(event)
        self.queue_handlers['u2000.subrack_rep_dia.dxd'] = {'handler': LOAD_SUBRACK_REPORT, 'callback': LOAD_SUBRACK_REPORT_handler}

        def LOAD_NE_REPORT_handler(service, event):
            service.event_handler_dxd(event)
        self.queue_handlers['u2000.ne_rep_dia.dxd'] = {'handler': LOAD_NE_REPORT, 'callback': LOAD_NE_REPORT_handler}

        def LOAD_INTERFACE_TRAFFIC_handler(service, event):
            service.event_handler(event)
        self.queue_handlers['pm.int_traffic'] = {'handler': LOAD_INTERFACE_TRAFFIC, 'callback': LOAD_INTERFACE_TRAFFIC_handler}

        self.queue_ids = self.queue_handlers.keys()