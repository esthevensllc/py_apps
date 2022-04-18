REPOSITORY = 'arbor_os.app_peer_traffic.ApplicationPeerTrafficRepository'
LOAD_APP_PEER_TRAFFIC = 'arbor_os.app_peer_trafic.LoadAppPeerTraffic'

class ArborAppPeerTrafficAppProvider:
    def __init__(self, app_container):
        def import_repository(name):
            from src.arbor_os.app_peer_traffic.repository import ApplicationPeerTrafficRepository
            oracle_db = app_container.getInstance('dboracle')
            return ApplicationPeerTrafficRepository(oracle_db)
        app_container.bind(REPOSITORY, import_repository)

        def import_LoadAppPeerTraffic(name):
            from src.arbor_os.app_peer_traffic.services.LoadAppPeerTraffic import LoadAppPeerTraffic
            dependencies = app_container.getInstancesInArray([REPOSITORY, 'arbor_api'])
            return LoadAppPeerTraffic(*dependencies)
        app_container.bind(LOAD_APP_PEER_TRAFFIC, import_LoadAppPeerTraffic)
