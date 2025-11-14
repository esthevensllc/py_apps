DIG_CGNAT_CONFIG_REPO = 'src.dig.carga.InMemoryDigCgnatConfigRepository'
LOAD_DIG_CGNAT_FROM_CONFIG = 'src.dig.carga.DigCgnatReportFromConfig'
EVENT_CONSUMER_CGNAT_FROM_CONFIG = 'src.dig.carga.DigCgnatEventConsumer'
EVENT_PRODUCER_CGNAT_FROM_CONFIG = 'src.dig.carga.DigCgnatEventProducer'

class DigAppProvider:
    def __init__(self, app_container):
        def in_memory_dig_cgnat_config_repo(name):
            from src.dig.carga.repository import InMemoryDigCgnatConfigRepository
            return InMemoryDigCgnatConfigRepository()
        app_container.bind(DIG_CGNAT_CONFIG_REPO, in_memory_dig_cgnat_config_repo)

        def load_dig_cgnat_from_config(name):
            from src.dig.carga.services import DigCgnatReportFromConfig
            db_provider = app_container.getInstance("dbprovider")
            ch = db_provider.getConnection("clickhouse_secondary")
            oracle_db = db_provider.getConnection("default")
            repository = app_container.getInstance(DIG_CGNAT_CONFIG_REPO)
            control_repo = app_container.getInstance('control_carga_repo')
            sftp_service = app_container.getInstance('sftp_service')
            return DigCgnatReportFromConfig(ch, oracle_db, repository, control_repo, sftp_service)
        app_container.bind(LOAD_DIG_CGNAT_FROM_CONFIG, load_dig_cgnat_from_config)

        def import_event_consumer_cgnat_from_config(name):
            from src.dig.carga.services import DigCgnatEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(DIG_CGNAT_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return DigCgnatEventConsumerFromConfig(queue_service, app_container, notification, repository)
        app_container.bind(EVENT_CONSUMER_CGNAT_FROM_CONFIG, import_event_consumer_cgnat_from_config)

        def import_event_producer_cgnat_from_config(name):
            from src.dig.carga.services import DigCgnatEventProducerFromConfig
            repository = app_container.getInstance(DIG_CGNAT_CONFIG_REPO)
            control_repo = app_container.getInstance('control_carga_repo')
            queue_service = app_container.getInstance('queue_service')
            sftp_service = app_container.getInstance('sftp_service')
            return DigCgnatEventProducerFromConfig(sftp_service, repository, control_repo, queue_service)
        app_container.bind(EVENT_PRODUCER_CGNAT_FROM_CONFIG, import_event_producer_cgnat_from_config)
