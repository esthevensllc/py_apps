REPOSITORY = 'arbor_os.router_customer_traffic.RouterCustomerTrafficRepository'
LOAD_ROUTER_CUST_TRAFFIC = 'arbor_os.router_customer_traffic.LoadRouterCustomerTraffic'

class RouterCustomerTrafficAppProvider:
    def __init__(self, app_container):
        def import_repository(name):
            from src.arbor_os.router_customer_traffic.repository import RouterCustomerTrafficRepository
            oracle_db = app_container.getInstance('dboracle')
            return RouterCustomerTrafficRepository(oracle_db)
        app_container.bind(REPOSITORY, import_repository)

        def import_LoadRouterCustomerTraffic(name):
            from src.arbor_os.router_customer_traffic.services.LoadRouterCustomerTraffic import LoadRouterCustomerTraffic
            dependencies = app_container.getInstancesInArray([REPOSITORY, 'arbor_api'])
            return LoadRouterCustomerTraffic(*dependencies)
        app_container.bind(LOAD_ROUTER_CUST_TRAFFIC, import_LoadRouterCustomerTraffic)