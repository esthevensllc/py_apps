CONFIG_REPO = 'src.cdr.reports.InMemoryWebacsConfigRepository'
LOAD_CDR_FROM_CONFIG = 'src.cdr.reports.CdrReportFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.cdr.reports.CdrEventConsumer'
EVENT_PRODUCER_FROM_CONFIG = 'src.cdr.reports.CdrEventProducer'

class CdrAppProvider:
    def __init__(self, app_container):
        def in_memory_cdr_config_repo(name):
            from src.cdr.reports.repository import InMemoryCdrConfigRepository
            return InMemoryCdrConfigRepository()
        app_container.bind(CONFIG_REPO, in_memory_cdr_config_repo)

        def load_cdr_from_config(name):
            from src.cdr.reports.services import CdrReportFromConfig
            dboracle = app_container.getInstance('dboracle')
            repository = app_container.getInstance(CONFIG_REPO)
            control_repo = app_container.getInstance('control_carga_repo')
            sftp_service = app_container.getInstance('sftp_service')
            return CdrReportFromConfig(dboracle, repository, control_repo, sftp_service)
        app_container.bind(LOAD_CDR_FROM_CONFIG, load_cdr_from_config)

        def import_event_consumer_from_config(name):
            from src.cdr.reports.services import CdrEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return CdrEventConsumerFromConfig(queue_service, app_container, notification, repository)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)

        def import_event_producer_from_config(name):
            from src.cdr.reports.services import CdrEventProducerFromConfig
            repository = app_container.getInstance(CONFIG_REPO)
            control_repo = app_container.getInstance('control_carga_repo')
            queue_service = app_container.getInstance('queue_service')
            sftp_service = app_container.getInstance('sftp_service')
            return CdrEventProducerFromConfig(sftp_service, repository, control_repo, queue_service)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)
