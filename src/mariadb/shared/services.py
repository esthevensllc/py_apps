MARIADB_CONFIG_REPO = 'src.mariadb.reports.InMemoryMariadbConfigRepository'
LOAD_MARIADB_FROM_CONFIG = 'src.mariadb.reports.LoadMariadbFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.mariadb.reports.MariadbEventConsumer'
EVENT_PRODUCER_FROM_CONFIG = 'src.mariadb.reports.MariadbEventProducer'

class MariadbAppProvider:
    def __init__(self, app_container):
        def in_memory_mariadb_config_repo(name):
            from src.mariadb.reports.repository import InMemoryMariadbConfigRepository
            return InMemoryMariadbConfigRepository(app_container.getInstance('dbprovider').getConnection("mariadb_alarmas"))
        app_container.bind(MARIADB_CONFIG_REPO, in_memory_mariadb_config_repo)

        def load_mariadb_from_config(name):
            from src.mariadb.reports.services import LoadMariadbFromConfig
            dboracle = app_container.getInstance('dboracle')
            repository = app_container.getInstance(MARIADB_CONFIG_REPO)
            mariadb = app_container.getInstance('dbprovider').getConnection("mariadb_alarmas")
            control_repo = app_container.getInstance('control_carga_repo')
            return LoadMariadbFromConfig(dboracle, repository, mariadb, control_repo)
        app_container.bind(LOAD_MARIADB_FROM_CONFIG, load_mariadb_from_config)

        def import_event_consumer_from_config(name):
            from src.mariadb.reports.services import MariadbEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(MARIADB_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return MariadbEventConsumerFromConfig(queue_service, app_container, notification, repository)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)

        def import_event_producer_from_config(name):
            from src.mariadb.reports.services import MariadbEventProducerFromConfig
            repository = app_container.getInstance(MARIADB_CONFIG_REPO)
            mariadb = app_container.getInstance('dbprovider').getConnection("mariadb_alarmas")
            control_repo = app_container.getInstance('control_carga_repo')
            queue_service = app_container.getInstance('queue_service')
            return MariadbEventProducerFromConfig(repository, mariadb, control_repo, queue_service)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)