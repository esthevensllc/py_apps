PHYSICAL_LM_REPO = 'src.san.physical_link_manager.SANPhysicalLM'
LOAD_PHYSICAL_LM = 'src.san.physical_link_manager.LoadPhysicalLM'

SERVICE_MANAGER_REPO = 'src.san.service_manager.ServiceManagerRepository'
SERVICE_MANAGER_SITE_REPO = 'src.san.service_manager.ServiceManagerSiteRepository'
LOAD_SERVICE_MANAGER = 'src.san.service_manager.LoadServiceManager'

NETWORK_ELEMENT_REPO = 'src.san.network_element.NetworkElementRepository'
NETWORK_ELEMENT_SHELF_REPO = 'src.san.network_element.NetworkElementShelfRepository'
LOAD_NETWORK_ELEMENT = 'src.san.network_element.LoadNetworkElement'

L3_ACCESS_INT_REPO = 'src.san.network_element.L3AccessInterfaceRepository'
LOAD_L3_ACCESS_INT = 'src.san.network_element.LoadL3AccessInterface'

LAG_INTERFACE_REPO = 'src.san.lag_interface.LagInterfaceRepository'
LAG_INTERFACE_PORT_REPO = 'src.san.lag_interface.LagInterfacePortRepository'
LOAD_LAG_INTERFACES = 'src.san.lag_interface.LoadLagInterfaces'

NETWORK_INTERFACE_REPO = 'src.san.network_interface.NetworkInterfaceRepository'
LOAD_NETWORK_INTERFACES = 'src.san.network_interface.LoadNetworkInterfaces'

NOT_DISC_PHYSICAL_LM_REPO = 'src.san.not_disc_physical_lm.NotDiscPhysicalLMRepository'
LOAD_NOT_DISC_PHYSICAL_LM = 'src.san.not_disc_physical_lm.LoadNetworkInterfaces'

VPRN_REPO = 'src.san.vprn.VPRNRepository'
VPRN_SITE_REPO = 'src.san.vprn.VprnSiteRepository'
LOAD_VPRN = 'src.san.vprn.LoadVPRN'

INTERFACE_STATS_REPO = 'src.san.interface_stats.InterfaceStatsRepository'
LOAD_INTERFACE_STATS = 'src.san.interface_stats.LoadInterfaceStats'

LOAD_CONFIG_REPO = 'src.san.shared_load.SanConfigRepository'
LOAD_DATA_FROM_CONFIG = 'src.san.shared_load.LoadDataFromConfig'
EVENT_CONSUMER = 'src.san.shared.SANAsyncEventConsumer'
EVENT_PRODUCER = 'src.san.shared_load.SanEventProducer'

# SAM 5620
LOAD_PHYSICAL_LM_SAM5620 = 'src.san.physical_link_manager.LoadPhysicalLM_sam5620'
LOAD_SERVICE_MANAGER_SAM5620 = 'src.san.service_manager.LoadServiceManager_sam5620'
LOAD_NETWORK_ELEMENT_SAM5620 = 'src.san.network_element.LoadNetworkElement_sam5620'
LOAD_L3_ACCESS_INT_SAM5620 = 'src.san.network_element.LoadL3AccessInterface_sam5620'
LOAD_LAG_INTERFACES_SAM5620 = 'src.san.lag_interface.LoadLagInterfaces_sam5620'
LOAD_NETWORK_INTERFACES_SAM5620 = 'src.san.network_interface.LoadNetworkInterfaces_sam5620'
LOAD_NOT_DISC_PHYSICAL_LM_SAM5620 = 'src.san.not_disc_physical_lm.LoadNetworkInterfaces_sam5620'
LOAD_VPRN_SAM5620 = 'src.san.vprn.LoadVPRN_sam5620'

SAN_INVENTARIO_EVENT_CONSUMER = "src.san.shared.SANInventarioEventConsumer"

class SANAppProvider:
    def __init__(self, app_container):
        def import_physical_lm_repo(name):
            from src.san.physical_link_manager.repository import SANPhysicalLMRepository
            return SANPhysicalLMRepository(app_container.getInstance('dboracle'))
        app_container.bind(PHYSICAL_LM_REPO, import_physical_lm_repo)

        def import_load_physical_lm(name):
            from src.san.physical_link_manager.services.LoadPhysicalLM import LoadPhysicalLM
            deps = app_container.getInstancesInArray([PHYSICAL_LM_REPO, 'san_api', 'control_carga_repo'])
            deps.append("san")
            return LoadPhysicalLM(*deps)
        app_container.bind(LOAD_PHYSICAL_LM, import_load_physical_lm)

        def import_service_manager_repo(name):
            from src.san.service_manager.repository import ServiceManagerRepository
            return ServiceManagerRepository(app_container.getInstance('dboracle'))
        app_container.bind(SERVICE_MANAGER_REPO, import_service_manager_repo)
        def import_service_manager_site_repo(name):
            from src.san.service_manager.repository import ServiceManagerSiteRepository
            return ServiceManagerSiteRepository(app_container.getInstance('dboracle'))
        app_container.bind(SERVICE_MANAGER_SITE_REPO, import_service_manager_site_repo)
        def import_load_service_manager(name):
            from src.san.service_manager.services import LoadServiceManager
            deps = app_container.getInstancesInArray([SERVICE_MANAGER_REPO, SERVICE_MANAGER_SITE_REPO, 'san_api', 'control_carga_repo'])
            deps.append("san")
            return LoadServiceManager(*deps)
        app_container.bind(LOAD_SERVICE_MANAGER, import_load_service_manager)

        def import_network_element_repo(name):
            from src.san.network_element.repository import NetworkElementRepository
            return NetworkElementRepository(app_container.getInstance('dboracle'))
        app_container.bind(NETWORK_ELEMENT_REPO, import_network_element_repo)
        def import_network_element_shelf_repo(name):
            from src.san.network_element.repository import NetworkElementShelfRepository
            return NetworkElementShelfRepository(app_container.getInstance('dboracle'))
        app_container.bind(NETWORK_ELEMENT_SHELF_REPO, import_network_element_shelf_repo)
        def import_load_network_element(name):
            from src.san.network_element.services import LoadNetworkElement
            deps = app_container.getInstancesInArray([NETWORK_ELEMENT_REPO, NETWORK_ELEMENT_SHELF_REPO, 'san_api', 'control_carga_repo'])
            deps.append("san")
            return LoadNetworkElement(*deps)
        app_container.bind(LOAD_NETWORK_ELEMENT, import_load_network_element)

        def import_l3_access_int_repo(name):
            from src.san.l3_access_int.repository import L3AccessInterfaceRepository
            return L3AccessInterfaceRepository(app_container.getInstance('dboracle'))
        app_container.bind(L3_ACCESS_INT_REPO, import_l3_access_int_repo)
        def import_load_l3_access_int(name):
            from src.san.l3_access_int.services import LoadL3AccessInterface
            deps = app_container.getInstancesInArray([L3_ACCESS_INT_REPO, 'san_api', 'control_carga_repo'])
            deps.append("san")
            return LoadL3AccessInterface(*deps)
        app_container.bind(LOAD_L3_ACCESS_INT, import_load_l3_access_int)

        def import_lag_interface_repo(name):
            from src.san.lag_interface.repository import LagInterfaceRepository
            return LagInterfaceRepository(app_container.getInstance('dboracle'))
        app_container.bind(LAG_INTERFACE_REPO, import_lag_interface_repo)
        def import_lag_interface_port_repo(name):
            from src.san.lag_interface.repository import LagInterfacePortRepository
            return LagInterfacePortRepository(app_container.getInstance('dboracle'))
        app_container.bind(LAG_INTERFACE_PORT_REPO, import_lag_interface_port_repo)
        def import_load_lag_interfaces(name):
            from src.san.lag_interface.services import LoadLagInterfaces
            deps = app_container.getInstancesInArray([LAG_INTERFACE_REPO, LAG_INTERFACE_PORT_REPO, 'san_api', 'control_carga_repo'])
            deps.append("san")
            return LoadLagInterfaces(*deps)
        app_container.bind(LOAD_LAG_INTERFACES, import_load_lag_interfaces)

        def import_network_interface_repo(name):
            from src.san.network_interface.repository import NetworkInterfaceRepository
            return NetworkInterfaceRepository(app_container.getInstance('dboracle'))
        app_container.bind(NETWORK_INTERFACE_REPO, import_network_interface_repo)
        def import_load_network_interfaces(name):
            from src.san.network_interface.services import LoadNetworkInterfaces
            deps = app_container.getInstancesInArray([NETWORK_INTERFACE_REPO, 'san_api', 'control_carga_repo'])
            deps.append("san")
            return LoadNetworkInterfaces(*deps)
        app_container.bind(LOAD_NETWORK_INTERFACES, import_load_network_interfaces)

        def import_not_disc_physical_lm_repo(name):
            from src.san.not_disc_physical_lm.repository import NotDiscPhysicalLMRepository
            return NotDiscPhysicalLMRepository(app_container.getInstance('dboracle'))
        app_container.bind(NOT_DISC_PHYSICAL_LM_REPO, import_not_disc_physical_lm_repo)
        def import_load_not_disc_physical_lm(name):
            from src.san.not_disc_physical_lm.services import LoadNotDiscPhysicalLM
            deps = app_container.getInstancesInArray([NOT_DISC_PHYSICAL_LM_REPO, 'san_api', 'control_carga_repo'])
            deps.append("san")
            return LoadNotDiscPhysicalLM(*deps)
        app_container.bind(LOAD_NOT_DISC_PHYSICAL_LM, import_load_not_disc_physical_lm)

        def import_vprn_repo(name):
            from src.san.vprn.repository import VPRNRepository
            return VPRNRepository(app_container.getInstance('dboracle'))
        app_container.bind(VPRN_REPO, import_vprn_repo)
        def import_vprn_site_repo(name):
            from src.san.vprn.repository import VprnSiteRepository
            return VprnSiteRepository(app_container.getInstance('dboracle'))
        app_container.bind(VPRN_SITE_REPO, import_vprn_site_repo)
        def import_load_vprn(name):
            from src.san.vprn.services import LoadVPRN
            deps = app_container.getInstancesInArray([VPRN_REPO, VPRN_SITE_REPO, 'san_api', 'control_carga_repo'])
            deps.append("san")
            return LoadVPRN(*deps)
        app_container.bind(LOAD_VPRN, import_load_vprn)

        def import_interface_stats_repo(name):
            from src.san.interface_stats.repository import InterfaceStatsRepository
            return InterfaceStatsRepository(app_container.getInstance('dboracle'))
        app_container.bind(INTERFACE_STATS_REPO, import_interface_stats_repo)
        def import_load_interface_stats(name):
            from src.san.interface_stats.services import LoadInterfaceStats
            deps = app_container.getInstancesInArray([INTERFACE_STATS_REPO, 'san_api'])
            return LoadInterfaceStats(*deps)
        app_container.bind(LOAD_INTERFACE_STATS, import_load_interface_stats)

        def import_load_config_repo(name):
            from src.san.shared_load.repository import SanConfigRepository
            return SanConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(LOAD_CONFIG_REPO, import_load_config_repo)
        def import_load_data_from_config(name):
            from src.san.shared_load.services import LoadDataFromConfig
            deps = app_container.getInstancesInArray(['dboracle', LOAD_CONFIG_REPO, 'san_api', 'control_carga_repo'])
            return LoadDataFromConfig(*deps)
        app_container.bind(LOAD_DATA_FROM_CONFIG, import_load_data_from_config)

        def import_event_consumer(name):
            from src.san.shared.services import SANAsyncEventConsumer
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(LOAD_CONFIG_REPO)
            notification_service = app_container.getInstance('notification_service')
            return SANAsyncEventConsumer(queue_service, app_container, repository, notification_service)
        app_container.bind(EVENT_CONSUMER, import_event_consumer)

        def import_event_producer(name):
            from src.san.shared_load.services import SanEventProducer
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(LOAD_CONFIG_REPO)
            return SanEventProducer(repository, queue_service)
        app_container.bind(EVENT_PRODUCER, import_event_producer)

        # SAM 5620
        def import_load_physical_lm_sam5620(name):
            from src.san.physical_link_manager.services.LoadPhysicalLM import LoadPhysicalLM
            deps = app_container.getInstancesInArray([PHYSICAL_LM_REPO, 'san_api', 'control_carga_repo'])
            deps[0].use('sam_5620')
            deps[1].use('sam_5620')
            deps.append("sam_5620")
            return LoadPhysicalLM(*deps)
        app_container.bind(LOAD_PHYSICAL_LM_SAM5620, import_load_physical_lm_sam5620)

        def import_load_service_manager_sam5620(name):
            from src.san.service_manager.services import LoadServiceManager
            deps = app_container.getInstancesInArray([SERVICE_MANAGER_REPO, SERVICE_MANAGER_SITE_REPO, 'san_api', 'control_carga_repo'])
            deps[0].use('sam_5620')
            deps[1].use('sam_5620')
            deps[2].use('sam_5620')
            deps.append("sam_5620")
            return LoadServiceManager(*deps)
        app_container.bind(LOAD_SERVICE_MANAGER_SAM5620, import_load_service_manager_sam5620)

        def import_load_network_element_sam5620(name):
            from src.san.network_element.services import LoadNetworkElement
            deps = app_container.getInstancesInArray([NETWORK_ELEMENT_REPO, NETWORK_ELEMENT_SHELF_REPO, 'san_api', 'control_carga_repo'])
            deps[0].use('sam_5620')
            deps[1].use('sam_5620')
            deps[2].use('sam_5620')
            deps.append("sam_5620")
            return LoadNetworkElement(*deps)
        app_container.bind(LOAD_NETWORK_ELEMENT_SAM5620, import_load_network_element_sam5620)

        def import_load_l3_access_int_sam5620(name):
            from src.san.l3_access_int.services import LoadL3AccessInterface
            deps = app_container.getInstancesInArray([L3_ACCESS_INT_REPO, 'san_api', 'control_carga_repo'])
            deps[0].use('sam_5620')
            deps[1].use('sam_5620')
            deps.append("sam_5620")
            return LoadL3AccessInterface(*deps)
        app_container.bind(LOAD_L3_ACCESS_INT_SAM5620, import_load_l3_access_int_sam5620)

        def import_load_lag_interfaces_sam5620(name):
            from src.san.lag_interface.services import LoadLagInterfaces
            deps = app_container.getInstancesInArray([LAG_INTERFACE_REPO, LAG_INTERFACE_PORT_REPO, 'san_api', 'control_carga_repo'])
            deps[0].use('sam_5620')
            deps[1].use('sam_5620')
            deps[2].use('sam_5620')
            deps.append("sam_5620")
            return LoadLagInterfaces(*deps)
        app_container.bind(LOAD_LAG_INTERFACES_SAM5620, import_load_lag_interfaces_sam5620)

        def import_load_network_interfaces_sam5620(name):
            from src.san.network_interface.services import LoadNetworkInterfaces
            deps = app_container.getInstancesInArray([NETWORK_INTERFACE_REPO, 'san_api', 'control_carga_repo'])
            deps[0].use('sam_5620')
            deps[1].use('sam_5620')
            deps.append("sam_5620")
            return LoadNetworkInterfaces(*deps)
        app_container.bind(LOAD_NETWORK_INTERFACES_SAM5620, import_load_network_interfaces_sam5620)

        def import_load_not_disc_physical_lm_sam5620(name):
            from src.san.not_disc_physical_lm.services import LoadNotDiscPhysicalLM
            deps = app_container.getInstancesInArray([NOT_DISC_PHYSICAL_LM_REPO, 'san_api', 'control_carga_repo'])
            deps[0].use('sam_5620')
            deps[1].use('sam_5620')
            deps.append("sam_5620")
            return LoadNotDiscPhysicalLM(*deps)
        app_container.bind(LOAD_NOT_DISC_PHYSICAL_LM_SAM5620, import_load_not_disc_physical_lm_sam5620)

        def import_load_vprn_sam5620(name):
            from src.san.vprn.services import LoadVPRN
            deps = app_container.getInstancesInArray([VPRN_REPO, VPRN_SITE_REPO, 'san_api', 'control_carga_repo'])
            deps[0].use('sam_5620')
            deps[1].use('sam_5620')
            deps[2].use('sam_5620')
            deps.append("sam_5620")
            return LoadVPRN(*deps)
        app_container.bind(LOAD_VPRN_SAM5620, import_load_vprn_sam5620)

        def import_san_inventario_event_consumer(name):
            queue_service = app_container.getInstance('queue_service')
            notification_service = app_container.getInstance('notification_service')
            return SANInventarioEventConsumer(queue_service, app_container, notification_service)
        app_container.bind(SAN_INVENTARIO_EVENT_CONSUMER, import_san_inventario_event_consumer)


class BaseSanService:
    def _map_entryset_to_row(self, children_set, with_name=False, map_with=[]):
        registros = []
        entry_name = None
        for children in children_set:
            entry_name = children.tag.split('}')[1]
            entry_name = entry_name.replace('.', '_')
            row_to_add = {}
            for attr in children:
                attr_name = attr.tag.split('}')[1]
                if attr_name == 'children-Set':
                    subrows = self._map_entryset_to_row(attr, True)
                    # name = 'children-Set' if name is None else name
                    for sub_child in subrows:
                        name = list(sub_child)[0]
                        if name not in list(row_to_add):
                            row_to_add[name] = []
                        row_to_add[name].append(sub_child[name])
                else:
                    row_to_add[attr_name] = attr.text

            if len(map_with) > 0:
                plain_row = []
                for field in map_with:
                    plain_row.append(row_to_add[field])
                row_to_add = plain_row

            if with_name:
                registros.append({entry_name: row_to_add})
            else:
                registros.append(row_to_add)
        return registros


from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
import json

class SANAsyncEventConsumer(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, repository, notification_service):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.5
        self.repository = repository
        self.notification_service = notification_service
        self.configid_by_queue = {}
        self.loop = False

        cargas_config = self.repository.get()

        def map_event(event):
            event['msg_body']['config_id'] = self.configid_by_queue[event['queue_id']]
            return event

        for row in cargas_config:
            self.configid_by_queue[row['queue_id']] = row['id']
            self.queue_handlers[row['queue_id']] = {
                'handler': LOAD_DATA_FROM_CONFIG,
                'callback': lambda s, e: s.event_handler(map_event(e))
            }
        self.queue_ids = list(self.queue_handlers)

    def __error_handler(self, event, error):
        subject = f"PROBLEMAS EN CARGA {event['queue_id']}"
        message = f"Se presento el siguiente problema: {error}"
        for key in list(event):
            message += f"\n{key}: {event[key]}"
        
        queue_config = self.queue_service.find_config_by_id(event['queue_id'])
        if queue_config['notify_error_to'] is None:
            queue_config['notify_error_to'] = ['SOPORTE_BD']
        for group in queue_config['notify_error_to']:
            self.notification_service.send_notification(subject, message, group)


class SANInventarioEventConsumer(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.1
        self.loop = False

        oracle = app_container.getInstance("dboracle")
        oracle.callproc("PK_PADM_QUEUE.SP_SAM_INVENTARIO_PRODUCER", {})

    def execute(self, group_id):
        if group_id == "san":
            self.queue_handlers["san.load_network_element"] = {'handler': LOAD_NETWORK_ELEMENT, 'callback': lambda s, e: s.event_handler(e)}
            self.queue_handlers["san.l3_access_int"] = {'handler': LOAD_L3_ACCESS_INT, 'callback': lambda s, e: s.event_handler(e)}
            self.queue_handlers["san.lag_interface"] = {'handler': LOAD_LAG_INTERFACES, 'callback': lambda s, e: s.event_handler(e)}
            self.queue_handlers["san.network_interface"] = {'handler': LOAD_NETWORK_INTERFACES, 'callback': lambda s, e: s.event_handler(e)}
            self.queue_handlers["san.not_disc_physical_lm"] = {'handler': LOAD_NOT_DISC_PHYSICAL_LM, 'callback': lambda s, e: s.event_handler(e)}
            self.queue_handlers["san.physical_lm"] = {'handler': LOAD_PHYSICAL_LM, 'callback': lambda s, e: s.event_handler(e)}
            self.queue_handlers["san.service_manager"] = {'handler': LOAD_SERVICE_MANAGER, 'callback': lambda s, e: s.event_handler(e)}
            self.queue_handlers["san.vprn"] = {'handler': LOAD_VPRN, 'callback': lambda s, e: s.event_handler(e)}
        elif group_id == "sam_5620":
            self.queue_handlers["sam_5620.load_network_element"] = {'handler': LOAD_NETWORK_ELEMENT_SAM5620, 'callback': lambda s, e: s.event_handler(e)}
            self.queue_handlers["sam_5620.l3_access_int"] = {'handler': LOAD_L3_ACCESS_INT_SAM5620, 'callback': lambda s, e: s.event_handler(e)}
            self.queue_handlers["sam_5620.lag_interface"] = {'handler': LOAD_LAG_INTERFACES_SAM5620, 'callback': lambda s, e: s.event_handler(e)}
            self.queue_handlers["sam_5620.network_interface"] = {'handler': LOAD_NETWORK_INTERFACES_SAM5620, 'callback': lambda s, e: s.event_handler(e)}
            self.queue_handlers["sam_5620.not_disc_physical_lm"] = {'handler': LOAD_NOT_DISC_PHYSICAL_LM_SAM5620, 'callback': lambda s, e: s.event_handler(e)}
            self.queue_handlers["sam_5620.physical_lm"] = {'handler': LOAD_PHYSICAL_LM_SAM5620, 'callback': lambda s, e: s.event_handler(e)}
            self.queue_handlers["sam_5620.service_manager"] = {'handler': LOAD_SERVICE_MANAGER_SAM5620, 'callback': lambda s, e: s.event_handler(e)}
            self.queue_handlers["sam_5620.vprn"] = {'handler': LOAD_VPRN_SAM5620, 'callback': lambda s, e: s.event_handler(e)}
        else:
            raise Exception("El grupo no existe")

        self.queue_ids = list(self.queue_handlers.keys())
        super().execute()
