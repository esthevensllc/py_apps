IPT_CONFIG_REPO = 'src.ipt.reports.InMemoryIptConfigRepository'
LOAD_IPT_FROM_CONFIG = 'src.ipt.reports.IptReportFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.ipt.reports.IptdbEventConsumer'
EVENT_PRODUCER_FROM_CONFIG = 'src.ipt.reports.IptdbEventProducer'

class IptAppProvider:
    def __init__(self, app_container):
        def in_memory_ipt_config_repo(name):
            from src.ipt.reports.repository import InMemoryIptConfigRepository
            return InMemoryIptConfigRepository()
        app_container.bind(IPT_CONFIG_REPO, in_memory_ipt_config_repo)

        def load_ipt_from_config(name):
            from src.ipt.reports.services import IptReportFromConfig
            dboracle = app_container.getInstance('dboracle')
            repository = app_container.getInstance(IPT_CONFIG_REPO)
            iptDb = app_container.getInstance('dbprovider').getConnection("pg_ipt")
            control_repo = app_container.getInstance('control_carga_repo')
            return IptReportFromConfig(dboracle, repository, iptDb, control_repo)
        app_container.bind(LOAD_IPT_FROM_CONFIG, load_ipt_from_config)

        def import_event_consumer_from_config(name):
            from src.ipt.reports.services import IptEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(IPT_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return IptEventConsumerFromConfig(queue_service, app_container, notification, repository)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)

        def import_event_producer_from_config(name):
            from src.ipt.reports.services import IptEventProducerFromConfig
            repository = app_container.getInstance(IPT_CONFIG_REPO)
            iptDb = app_container.getInstance('dbprovider').getConnection("pg_ipt")
            control_repo = app_container.getInstance('control_carga_repo')
            queue_service = app_container.getInstance('queue_service')
            return IptEventProducerFromConfig(repository, iptDb, control_repo, queue_service)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)
