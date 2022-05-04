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