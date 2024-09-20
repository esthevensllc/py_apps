WEPLANCLOUD_CONFIG_REPO = 'src.weplan_analytics.s3.InMemoryWeplanCloudConfigRepository'
LOAD_WEPLANCLOUD_FROM_CONFIG = 'src.weplan_analytics.s3.LoadWeplanCloudFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.weplan_analytics.s3.WeplanCloudEventConsumer'
EVENT_PRODUCER_FROM_CONFIG = 'src.weplan_analytics.s3.WeplanCloudEventProducer'

class WeplanCloudAppProvider:
    def __init__(self, app_container):
        def in_memory_mariadb_config_repo(name):
            from src.weplan_analytics.s3.repository import InMemoryWeplanCloudConfigRepository
            return InMemoryWeplanCloudConfigRepository()
        app_container.bind(WEPLANCLOUD_CONFIG_REPO, in_memory_mariadb_config_repo)

        def load_weplancloud_from_config(name):
            from src.weplan_analytics.s3.services import LoadWeplanCloudFromConfig
            dbclickhouse = app_container.getInstance('dbprovider').getConnection("clickhouse_nce")
            repository = app_container.getInstance(WEPLANCLOUD_CONFIG_REPO)
            s3_client = app_container.getInstance('aws_s3')
            control_repo = app_container.getInstance('control_carga_repo')
            cache = app_container.getInstance('cache')
            return LoadWeplanCloudFromConfig(dbclickhouse, repository, s3_client, control_repo, cache)
        app_container.bind(LOAD_WEPLANCLOUD_FROM_CONFIG, load_weplancloud_from_config)

        def import_event_consumer_from_config(name):
            from src.weplan_analytics.s3.services import WeplanCloudEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(WEPLANCLOUD_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return WeplanCloudEventConsumerFromConfig(queue_service, app_container, notification, repository)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)

        def import_event_producer_from_config(name):
            from src.weplan_analytics.s3.services import WeplanCloudEventProducerFromConfig
            repository = app_container.getInstance(WEPLANCLOUD_CONFIG_REPO)
            s3_client = app_container.getInstance('aws_s3')
            control_repo = app_container.getInstance('control_carga_repo')
            queue_service = app_container.getInstance('queue_service')
            cache = app_container.getInstance('cache')
            return WeplanCloudEventProducerFromConfig(repository, s3_client, control_repo, queue_service, cache)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)