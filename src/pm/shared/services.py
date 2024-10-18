INTERFACE_TRAFFIC_REPO = 'pm.interface_traffic.InterfacesTrafficRepository'
LOAD_INTERFACE_TRAFFIC = 'pm.interface_traffic.LoadInterfaceTraffic'

PM_CONFIG_REPO = 'src.pm.carga.InMemoryPMConfigRepository'
LOAD_PM_FROM_CONFIG = 'src.pm.carga.LoadPMFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.pm.carga.PMEventConsumerFromConfig'
EVENT_PRODUCER_FROM_CONFIG = 'src.pm.carga.PMEventProducerFromConfig'

PM_BATCH_CONFIG_REPO = 'src.pm.carga.InMemoryPMBatchConfigRepository'
LOAD_PM_BATCH_FROM_CONFIG = 'src.pm.carga.PmBatchFromConfig'
EVENT_BATCH_CONSUMER = 'src.pm.carga.PMEventBatchConsumer'
EVENT_BATCH_PRODUCER = 'src.pm.carga.PMEventBatchProducer'

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

        def in_memory_pm_config_repo(name):
            from src.pm.stats.repository import InMemoryPMConfigRepository
            return InMemoryPMConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(PM_CONFIG_REPO, in_memory_pm_config_repo)

        def load_pm_from_config(name):
            from src.pm.stats.services import LoadPMFromConfig
            deps = app_container.getInstancesInArray(["dboracle", PM_CONFIG_REPO, "pm_api", "control_carga_repo"])
            return LoadPMFromConfig(*deps)
        app_container.bind(LOAD_PM_FROM_CONFIG, load_pm_from_config)

        def import_event_consumer_from_config(name):
            from src.pm.stats.services import PMEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(PM_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return PMEventConsumerFromConfig(queue_service, app_container, notification, repository)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)

        def import_event_producer_from_config(name):
            from src.pm.stats.services import PMEventProducerFromConfig
            deps = app_container.getInstancesInArray([PM_CONFIG_REPO, "pm_api", "control_carga_repo", "queue_service"])
            return PMEventProducerFromConfig(*deps)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)

        # Batch
        def in_memory_pm_batch_config_repo(name):
            from src.pm.stats.repository import InMemoryPmBatchConfigRepository
            return InMemoryPmBatchConfigRepository()
        app_container.bind(PM_BATCH_CONFIG_REPO, in_memory_pm_batch_config_repo)

        def load_pm_batch_from_config(name):
            from src.pm.stats.services import PmBatchFromConfig
            deps = app_container.getInstancesInArray(["dboracle", PM_BATCH_CONFIG_REPO, "control_carga_repo"])
            return PmBatchFromConfig(*deps)
        app_container.bind(LOAD_PM_BATCH_FROM_CONFIG, load_pm_batch_from_config)

        def import_event_batch_consumer_from_config(name):
            from src.pm.stats.services import PmEventBatchConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(PM_BATCH_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return PmEventBatchConsumerFromConfig(queue_service, app_container, notification, repository)
        app_container.bind(EVENT_BATCH_CONSUMER, import_event_batch_consumer_from_config)

        def import_event_batch_producer_from_config(name):
            from src.pm.stats.services import PmEventBatchProducerFromConfig
            deps = app_container.getInstancesInArray([PM_BATCH_CONFIG_REPO, "pm_api", "control_carga_repo", "queue_service"])
            return PmEventBatchProducerFromConfig(*deps)
        app_container.bind(EVENT_BATCH_PRODUCER, import_event_batch_producer_from_config)

