REPOSITORY = 'arbor_os.app_int_traffic.AppInterfaceTrafficRepository'
LOAD_APP_INT_TRAFFIC = 'arbor_os.app_peer_trafic.LoadAppInterfaceTraffic'

class LoadAppInterfaceTrafficAppProvider:
    def __init__(self, app_container):
        def import_repository(name):
            from src.arbor_os.app_int_traffic.repository import AppInterfaceTrafficRepository
            oracle_db = app_container.getInstance('dboracle')
            return AppInterfaceTrafficRepository(oracle_db)
        app_container.bind(REPOSITORY, import_repository)

        def import_LoadAppInterfaceTraffic(name):
            from src.arbor_os.app_int_traffic.services.LoadAppInterfaceTraffic import LoadAppInterfaceTraffic
            dependencies = app_container.getInstancesInArray([REPOSITORY, 'arbor_api'])
            return LoadAppInterfaceTraffic(*dependencies)
        app_container.bind(LOAD_APP_INT_TRAFFIC, import_LoadAppInterfaceTraffic)