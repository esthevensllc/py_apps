INTERFACE_TRAFFIC_REPO = 'pm.interface_traffic.InterfacesTrafficRepository'
LOAD_INTERFACE_TRAFFIC = 'pm.interface_traffic.LoadInterfaceTraffic'

class PMAppProvider:
    def __init__(self, app_container):
        def import_interface_traffic_repository(name):
            from src.pm.interface_traffic.repository import InterfacesTrafficRepository
            oracle_db = app_container.getInstance('dboracle')
            return InterfacesTrafficRepository(oracle_db)
        app_container.bind(INTERFACE_TRAFFIC_REPO, import_interface_traffic_repository)

        def import_load_interface_traffic_repository(name):
            from src.pm.interface_traffic.services.LoadInterfaceTraffic import LoadInterfaceTraffic
            dependencies = app_container.getInstancesInArray([INTERFACE_TRAFFIC_REPO, 'pm_api'])
            return LoadInterfaceTraffic(*dependencies)
        app_container.bind(LOAD_INTERFACE_TRAFFIC, import_load_interface_traffic_repository)
