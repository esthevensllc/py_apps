CONFIG_REPO = 'src.webacs.api.InMemoryWebacsConfigRepository'
LOAD_WEBACS_FROM_CONFIG = 'src.webacs.api.WebacsReportFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.webacs.api.WebacsEventConsumer'
EVENT_PRODUCER_FROM_CONFIG = 'src.webacs.api.WebacsEventProducer'

class WebacsAppProvider:
    def __init__(self, app_container):
        def in_memory_webacs_config_repo(name):
            from src.webacs.api.repository import InMemoryWebacsConfigRepository
            return InMemoryWebacsConfigRepository()
        app_container.bind(CONFIG_REPO, in_memory_webacs_config_repo)

        def load_webacs_from_config(name):
            from src.webacs.api.services import WebacsReportFromConfig
            dboracle = app_container.getInstance('dboracle')
            repository = app_container.getInstance(CONFIG_REPO)
            control_repo = app_container.getInstance('control_carga_repo')
            return WebacsReportFromConfig(dboracle, repository, control_repo)
        app_container.bind(LOAD_WEBACS_FROM_CONFIG, load_webacs_from_config)

        def import_event_consumer_from_config(name):
            from src.webacs.api.services import WebacsEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return WebacsEventConsumerFromConfig(queue_service, app_container, notification, repository)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)

        def import_event_producer_from_config(name):
            from src.webacs.api.services import WebacsEventProducerFromConfig
            repository = app_container.getInstance(CONFIG_REPO)
            control_repo = app_container.getInstance('control_carga_repo')
            queue_service = app_container.getInstance('queue_service')
            return WebacsEventProducerFromConfig(repository, control_repo, queue_service)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)
