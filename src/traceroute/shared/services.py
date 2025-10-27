SPEEDTEST_API = 'src.traceroute.anomalias.SendTracerouteFileActiveIps'
CONFIG_REPO = 'src.traceroute.carga.InMemoryTracerouteConfigRepository'
LOAD_TRACEROUTE_FROM_CONFIG = 'src.traceroute.carga.TracerouteReportFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.traceroute.carga.TracerouteEventConsumer'
EVENT_PRODUCER_FROM_CONFIG = 'src.traceroute.carga.TracerouteEventProducer'
TRACEROUTE_RESUMEN = 'src.traceroute.anomalias.TracerouteResumen'
TRACEROUTE_RESUMEN_CONSUMER = 'src.traceroute.anomalias.TracerouteResumenConsumer'
SEND_TRACEROUTE_ALL_DOMAINS = 'src.traceroute.anomalias.SendTracerouteAllDomains'

class TracerouteAppProvider:
    def __init__(self, app_container):
        def send_traceroute_file_active_ips(name):
            from src.traceroute.anomalias.services import SendTracerouteFileActiveIps
            deps = app_container.getInstancesInArray(["dbprovider", "sftp_service"])
            deps[0] = deps[0].getConnection("clickhouse_nce")
            return SendTracerouteFileActiveIps(*deps)
        app_container.bind(SPEEDTEST_API, send_traceroute_file_active_ips)

        def in_memory_traceroute_config_repo(name):
            from src.traceroute.carga.repository import InMemoryTracerouteConfigRepository
            return InMemoryTracerouteConfigRepository()
        app_container.bind(CONFIG_REPO, in_memory_traceroute_config_repo)

        def load_traceroute_from_config(name):
            from src.traceroute.carga.services import TracerouteReportFromConfig
            db_provider = app_container.getInstance("dbprovider")
            ch = db_provider.getConnection("clickhouse_nce")
            oracle_db = db_provider.getConnection("default")
            repository = app_container.getInstance(CONFIG_REPO)
            control_repo = app_container.getInstance('control_carga_repo')
            sftp_service = app_container.getInstance('sftp_service')
            return TracerouteReportFromConfig(ch, oracle_db, repository, control_repo, sftp_service)
        app_container.bind(LOAD_TRACEROUTE_FROM_CONFIG, load_traceroute_from_config)

        def import_event_consumer_from_config(name):
            from src.traceroute.carga.services import TracerouteEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return TracerouteEventConsumerFromConfig(queue_service, app_container, notification, repository)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)

        def import_event_producer_from_config(name):
            from src.traceroute.carga.services import TracerouteEventProducerFromConfig
            repository = app_container.getInstance(CONFIG_REPO)
            control_repo = app_container.getInstance('control_carga_repo')
            queue_service = app_container.getInstance('queue_service')
            sftp_service = app_container.getInstance('sftp_service')
            return TracerouteEventProducerFromConfig(sftp_service, repository, control_repo, queue_service)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)

        def import_traceroute_resumen(name):
            from src.traceroute.anomalias.services import TracerouteResumen
            ch = app_container.getInstance("dbprovider")
            ch = ch.getConnection("clickhouse_nce")
            return TracerouteResumen(ch)
        app_container.bind(TRACEROUTE_RESUMEN, import_traceroute_resumen)

        def import_traceroute_resumen_consumer(name):
            from src.traceroute.anomalias.services import TracerouteResumenConsumer
            queue_service = app_container.getInstance('queue_service')
            notification = app_container.getInstance('notification_service')
            return TracerouteResumenConsumer(queue_service, app_container, notification)
        app_container.bind(TRACEROUTE_RESUMEN_CONSUMER, import_traceroute_resumen_consumer)

        def import_send_traceroute_all_domains(name):
            from src.traceroute.anomalias.services import SendTracerouteAllDomains
            ch = app_container.getInstance("dbprovider")
            ch = ch.getConnection("clickhouse_nce")
            sftp_service = app_container.getInstance('sftp_service')
            return SendTracerouteAllDomains(ch, sftp_service)
        app_container.bind(SEND_TRACEROUTE_ALL_DOMAINS, import_send_traceroute_all_domains)
