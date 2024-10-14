ZTE_CONFIG_REPO = 'src.zte.alarms.InMemoryZTEConfigRepository'
LOAD_ZTE_FROM_CONFIG = 'src.zte.alarms.LoadZTEFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.zte.alarms.ZTEEventConsumerFromConfig'
EVENT_PRODUCER_FROM_CONFIG = 'src.zte.alarms.ZTEEventProducerFromConfig'

ZTE_STATS_CONFIG_REPO = 'src.zte.stats.InMemoryZTEConfigRepository'
LOAD_ZTE_STATS_FROM_CONFIG = 'src.zte.stats.LoadZTEStatsFromConfig'
EVENT_STATS_CONSUMER_FROM_CONFIG = 'src.zte.stats.ZTEEventStatsConsumerFromConfig'
EVENT_STATS_PRODUCER_FROM_CONFIG = 'src.zte.stats.ZTEEventStatsProducerFromConfig'

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

