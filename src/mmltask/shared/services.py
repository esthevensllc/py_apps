MMLTASK_CONFIG_REPO = 'src.mmltask.reports.InMemoryMmltaskConfigRepository'
LOAD_MMLTASK_FROM_CONFIG = 'src.mmltask.reports.MmltaskReportFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.mmltask.reports.MmltaskEventConsumer'
EVENT_PRODUCER_FROM_CONFIG = 'src.mmltask.reports.MmltaskEventProducer'

class MmlTaskAppProvider:
    def __init__(self, app_container):
        def in_memory_ipt_config_repo(name):
            from src.mmltask.reports.repository import InMemoryMmltaskConfigRepository
            return InMemoryMmltaskConfigRepository()
        app_container.bind(MMLTASK_CONFIG_REPO, in_memory_ipt_config_repo)

        def load_ipt_from_config(name):
            from src.mmltask.reports.services import MmltaskReportFromConfig
            dboracle = app_container.getInstance('dboracle')
            repository = app_container.getInstance(MMLTASK_CONFIG_REPO)
            sftp = app_container.getInstance('sftp_service')
            control_repo = app_container.getInstance('control_carga_repo')
            return MmltaskReportFromConfig(dboracle, repository, sftp, control_repo)
        app_container.bind(LOAD_MMLTASK_FROM_CONFIG, load_ipt_from_config)

        def import_event_consumer_from_config(name):
            from src.mmltask.reports.services import MmltaskEventConsumer
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(MMLTASK_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return MmltaskEventConsumer(queue_service, app_container, notification, repository)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)

        def import_event_producer_from_config(name):
            from src.mmltask.reports.services import MmltaskEventProducer
            repository = app_container.getInstance(MMLTASK_CONFIG_REPO)
            sftp = app_container.getInstance('sftp_service')
            control_repo = app_container.getInstance('control_carga_repo')
            queue_service = app_container.getInstance('queue_service')
            return MmltaskEventProducer(repository, sftp, control_repo, queue_service)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)
