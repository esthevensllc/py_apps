PRONATEL_CONFIG_REPO = 'src.pronatel.carga.InMemoryPronatelConfigRepository'
LOAD_PRONATEL_FROM_CONFIG = 'src.pronatel.carga.LoadPronatelFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.pronatel.carga.PronatelEventConsumerFromConfig'
EVENT_PRODUCER_FROM_CONFIG = 'src.pronatel.carga.PronatelEventProducerFromConfig'

class PronatelAppProvider:
    def __init__(self, app_container):
        def in_memory_pronatel_config_repo(name):
            from src.pronatel.carga.repository import InMemoryPronatelConfigRepository
            return InMemoryPronatelConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(PRONATEL_CONFIG_REPO, in_memory_pronatel_config_repo)
        
        def load_pronatel_from_config(name):
            from src.pronatel.carga.services import LoadPronatelFromConfig
            deps = app_container.getInstancesInArray(["dboracle", PRONATEL_CONFIG_REPO, "sftp_service", "control_carga_repo"])
            return LoadPronatelFromConfig(*deps)
        app_container.bind(LOAD_PRONATEL_FROM_CONFIG, load_pronatel_from_config)

        def import_event_consumer_from_config(name):
            from src.pronatel.carga.services import PronatelEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(PRONATEL_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return PronatelEventConsumerFromConfig(queue_service, app_container, repository, notification)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)
        
        def import_event_producer_from_config(name):
            from src.pronatel.carga.services import PronatelEventProducerFromConfig
            deps = app_container.getInstancesInArray([PRONATEL_CONFIG_REPO, "sftp_service", "control_carga_repo", "queue_service"])
            return PronatelEventProducerFromConfig(*deps)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)

