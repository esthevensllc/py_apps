CPU_REPOSITORY = 'src.apic.hardware_usage.repository.ApicCPURepository'
MEM_REPOSITORY = 'src.apic.hardware_usage.repository.ApicMemoryRepository'
TEMP_REPOSITORY = 'src.apic.hardware_usage.repository.ApicTemperatureRepository'
NODE_REPOSITORY = 'src.apic.nodes.repository.NodeRepository'

LOAD_HARDWARE_USAGE = 'src.apic.nodes.services.LoadHardwareUsage'
LOAD_NODES = 'src.apic.nodes.services.LoadNodes'

TENANT_REPOSITORY = 'src.apic.tenants.repository.ApicTenantRepository'
TENANT_EPG_REPOSITORY = 'src.apic.tenants.repository.ApicTenantEpgRepository'
TENANT_L3OUT_REPOSITORY = 'src.apic.tenants.repository.ApicTenantL3outRepository'
LOAD_TENANTS = 'src.apic.tenants.services.LoadTenants'

INTERFACE_REPOSITORY = 'src.apic.interfaces.repository.ApicInterfaceRepository'
LOAD_ALL_INTERFACES = 'src.apic.interfaces.services.LoadAllInterfaces'
INTERFACE_INGRESS_REPOSITORY = 'src.apic.interfaces.repository.ApicInterfaceIngressRepository'
LOAD_ALL_INTERFACES_TRAFFIC = 'src.apic.interfaces.services.LoadAllInterfacesTraffic'
INTERFACE_INGRESS_ERROR_REPOSITORY = 'src.apic.interfaces.repository.ApicInterfaceIngressErrorRepository'
INTERFACE_EGRESS_REPOSITORY = 'src.apic.interfaces.repository.ApicInterfaceEgressRepository'
INTERFACE_EVENT_REPOSITORY = 'src.apic.interfaces.repository.ApicInterfaceEventRepository'
INTERFACE_FAULT_REPOSITORY = 'src.apic.interfaces.repository.ApicInterfaceFaultRepository'
INTERFACE_HEALTH_REPOSITORY = 'src.apic.interfaces.repository.ApicInterfaceHealthRepository'

LOAD_INTERFACE_EVENTS = 'src.apic.interfaces.services.LoadInterfaceEvents'
LOAD_INTERFACE_HEALTH = 'src.apic.interfaces.services.LoadInterfaceHealth'

# cpu_interfaces
PC_INTERFACES_REPOSITORY = 'src.apic.pc_interfaces.repository.ApicPCInterfaceRepository'
LOAD_PC_INTERFACES = 'src.apic.pc_interfaces.services.LoadPCInterfaces'
# # egress, ingress error y ingress
PC_INTERFACES_EGRESS_REPO = 'src.apic.pc_interfaces.repository.ApicPCInterfaceEgressRepository'
PC_INTERFACES_INGRESS_ERROR_REPO = 'src.apic.pc_interfaces.repository.ApicPCInterfaceIngressErrorRepository'
PC_INTERFACES_INGRESS_REPO = 'src.apic.pc_interfaces.repository.ApicPCInterfaceIngressRepository'
LOAD_PC_INTERFACES_TRAFFIC = 'src.apic.pc_interfaces.services.LoadPCInterfacesTraffic'

# vpc_interfaces
VPC_DOMAIN_REPOSITORY = 'src.apic.vpc_interfaces.repository.ApicVPCDomainRepository'
VPC_INTERFACES_REPOSITORY = 'src.apic.vpc_interfaces.repository.ApicVPCInterfaceRepository'
LOAD_VPC_INTERFACES = 'src.apic.vpc_interfaces.services.LoadVPCInterfaces'

class APICAppProvider:
    def __init__(self, app_container):
        def import_cpu_repository(name):
            from src.apic.hardware_usage.repository import ApicCPURepository
            oracle_db = app_container.getInstance('dboracle')
            return ApicCPURepository(oracle_db)
        app_container.bind(CPU_REPOSITORY, import_cpu_repository)

        def import_memory_repository(name):
            from src.apic.hardware_usage.repository import ApicMemoryRepository
            oracle_db = app_container.getInstance('dboracle')
            return ApicMemoryRepository(oracle_db)
        app_container.bind(MEM_REPOSITORY, import_memory_repository)

        def import_temperature_repository(name):
            from src.apic.hardware_usage.repository import ApicTemperatureRepository
            oracle_db = app_container.getInstance('dboracle')
            return ApicTemperatureRepository(oracle_db)
        app_container.bind(TEMP_REPOSITORY, import_temperature_repository)

        def import_load_hardware_usage(name):
            from src.apic.hardware_usage.services.LoadHardwareUsage import LoadHardwareUsage
            deps = app_container.getInstancesInArray([CPU_REPOSITORY, MEM_REPOSITORY, TEMP_REPOSITORY, 'apic_management'])
            return LoadHardwareUsage(*deps)
        app_container.bind(LOAD_HARDWARE_USAGE, import_load_hardware_usage)

	# carga de nodos
        def import_nodo_repository(name):
            from src.apic.nodes.repository import NodeRepository
            oracle_db = app_container.getInstance('dboracle')
            return NodeRepository(oracle_db)
        app_container.bind(NODE_REPOSITORY, import_nodo_repository)

        def import_load_nodes(name):
            from src.apic.nodes.services.LoadNodes import LoadNodes
            deps = app_container.getInstancesInArray([NODE_REPOSITORY, 'apic_management'])
            return LoadNodes(*deps)
        app_container.bind(LOAD_NODES, import_load_nodes)

        # carga de nodos
        def import_tenant_repository(name):
            from src.apic.tenants.repository import ApicTenantRepository
            oracle_db = app_container.getInstance('dboracle')
            return ApicTenantRepository(oracle_db)
        app_container.bind(TENANT_REPOSITORY, import_tenant_repository)

        def import_tenant_epg_repository(name):
            from src.apic.tenants.repository import ApicTenantEpgRepository
            oracle_db = app_container.getInstance('dboracle')
            return ApicTenantEpgRepository(oracle_db)
        app_container.bind(TENANT_EPG_REPOSITORY, import_tenant_epg_repository)

        def import_tenant_l3out_repository(name):
            from src.apic.tenants.repository import ApicTenantL3outRepository
            oracle_db = app_container.getInstance('dboracle')
            return ApicTenantL3outRepository(oracle_db)
        app_container.bind(TENANT_L3OUT_REPOSITORY, import_tenant_l3out_repository)

        def import_load_tenants(name):
            from src.apic.tenants.services.LoadTenants import LoadTenants
            deps = app_container.getInstancesInArray([TENANT_REPOSITORY, TENANT_EPG_REPOSITORY, TENANT_L3OUT_REPOSITORY, 'apic_management'])
            return LoadTenants(*deps)
        app_container.bind(LOAD_TENANTS, import_load_tenants)

        # interfaces
        def import_interface_repository(name):
            from src.apic.interfaces.repository import ApicInterfaceRepository
            oracle_db = app_container.getInstance('dboracle')
            return ApicInterfaceRepository(oracle_db)
        app_container.bind(INTERFACE_REPOSITORY, import_interface_repository)

        def import_interface_ingress_repository(name):
            from src.apic.interfaces.repository import ApicInterfaceIngressRepository
            oracle_db = app_container.getInstance('dboracle')
            return ApicInterfaceIngressRepository(oracle_db)
        app_container.bind(INTERFACE_INGRESS_REPOSITORY, import_interface_ingress_repository)

        def import_interface_ingress_error_repository(name):
            from src.apic.interfaces.repository import ApicInterfaceIngressErrorRepository
            oracle_db = app_container.getInstance('dboracle')
            return ApicInterfaceIngressErrorRepository(oracle_db)
        app_container.bind(INTERFACE_INGRESS_ERROR_REPOSITORY, import_interface_ingress_error_repository)

        def import_interface_egress_repository(name):
            from src.apic.interfaces.repository import ApicInterfaceEgressRepository
            oracle_db = app_container.getInstance('dboracle')
            return ApicInterfaceEgressRepository(oracle_db)
        app_container.bind(INTERFACE_EGRESS_REPOSITORY, import_interface_egress_repository)

        def import_interface_event_repository(name):
            from src.apic.interfaces.repository import ApicInterfaceEventRepository
            oracle_db = app_container.getInstance('dboracle')
            return ApicInterfaceEventRepository(oracle_db)
        app_container.bind(INTERFACE_EVENT_REPOSITORY, import_interface_event_repository)

        def import_interface_fault_repository(name):
            from src.apic.interfaces.repository import ApicInterfaceFaultRepository
            oracle_db = app_container.getInstance('dboracle')
            return ApicInterfaceFaultRepository(oracle_db)
        app_container.bind(INTERFACE_FAULT_REPOSITORY, import_interface_fault_repository)

        def import_interface_health_repository(name):
            from src.apic.interfaces.repository import ApicInterfaceHealthRepository
            oracle_db = app_container.getInstance('dboracle')
            return ApicInterfaceHealthRepository(oracle_db)
        app_container.bind(INTERFACE_HEALTH_REPOSITORY, import_interface_health_repository)

        def import_load_all_interfaces(name):
            from src.apic.interfaces.services.LoadAllInterfaces import LoadAllInterfaces
            deps = app_container.getInstancesInArray([INTERFACE_REPOSITORY, 'apic_management'])
            return LoadAllInterfaces(*deps)
        app_container.bind(LOAD_ALL_INTERFACES, import_load_all_interfaces)

        def import_load_all_interfaces_traffic(name):
            from src.apic.interfaces.services.LoadAllInterfacesTraffic import LoadAllInterfacesTraffic
            deps = app_container.getInstancesInArray([
                INTERFACE_INGRESS_REPOSITORY,
                INTERFACE_INGRESS_ERROR_REPOSITORY,
                INTERFACE_EGRESS_REPOSITORY,
                'apic_management'
            ])
            return LoadAllInterfacesTraffic(*deps)
        app_container.bind(LOAD_ALL_INTERFACES_TRAFFIC, import_load_all_interfaces_traffic)

        def import_load_interface_events(name):
            from src.apic.interfaces.services.LoadInterfaceEvents import LoadInterfaceEvents
            deps = app_container.getInstancesInArray([
                INTERFACE_EVENT_REPOSITORY,
                INTERFACE_FAULT_REPOSITORY,
                INTERFACE_HEALTH_REPOSITORY,
                'apic_management'
            ])
            return LoadInterfaceEvents(*deps)
        app_container.bind(LOAD_INTERFACE_EVENTS, import_load_interface_events)

        def import_load_interface_health(name):
            from src.apic.interfaces.services.LoadInterfaceHealth import LoadInterfaceHealth
            deps = app_container.getInstancesInArray([INTERFACE_HEALTH_REPOSITORY, 'apic_management'])
            return LoadInterfaceHealth(*deps)
        app_container.bind(LOAD_INTERFACE_HEALTH, import_load_interface_health)

        # pc interfaces
        def import_pc_interfaces_repository(name):
            from src.apic.pc_interfaces.repository import ApicPCInterfaceRepository
            deps = app_container.getInstancesInArray(['dboracle'])
            return ApicPCInterfaceRepository(*deps)
        app_container.bind(PC_INTERFACES_REPOSITORY, import_pc_interfaces_repository)
        
        def import_load_pc_interfaces(name):
            from src.apic.pc_interfaces.services import LoadPCInterfaces
            deps = app_container.getInstancesInArray([PC_INTERFACES_REPOSITORY, 'apic_management'])
            return LoadPCInterfaces(*deps)
        app_container.bind(LOAD_PC_INTERFACES, import_load_pc_interfaces)

        # egress, ingress error y ingress
        def import_pc_int_egress_repository(name):
            from src.apic.pc_interfaces.repository import ApicPCInterfaceEgressRepository
            return ApicPCInterfaceEgressRepository(app_container.getInstance('dboracle'))
        app_container.bind(PC_INTERFACES_EGRESS_REPO, import_pc_int_egress_repository)
        def import_pc_int_ingress_error_repository(name):
            from src.apic.pc_interfaces.repository import ApicPCInterfaceIngressErrorRepository
            return ApicPCInterfaceIngressErrorRepository(app_container.getInstance('dboracle'))
        app_container.bind(PC_INTERFACES_INGRESS_ERROR_REPO, import_pc_int_ingress_error_repository)
        def import_pc_int_ingress_repository(name):
            from src.apic.pc_interfaces.repository import ApicPCInterfaceIngressRepository
            return ApicPCInterfaceIngressRepository(app_container.getInstance('dboracle'))
        app_container.bind(PC_INTERFACES_INGRESS_REPO, import_pc_int_ingress_repository)

        def import_load_pc_interfaces_traffic(name):
            from src.apic.pc_interfaces.services import LoadPCInterfacesTraffic
            deps = app_container.getInstancesInArray([PC_INTERFACES_EGRESS_REPO, PC_INTERFACES_INGRESS_ERROR_REPO, PC_INTERFACES_INGRESS_REPO, 'apic_management'])
            return LoadPCInterfacesTraffic(*deps)
        app_container.bind(LOAD_PC_INTERFACES_TRAFFIC, import_load_pc_interfaces_traffic)

        # vpc interfaces
        def import_vpc_domain_repository(name):
            from src.apic.vpc_interfaces.repository import ApicVPCDomainRepository
            return ApicVPCDomainRepository(app_container.getInstance('dboracle'))
        app_container.bind(VPC_DOMAIN_REPOSITORY, import_vpc_domain_repository)

        def import_vpc_interfaces_repository(name):
            from src.apic.vpc_interfaces.repository import ApicVPCInterfaceRepository
            return ApicVPCInterfaceRepository(app_container.getInstance('dboracle'))
        app_container.bind(VPC_INTERFACES_REPOSITORY, import_vpc_interfaces_repository)
        
        def import_load_vpc_interfaces(name):
            from src.apic.vpc_interfaces.services import LoadVPCInterfaces
            deps = app_container.getInstancesInArray([VPC_DOMAIN_REPOSITORY, VPC_INTERFACES_REPOSITORY, 'apic_management'])
            return LoadVPCInterfaces(*deps)
        app_container.bind(LOAD_VPC_INTERFACES, import_load_vpc_interfaces)


import datetime

class BaseApicService:
    def _get_nodesid_by_topology(self, topology):
        params = {
            'query-target': 'children',
            'target-subtree-class': 'fabricNode',
            'query-target-filter': 'and(not(wcard(fabricNode.dn,"__ui_")),and(ne(fabricNode.role,"controller")))'
        }
        response = self.apic_service.get(f'node/mo/topology/pod-{topology}.json', {'params': params})
        response = response.json()
        nodes_id = list(map(lambda row: f"{row['fabricNode']['attributes']['id']}", response['imdata']))
        return nodes_id

    def _format_str_dt(self, str_date, from_format = '%Y-%m-%dT%H:%M:%S.%f%z', to_format = '%Y-%m-%d %H:%M:%S'):
        if str_date is not None and str_date != '':
            return datetime.datetime.strptime(str_date, from_format).strftime(to_format)
        return None

    def _make_template_load(self, table, main_obj, childrens):
        entity = main_obj.copy()
        bindings = {}
        for field in list(entity):
            for row in childrens:
                children_key = list(row)[0]
                for sub_field in list(row[children_key]['attributes']):
                    entity[f"{children_key}_{sub_field}"] = row[children_key]['attributes'][sub_field]

        for field in list(entity):
            try:
                if type(0.1) == type(float(entity[field])):
                    bindings[field] = 'cx_Oracle.NUMBER'
            except:
                bindings[field] = 'cx_Oracle.STRING'

        temp_attr = ', '.join(list(bindings))
        temp_binds = ', '.join(map(lambda f: f':{f}', list(bindings)))
        template = f"INSERT INTO {table}({temp_attr}) VALUES ({temp_binds})"

        table_temp = ', '.join(map(lambda f: f"{f} "+('NUMBER' if bindings[f] == 'cx_Oracle.NUMBER' else 'VARCHAR2(500)'), list(bindings)))
        table_temp = f'CREATE TABLE {table}({table_temp})'
        return template, bindings, table_temp