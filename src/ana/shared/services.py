ANA_CONFIG_REPO = 'src.ana.carga.ANAConfigRepository'
LOAD_ANA_DATA_FROM_CONFIG = 'src.ana.carga.LoadANADataFromConfig'
EVENT_PRODUCER_FROM_CONFIG = 'src.ana.carga.ANAEventProducerFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.ana.carga.ANAEventConsumerFromConfig'

REPORTE_EVOLUCION_GENERATOR = 'src.ana.handlers.ReporteEvolucionGenerator'
TRAFICO_3G_2G_GENERATOR = 'src.ana.handlers.Trafico3g2gGenerator'
REP_MAGGIE_GENERATOR = 'src.ana.handlers.RepMaggieGenerator'
REP_BANDAS_GENERATOR = 'src.ana.handlers.RepBandasGenerator'
ANA_HANDLERS_EVENT_CONSUMER = 'src.ana.handlers.AnaHandlerEventConsumer'

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
        
        def import_reporte_evolucion_generator(name):
            from src.ana.handlers.services import ReporteEvolucionGenerator
            oracle = app_container.getInstance("dboracle")
            return ReporteEvolucionGenerator(oracle)
        app_container.bind(REPORTE_EVOLUCION_GENERATOR, import_reporte_evolucion_generator)
        
        def import_trafico_2g_vs_3g_generator(name):
            from src.ana.handlers.services import Trafico3g2gGenerator
            oracle = app_container.getInstance("dboracle")
            return Trafico3g2gGenerator(oracle)
        app_container.bind(TRAFICO_3G_2G_GENERATOR, import_trafico_2g_vs_3g_generator)
        
        def import_rep_maggie_generator(name):
            from src.ana.handlers.services import RepMaggieGenerator
            oracle = app_container.getInstance("dboracle")
            return RepMaggieGenerator(oracle)
        app_container.bind(REP_MAGGIE_GENERATOR, import_rep_maggie_generator)
        
        def import_rep_bandas_generator(name):
            from src.ana.handlers.services import RepBandasGenerator
            oracle = app_container.getInstance("dboracle")
            return RepBandasGenerator(oracle)
        app_container.bind(REP_BANDAS_GENERATOR, import_rep_bandas_generator)

        def ana_handlers_event_consumer(name):
            from src.ana.handlers.services import AnaHandlerEventConsumer
            queue_service = app_container.getInstance('queue_service')
            notification = app_container.getInstance('notification_service')
            return AnaHandlerEventConsumer(queue_service, app_container, notification)
        app_container.bind(ANA_HANDLERS_EVENT_CONSUMER, ana_handlers_event_consumer)