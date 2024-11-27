CH_CONFIG_REPO = 'src.clickhouse.replication.InMemoryChReplicationConfigRepository'
LOAD_CH_FROM_CONFIG = 'src.clickhouse.replication.ChReplicationFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.clickhouse.replication.ChReplicationEventConsumer'
EVENT_PRODUCER_FROM_CONFIG = 'src.clickhouse.replication.ChReplicationEventProducer'

class ChReplicationAppProvider:
    def __init__(self, app_container):
        def in_memory_ch_config_repo(name):
            from src.clickhouse.replication.repository import InMemoryClickhouseConfigRepository
            return InMemoryClickhouseConfigRepository()
        app_container.bind(CH_CONFIG_REPO, in_memory_ch_config_repo)

        def load_ch_from_config(name):
            from src.clickhouse.replication.services import ChReplicationFromConfig
            dboracle = app_container.getInstance('dboracle')
            repository = app_container.getInstance(CH_CONFIG_REPO)
            ch_db = app_container.getInstance('dbprovider').getConnection("clickhouse_dn06").getReference()
            control_repo = app_container.getInstance('control_carga_repo')
            return ChReplicationFromConfig(dboracle, repository, ch_db, control_repo)
        app_container.bind(LOAD_CH_FROM_CONFIG, load_ch_from_config)

        def import_event_consumer_from_config(name):
            from src.clickhouse.replication.services import ChReplicationEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(CH_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return ChReplicationEventConsumerFromConfig(queue_service, app_container, notification, repository)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)

        def import_event_producer_from_config(name):
            from src.clickhouse.replication.services import ChReplicationEventProducerFromConfig
            repository = app_container.getInstance(CH_CONFIG_REPO)
            ch_db = app_container.getInstance('dbprovider').getConnection("clickhouse_dn06")
            control_repo = app_container.getInstance('control_carga_repo')
            queue_service = app_container.getInstance('queue_service')
            return ChReplicationEventProducerFromConfig(repository, ch_db, control_repo, queue_service)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)
