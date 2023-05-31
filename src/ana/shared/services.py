ANA_CONFIG_REPO = 'src.ana.carga.ANAConfigRepository'
LOAD_ANA_DATA_FROM_CONFIG = 'src.ana.carga.LoadANADataFromConfig'
EVENT_PRODUCER_FROM_CONFIG = 'src.ana.carga.ANAEventProducerFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.ana.carga.ANAEventConsumerFromConfig'

class ANAAppProvider:
    def __init__(self, app_container):
        def ana_config_repo(name):
            from src.ana.carga.repository import ANAConfigRepository
            return ANAConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(ANA_CONFIG_REPO, ana_config_repo)
        
        def load_ana_data_from_config(name):
            from src.ana.carga.services import LoadANADataFromConfig
            deps = app_container.getInstancesInArray(["dboracle", ANA_CONFIG_REPO, "sftp_service", "control_carga_repo"])
            return LoadANADataFromConfig(*deps)
        app_container.bind(LOAD_ANA_DATA_FROM_CONFIG, load_ana_data_from_config)
        
        def import_event_consumer_from_config(name):
            from src.ana.carga.services import ANAEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(ANA_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return ANAEventConsumerFromConfig(queue_service, app_container, repository, notification)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)
        
        def import_event_producer_from_config(name):
            from src.ana.carga.services import ANAEventProducerFromConfig
            deps = app_container.getInstancesInArray([ANA_CONFIG_REPO, "sftp_service", "control_carga_repo", "queue_service"])
            return ANAEventProducerFromConfig(*deps)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)