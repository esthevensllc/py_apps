U2000_CONFIG_REPO = 'src.U2000.reports.InMemoryU2000ConfigRepository'
LOAD_U2000_FROM_CONFIG = 'src.U2000.reports.LoadU2000FromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.U2000.reports.U2000EventConsumerFromConfig'
EVENT_PRODUCER_FROM_CONFIG = 'src.U2000.reports.U2000EventProducerFromConfig'

class U2000AppProvider:
    def __init__(self, app_container):
        def in_memory_U2000_config_repo(name):
            from src.U2000.reports.repository import InMemoryU2000ConfigRepository
            return InMemoryU2000ConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(U2000_CONFIG_REPO, in_memory_U2000_config_repo)
        
        def load_U2000_from_config(name):
            from src.U2000.reports.services import LoadU2000FromConfig
            deps = app_container.getInstancesInArray(["dboracle", U2000_CONFIG_REPO, "sftp_service", "control_carga_repo"])
            return LoadU2000FromConfig(*deps)
        app_container.bind(LOAD_U2000_FROM_CONFIG, load_U2000_from_config)

        def import_event_consumer_from_config(name):
            from src.U2000.reports.services import U2000EventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(U2000_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return U2000EventConsumerFromConfig(queue_service, app_container, repository, notification)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)
        
        def import_event_producer_from_config(name):
            from src.U2000.reports.services import U2000EventProducerFromConfig
            deps = app_container.getInstancesInArray([U2000_CONFIG_REPO, "sftp_service", "control_carga_repo", "queue_service"])
            return U2000EventProducerFromConfig(*deps)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)

