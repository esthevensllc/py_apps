from src.PSO_19.PSO_19_6748.services.PSO_19_6748AppProvider import PSO_19_6748AppProvider
from src.U2000.alarmas.services.U2000AlarmasAppProvider import U2000AlarmasAppProvider
from src.U2000.cpu_occ_profile.services.U2000CPU_OCC_ProfileAppProvider import U2000CPU_OCC_ProfileAppProvider
from src.U2000.mem_occ_profile.services.U2000MEM_OCC_ProfileAppProvider import U2000MEM_OCC_ProfileAppProvider
from src.U2000.slot_temp_profile.services.U2000SlotTempProfileAppProvider import U2000SlotTempProfileAppProvider
from src.U2000.board_report.services.U2000BoardReportAppProvider import U2000BoardReportAppProvider
from src.U2000.subrack_report.services.U2000SubrackReportAppProvider import U2000SubrackReportAppProvider
from src.U2000.ne_report.services.U2000NeReportAppProvider import U2000NeReportAppProvider
from src.PSO_19.data_fija.services.DataFijaAppProvider import DataFijaAppProvider
from src.PSO_19.PSO_19_6748_6928.services.PSO_EmpresasAppProvider import PSO_EmpresasAppProvider

from src.arbor_os.app_peer_traffic.services.ArborAppPeerTrafficAppProvider import ArborAppPeerTrafficAppProvider
from src.arbor_os.app_int_traffic.services.LoadAppInterfaceTrafficAppProvider import LoadAppInterfaceTrafficAppProvider
from src.arbor_os.router_customer_traffic.services.RouterCustomerTrafficAppProvider import RouterCustomerTrafficAppProvider
from src.arbor_os.shared.services import ArborOSAppProvider
from src.apic.shared.services import APICAppProvider
from src.pm.shared.services import PMAppProvider
from src.nce.shared.services import NCEAppProvider
from src.san.shared.services import SANAppProvider
from src.gmyd.shared.services import GMyDAppProvider
from src.med_huawei2.shared.services import MedHuawei2AppProvider
from src.control_carga.shared.services import ControlCargaAppProvider
from src.prtltx.shared.services import PrtltxAppProvider
from src.pso_cobfija.shared.services import PsoCobfijaAppProvider
from src.ana.shared.services import ANAAppProvider
from src.pronatel.shared.services import PronatelAppProvider
from src.speedtest.shared.services import SpeedTestAppProvider
from src.zte.shared.services import ZTEAppProvider
from src.U2000.shared.services import U2000AppProvider
from src.syslog.shared.services import SyslogAppProvider
from src.densidad_sites.shared.services import DensidadSitesAppProvider
from src.neteco.shared.services import NetecoAppProvider
from src.notification.shared.services import NotificationAppProvider
from src.cmd_huawei.shared.services import CmdHuaweiAppProvider
from src.nfa.shared.services import NFAAppProvider
from src.gde.shared.services import GdeAppProvider

class AppContainer:
    def __init__(self):
        self.bindings = {}
        def import_cx_oracle(name):
            from src.shared.database.OracleDB import OracleDB
            return OracleDB()
        self.bind('dboracle', import_cx_oracle)

        def import_mysql(name):
            from src.shared.database.MysqlDB import MysqlDB
            return MysqlDB()
        self.bind('dbmysql', import_mysql)

        def import_sqlserver(name):
            from src.shared.database.SQLServerDB import SQLServerDB
            return SQLServerDB()
        self.bind('sqlserver', import_sqlserver)

        def import_clickhouse(name):
            from src.shared.database.ClickHouseDB import ClickHouseDB
            return ClickHouseDB()
        self.bind('clickhouse', import_clickhouse)

        def import_db_provider(name):
            from src.shared.database.DatabaseProvider import DatabaseProvider
            return DatabaseProvider()
        self.bind('dbprovider', import_db_provider)

        def import_remote_connect(name):
            from src.shared.database.RemoteConnect import RemoteConnect
            return RemoteConnect()
        self.bind('remote_connect', import_remote_connect)

        def import_sftp_connect(name):
            from src.shared.database.SFTPConnect import SFTPConnect
            return SFTPConnect()
        self.bind('sftp_service', import_sftp_connect)

        def import_queue_service(name):
            from src.shared.queue.OracleQueueService import OracleQueueService
            dboracle = self.getInstance('dboracle')
            return OracleQueueService(dboracle)
        self.bind('queue_service', import_queue_service)

        def import_control_carga_repo(name):
            from src.shared.control_carga.ControlCargaRepository import ControlCargaRepository
            dboracle = self.getInstance('dboracle')
            return ControlCargaRepository(dboracle)
        self.bind('control_carga_repo', import_control_carga_repo)

        def import_notification_service(name):
            from src.shared.notifications.NotificationService import NotificationService
            dboracle = self.getInstance('dboracle')
            return NotificationService(dboracle)
        self.bind('notification_service', import_notification_service)

        def import_inei_repo(name):
            from src.shared.inei.IneiRepository import IneiRepository
            dboracle = self.getInstance('dboracle')
            return IneiRepository(dboracle)
        self.bind('inei_repo', import_inei_repo)

        def import_async_event_consumer(name):
            from src.shared.app.AppAsyncEventConsumer import AppAsyncEventConsumer
            queue_service = self.getInstance('queue_service')
            return AppAsyncEventConsumer(queue_service, self)
        self.bind('async_event_consumer', import_async_event_consumer)

        def import_arbor_async_event_consumer(name):
            from src.shared.app.ArborAsyncEventConsumer import ArborAsyncEventConsumer
            queue_service = self.getInstance('queue_service')
            notification_service = self.getInstance('notification_service')
            return ArborAsyncEventConsumer(queue_service, self, notification_service)
        self.bind('arbor_async_event_consumer', import_arbor_async_event_consumer)

        def import_cache(name):
            from src.shared.cache.repository import FileCacheRepository
            return FileCacheRepository()
        self.bind('cache', import_cache)

        # arbor api
        def import_arbor_api_management(name):
            from src.shared.arbor.ArborApi import ArborApi
            return ArborApi()
        self.bind('arbor_api', import_arbor_api_management)

        # apic management
        def import_apic_management(name):
            from src.shared.apic.ApicManagement import ApicManagement
            return ApicManagement()
        self.bind('apic_management', import_apic_management)

        # PM Api
        def import_pm_api(name):
            from src.shared.pm.PMApi import PMApi
            return PMApi()
        self.bind('pm_api', import_pm_api)

        # SAN Api
        def import_san_api(name):
            from src.shared.san.SanApi import SanApi
            return SanApi()
        self.bind('san_api', import_san_api)

        PSO_19_6748AppProvider(self)
        U2000AlarmasAppProvider(self)
        U2000CPU_OCC_ProfileAppProvider(self)
        U2000MEM_OCC_ProfileAppProvider(self)
        U2000SlotTempProfileAppProvider(self)
        U2000BoardReportAppProvider(self)
        U2000SubrackReportAppProvider(self)
        U2000NeReportAppProvider(self)
        DataFijaAppProvider(self)
        PSO_EmpresasAppProvider(self)
        
        ArborAppPeerTrafficAppProvider(self)
        LoadAppInterfaceTrafficAppProvider(self)
        RouterCustomerTrafficAppProvider(self)
        ArborOSAppProvider(self)
        APICAppProvider(self)
        PMAppProvider(self)
        NCEAppProvider(self)
        SANAppProvider(self)
        GMyDAppProvider(self)
        MedHuawei2AppProvider(self)
        ControlCargaAppProvider(self)
        PrtltxAppProvider(self)
        PsoCobfijaAppProvider(self)
        ANAAppProvider(self)
        PronatelAppProvider(self)
        SpeedTestAppProvider(self)
        ZTEAppProvider(self)
        U2000AppProvider(self)
        SyslogAppProvider(self)
        DensidadSitesAppProvider(self)
        NetecoAppProvider(self)
        NotificationAppProvider(self)
        CmdHuaweiAppProvider(self)
        NFAAppProvider(self)
        GdeAppProvider(self)

    def bind(self, namespace, callback):
        self.bindings[namespace] = {'instance': None, 'callback': callback}

    def getInstance(self, nameespace, new=False):
        if nameespace in self.bindings.keys():
            instance = self.bindings[nameespace]['instance']
            if instance == None or new:
                builder = self.bindings[nameespace]
                instance = builder['callback'](nameespace)
                self.bindings[nameespace]['instance'] = instance
            return instance
        else:
            raise Exception(f"Error: Nombre de instancia '{nameespace}' no valida")
    
    def getInstancesInArray(self, namespaces):
        instances = []
        for name in namespaces:
            instances.append(self.getInstance(name))
        return instances

    def close_connections(self):
        if 'dboracle' in self.bindings.keys():
            self.getInstance('dboracle').__disconnect__()

        if 'dbmysql' in self.bindings.keys():
            self.getInstance('dbmysql').__disconnect__()

        if 'remote_connect' in self.bindings.keys():
            self.getInstance('remote_connect').disconnect()
