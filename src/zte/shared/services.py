ZTE_CONFIG_REPO = 'src.zte.alarms.InMemoryZTEConfigRepository'
LOAD_ZTE_FROM_CONFIG = 'src.zte.alarms.LoadZTEFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.zte.alarms.ZTEEventConsumerFromConfig'
EVENT_PRODUCER_FROM_CONFIG = 'src.zte.alarms.ZTEEventProducerFromConfig'

ZTE_STATS_CONFIG_REPO = 'src.zte.stats.InMemoryZTEConfigRepository'
LOAD_ZTE_STATS_FROM_CONFIG = 'src.zte.stats.LoadZTEStatsFromConfig'
EVENT_STATS_CONSUMER_FROM_CONFIG = 'src.zte.stats.ZTEEventStatsConsumerFromConfig'
EVENT_STATS_PRODUCER_FROM_CONFIG = 'src.zte.stats.ZTEEventStatsProducerFromConfig'

CH_ZTE_STATS_CONFIG_REPO = 'src.zte.ch_stats.InMemoryZTEConfigRepository'
LOAD_CH_ZTE_STATS_FROM_CONFIG = 'src.zte.ch_stats.ChZteStatsFromConfig'
CH_EVENT_STATS_CONSUMER_FROM_CONFIG = 'src.zte.ch_stats.ChZteEventConsumerFromConfig'
CH_EVENT_STATS_PRODUCER_FROM_CONFIG = 'src.zte.ch_stats.ChZteEventProducerFromConfig'

LOAD_ZTE_MAESTRO = 'src.zte.replication.LoadZteMaestroFromOracle'
LOAD_ZTE_EQUIPOS_TX_DESEMP = 'src.zte.replication.LoadZteEquiposTxDesempFromOracle'
ZTE_REPLICATION_EVENT_CONSUMER = 'src.zte.replication.ZteReplicatorEventConsumer'

class ZTEAppProvider:
    def __init__(self, app_container):
        def in_memory_zte_config_repo(name):
            from src.zte.alarms.repository import InMemoryZTEConfigRepository
            return InMemoryZTEConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(ZTE_CONFIG_REPO, in_memory_zte_config_repo)
        
        def load_zte_from_config(name):
            from src.zte.alarms.services import LoadZTEFromConfig
            deps = app_container.getInstancesInArray(["dboracle", ZTE_CONFIG_REPO, "sftp_service", "control_carga_repo"])
            return LoadZTEFromConfig(*deps)
        app_container.bind(LOAD_ZTE_FROM_CONFIG, load_zte_from_config)

        def import_event_consumer_from_config(name):
            from src.zte.alarms.services import ZTEEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(ZTE_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return ZTEEventConsumerFromConfig(queue_service, app_container, repository, notification)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)
        
        def import_event_producer_from_config(name):
            from src.zte.alarms.services import ZTEEventProducerFromConfig
            deps = app_container.getInstancesInArray([ZTE_CONFIG_REPO, "sftp_service", "control_carga_repo", "queue_service"])
            return ZTEEventProducerFromConfig(*deps)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)

        # zte stats

        def in_memory_zte_stats_config_repo(name):
            from src.zte.stats.repository import InMemoryZTEConfigRepository
            return InMemoryZTEConfigRepository()
        app_container.bind(ZTE_STATS_CONFIG_REPO, in_memory_zte_stats_config_repo)

        def load_zte_stats_from_config(name):
            from src.zte.stats.services import ZteStatsFromConfig
            deps = app_container.getInstancesInArray(["dboracle", ZTE_STATS_CONFIG_REPO, "sftp_service", "control_carga_repo"])
            return ZteStatsFromConfig(*deps)
        app_container.bind(LOAD_ZTE_STATS_FROM_CONFIG, load_zte_stats_from_config)

        def import_event_producer_stats_from_config(name):
            from src.zte.stats.services import ZTEEventProducerFromConfig
            deps = app_container.getInstancesInArray([ZTE_STATS_CONFIG_REPO, "sftp_service", "control_carga_repo", "queue_service"])
            return ZTEEventProducerFromConfig(*deps)
        app_container.bind(EVENT_STATS_PRODUCER_FROM_CONFIG, import_event_producer_stats_from_config)

        def import_event_consumer_stats_from_config(name):
            from src.zte.stats.services import ZTEEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(ZTE_STATS_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return ZTEEventConsumerFromConfig(queue_service, app_container, repository, notification)
        app_container.bind(EVENT_STATS_CONSUMER_FROM_CONFIG, import_event_consumer_stats_from_config)

        # clickhouse zte stats

        def in_memory_ch_zte_stats_config_repo(name):
            from src.zte.ch_stats.repository import InMemoryZTEConfigRepository
            return InMemoryZTEConfigRepository()
        app_container.bind(CH_ZTE_STATS_CONFIG_REPO, in_memory_ch_zte_stats_config_repo)

        def load_ch_zte_stats_from_config(name):
            from src.zte.ch_stats.services import ChZteStatsFromConfig
            clickhouse = app_container.getInstance('dbprovider').getConnection('clickhouse_nce')
            deps = [clickhouse]
            deps += app_container.getInstancesInArray([CH_ZTE_STATS_CONFIG_REPO, "sftp_service", "control_carga_repo"])
            return ChZteStatsFromConfig(*deps)
        app_container.bind(LOAD_CH_ZTE_STATS_FROM_CONFIG, load_ch_zte_stats_from_config)

        def import_ch_event_producer_stats_from_config(name):
            from src.zte.ch_stats.services import ChZteEventProducerFromConfig
            deps = app_container.getInstancesInArray([CH_ZTE_STATS_CONFIG_REPO, "sftp_service", "control_carga_repo", "queue_service"])
            return ChZteEventProducerFromConfig(*deps)
        app_container.bind(CH_EVENT_STATS_PRODUCER_FROM_CONFIG, import_ch_event_producer_stats_from_config)

        def import_event_consumer_stats_from_config(name):
            from src.zte.ch_stats.services import ChZteEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(CH_ZTE_STATS_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return ChZteEventConsumerFromConfig(queue_service, app_container, notification, repository)
        app_container.bind(CH_EVENT_STATS_CONSUMER_FROM_CONFIG, import_event_consumer_stats_from_config)

        # replication

        def load_zte_maestro_from_oracle(name):
            from src.zte.replication.services import LoadZteMaestroFromOracle
            clickhouse = app_container.getInstance('dbprovider').getConnection('clickhouse_nce')
            return LoadZteMaestroFromOracle(app_container.getInstance('dboracle'), clickhouse)
        app_container.bind(LOAD_ZTE_MAESTRO, load_zte_maestro_from_oracle)

        def load_zte_maestro_from_oracle(name):
            from src.zte.replication.services import LoadZteEquiposTxDesempFromOracle
            clickhouse = app_container.getInstance('dbprovider').getConnection('clickhouse_nce')
            return LoadZteEquiposTxDesempFromOracle(app_container.getInstance('dboracle'), clickhouse)
        app_container.bind(LOAD_ZTE_EQUIPOS_TX_DESEMP, load_zte_maestro_from_oracle)

        def soportecli_handlers_event_consumer(name):
            from src.zte.replication.services import ZteReplicatorEventConsumer
            queue_service = app_container.getInstance('queue_service')
            notification = app_container.getInstance('notification_service')
            return ZteReplicatorEventConsumer(queue_service, app_container, notification)
        app_container.bind(ZTE_REPLICATION_EVENT_CONSUMER, soportecli_handlers_event_consumer)
