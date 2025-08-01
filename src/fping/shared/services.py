import os

FPING_IP_FINDER = 'src.fping.maestro.fping_finder'
FPING_IP_FINDER_PRODUCER = 'src.fping.maestro.FpingIpFinderProducer'
FPING_IP_FINDER_PROCESS = 'src.fping.maestro.FpingIpFinderProcess'
MAESTRO_FPING_CGNAT_UPDATER = 'src.fping.maestro.MaestroFpingCgnatUpdater'
SEND_FILE_ACTIVE_IPS = 'src.fping.maestro.SendFileActiveIps'
SEND_FILE_ACTIVE_IPS_CONSUMER = 'src.fping.maestro.SendFileActiveIpsConsumer'
CONFIG_REPO = 'src.fping.maestro.InMemoryFpingConfigRepository'
LOAD_FPING_FROM_CONFIG = 'src.fping.maestro.FpingReportFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.fping.maestro.FpingMaestroEventConsumer'
EVENT_PRODUCER_FROM_CONFIG = 'src.fping.maestro.FpingMaestroEventProducer'

class FpingAppProvider:
    def __init__(self, app_container):
        def fping_ip_finder(name):
            from src.fping.maestro.services import IpInfoFinder
            return IpInfoFinder(os.getenv('PYAPP_IPINFO_BASE_URL'), os.getenv('PYAPP_IPINFO_TOKEN'))
        app_container.bind(FPING_IP_FINDER, fping_ip_finder)
        
        def fping_ip_finder_producer(name):
            from src.fping.maestro.services import FpingIpFinderProducer
            ch = app_container.getInstance('clickhouse')
            ch.useConnection('clickhouse_nce')
            return FpingIpFinderProducer(ch, app_container.getInstance('queue_service'))
        app_container.bind(FPING_IP_FINDER_PRODUCER, fping_ip_finder_producer)

        def fping_ip_finder_process(name):
            from src.fping.maestro.services import FpingIpFinderProcess
            ch = app_container.getInstance('clickhouse')
            ch.useConnection('clickhouse_nce')
            return FpingIpFinderProcess(
                app_container.getInstance('queue_service'),
                app_container.getInstance(FPING_IP_FINDER),
                ch
            )
        app_container.bind(FPING_IP_FINDER_PROCESS, fping_ip_finder_process)

        def maestro_fping_cgnat_updater(name):
            from src.fping.maestro.services import MaestroFpingCgnatUpdater
            ch = app_container.getInstance('clickhouse')
            ch.useConnection('clickhouse_nce')
            return MaestroFpingCgnatUpdater(ch)
        app_container.bind(MAESTRO_FPING_CGNAT_UPDATER, maestro_fping_cgnat_updater)

        def send_file_active_ips(name):
            from src.fping.maestro.services import SendFileActiveIps
            ch = app_container.getInstance('clickhouse')
            ch.useConnection('clickhouse_nce')
            return SendFileActiveIps(ch, app_container.getInstance('sftp_service'))
        app_container.bind(SEND_FILE_ACTIVE_IPS, send_file_active_ips)

        def send_file_active_ips_consumer(name):
            from src.fping.maestro.services import SendFileActiveIpsConsumer
            ch = app_container.getInstance('clickhouse')
            ch.useConnection('clickhouse_nce')
            return SendFileActiveIpsConsumer(app_container.getInstance('queue_service'), ch, app_container.getInstance('sftp_service'))
        app_container.bind(SEND_FILE_ACTIVE_IPS_CONSUMER, send_file_active_ips_consumer)

        # fping cgnat maestro

        def in_memory_fping_maestro_config_repo(name):
            from src.fping.maestro.repository import InMemoryFpingMaestroConfigRepository
            return InMemoryFpingMaestroConfigRepository()
        app_container.bind(CONFIG_REPO, in_memory_fping_maestro_config_repo)

        def load_fping_from_config(name):
            from src.fping.maestro.sftp import FpingReportFromConfig
            db = app_container.getInstance('clickhouse')
            db.useConnection('clickhouse_nce')
            oracle = app_container.getInstance('dboracle')
            repository = app_container.getInstance(CONFIG_REPO)
            control_repo = app_container.getInstance('control_carga_repo')
            sftp_service = app_container.getInstance('sftp_service')
            return FpingReportFromConfig(db, oracle, repository, control_repo, sftp_service)
        app_container.bind(LOAD_FPING_FROM_CONFIG, load_fping_from_config)

        def import_event_consumer_from_config(name):
            from src.fping.maestro.sftp import FpingMaestroEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return FpingMaestroEventConsumerFromConfig(queue_service, app_container, notification, repository)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)

        def import_event_producer_from_config(name):
            from src.fping.maestro.sftp import FpingMaestroEventProducerFromConfig
            repository = app_container.getInstance(CONFIG_REPO)
            control_repo = app_container.getInstance('control_carga_repo')
            queue_service = app_container.getInstance('queue_service')
            sftp_service = app_container.getInstance('sftp_service')
            return FpingMaestroEventProducerFromConfig(sftp_service, repository, control_repo, queue_service)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)
