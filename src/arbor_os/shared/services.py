APP_CUST_REPOSITORY = 'arbor_os.app_customer_traffic.AppCustomerTrafficRepository'
LOAD_APP_CUST_TRAFFIC = 'arbor_os.app_customer_traffic.LoadAppCustomerTraffic'

CUST_REPOSITORY = 'arbor_os.customer_traffic.CustomerTrafficRepository'
LOAD_CUST_TRAFFIC = 'arbor_os.customer_traffic.LoadCustomerTraffic'

ALERT_REPOSITORY = 'arbor_os.alerts.AlertRepository'
ALERT_SRCPREFIXES_REPOSITORY = 'arbor_os.alerts.AlertSrcprefixes'
ALERT_COUNTRY_REPOSITORY = 'arbor_os.alerts.AlertCountryRepository'
ALERT_PATTERN_REPOSITORY = 'arbor_os.alerts.AlertPatternRepository'
LOAD_ALERTS = 'arbor_os.alerts.LoadAlerts'

MANAGED_OBJECT_REPOSITORY = 'arbor_os.managed_object.ReloadManagedRepository'
RELOAD_MANAGED_OBJECT = 'arbor_os.managed_object.ReloadManagedObject'

MITIGATION_REPOSITORY = 'arbor_os.mitigations.MitigationRepository'
LOAD_MITIGATIONS = 'arbor_os.mitigations.LoadMitigations'

ARBOR_CONFIG_REPO = "arbor_os.reports.InMemoryArborConfigRepository"
LOAD_ARBOR_FROM_CONFIG = "arbor_os.reports.LoadArborFromConfig"
EVENT_CONSUMER_FROM_CONFIG = 'arbor_os.reports.ArborEventConsumerFromConfig'
EVENT_PRODUCER_FROM_CONFIG = 'arbor_os.reports.ArborEventProducerFromConfig'

class ArborOSAppProvider:
    def __init__(self, app_container):
        def import_app_cust_repository(name):
            from src.arbor_os.app_customer_traffic.repository import AppCustomerTrafficRepository
            oracle_db = app_container.getInstance('dboracle')
            return AppCustomerTrafficRepository(oracle_db)
        app_container.bind(APP_CUST_REPOSITORY, import_app_cust_repository)

        def import_LoadAppCustomerTraffic(name):
            from src.arbor_os.app_customer_traffic.services.LoadAppCustomerTraffic import LoadAppCustomerTraffic
            dependencies = app_container.getInstancesInArray([APP_CUST_REPOSITORY, 'arbor_api'])
            return LoadAppCustomerTraffic(*dependencies)
        app_container.bind(LOAD_APP_CUST_TRAFFIC, import_LoadAppCustomerTraffic)

        def import_customer_repository(name):
            from src.arbor_os.customer_traffic.repository import CustomerTrafficRepository
            oracle_db = app_container.getInstance('dboracle')
            return CustomerTrafficRepository(oracle_db)
        app_container.bind(CUST_REPOSITORY, import_customer_repository)

        def import_LoadCustomerTraffic(name):
            from src.arbor_os.customer_traffic.services.LoadCustomerTraffic import LoadCustomerTraffic
            dependencies = app_container.getInstancesInArray([CUST_REPOSITORY, 'arbor_api'])
            return LoadCustomerTraffic(*dependencies)
        app_container.bind(LOAD_CUST_TRAFFIC, import_LoadCustomerTraffic)

        def import_AlertRepository(name):
            from src.arbor_os.alerts.repository import AlertRepository
            dependencies = app_container.getInstancesInArray(['dboracle'])
            return AlertRepository(*dependencies)
        app_container.bind(ALERT_REPOSITORY, import_AlertRepository)

        def import_AlertSrcprefixes(name):
            from src.arbor_os.alerts.repository import AlertSrcprefixes
            dependencies = app_container.getInstancesInArray(['dboracle'])
            return AlertSrcprefixes(*dependencies)
        app_container.bind(ALERT_SRCPREFIXES_REPOSITORY, import_AlertSrcprefixes)

        def import_AlertCountryRepository(name):
            from src.arbor_os.alerts.repository import AlertCountryRepository
            dependencies = app_container.getInstancesInArray(['dboracle'])
            return AlertCountryRepository(*dependencies)
        app_container.bind(ALERT_COUNTRY_REPOSITORY, import_AlertCountryRepository)

        def import_AlertPatternRepository(name):
            from src.arbor_os.alerts.repository import AlertPatternRepository
            dependencies = app_container.getInstancesInArray(['dboracle'])
            return AlertPatternRepository(*dependencies)
        app_container.bind(ALERT_PATTERN_REPOSITORY, import_AlertPatternRepository)

        def import_LoadAlerts(name):
            from src.arbor_os.alerts.services.LoadAlerts import LoadAlerts
            dependencies = app_container.getInstancesInArray([
                ALERT_REPOSITORY,
                ALERT_SRCPREFIXES_REPOSITORY,
                ALERT_COUNTRY_REPOSITORY,
                ALERT_PATTERN_REPOSITORY,
                'arbor_api'
            ])
            return LoadAlerts(*dependencies)
        app_container.bind(LOAD_ALERTS, import_LoadAlerts)

        # managed_object
        def import_managed_object_repository(name):
            from src.arbor_os.managed_object.repository import ManagedObjectRepository
            oracle_db = app_container.getInstance('dboracle')
            return ManagedObjectRepository(oracle_db)
        app_container.bind(MANAGED_OBJECT_REPOSITORY, import_managed_object_repository)

        def import_ReloadManagedObject(name):
            from src.arbor_os.managed_object.services.ReloadManagedObject import ReloadManagedObject
            dependencies = app_container.getInstancesInArray([MANAGED_OBJECT_REPOSITORY, 'arbor_api'])
            return ReloadManagedObject(*dependencies)
        app_container.bind(RELOAD_MANAGED_OBJECT, import_ReloadManagedObject)

        # mitigations
        def import_MitigationRepository(name):
            from src.arbor_os.mitigations.repository import MitigationRepository
            dependencies = app_container.getInstancesInArray(['dboracle'])
            return MitigationRepository(*dependencies)
        app_container.bind(MITIGATION_REPOSITORY, import_MitigationRepository)

        def import_LoadMitigations(name):
            from src.arbor_os.mitigations.services.LoadMitigations import LoadMitigations
            dependencies = app_container.getInstancesInArray([MITIGATION_REPOSITORY, 'arbor_api'])
            return LoadMitigations(*dependencies)
        app_container.bind(LOAD_MITIGATIONS, import_LoadMitigations)

        def import_arbor_config_repo(name):
            from src.arbor_os.reports.repository import InMemoryArborConfigRepository
            return InMemoryArborConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(ARBOR_CONFIG_REPO, import_arbor_config_repo)
        
        def import_load_arbor_from_config(name):
            from src.arbor_os.reports.services import LoadArborFromConfig
            deps = app_container.getInstancesInArray(["dboracle", ARBOR_CONFIG_REPO, "arbor_api", "control_carga_repo"])
            return LoadArborFromConfig(*deps)
        app_container.bind(LOAD_ARBOR_FROM_CONFIG, import_load_arbor_from_config)

        def import_event_consumer_from_config(name):
            from src.arbor_os.reports.services import ArborEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(ARBOR_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return ArborEventConsumerFromConfig(queue_service, app_container, notification, repository)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)

        def import_event_producer_from_config(name):
            from src.arbor_os.reports.services import ArborEventProducerFromConfig
            deps = app_container.getInstancesInArray([ARBOR_CONFIG_REPO, "arbor_api", "control_carga_repo", "queue_service"])
            return ArborEventProducerFromConfig(*deps)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)