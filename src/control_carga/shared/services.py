CONFIG_REPO = 'src.control_carga.ora_handlers.OracleHandlersRepository'
LOAD_HANDLERS = 'src.control_carga.ora_handlers.LoadOracleHandlers'
RESUMEN_EVENT_CONSUMER = 'src.control_carga.ora_handlers.ResumenEventConsumer'
#LOAD_MITIGATIONS = 'med_huawei2.mitigations.LoadMitigations'

class ControlCargaAppProvider:
    def __init__(self, app_container):
        def import_config_repo(name):
            from src.control_carga.ora_handlers.repository import OracleHandlersRepository
            oracle_db = app_container.getInstance('dboracle')
            clickhouse = app_container.getInstance('clickhouse')
            return OracleHandlersRepository(oracle_db, clickhouse)
        app_container.bind(CONFIG_REPO, import_config_repo)

        def import_load_handlers(name):
            from src.control_carga.ora_handlers.services import LoadOracleHandlers
            config_repo = app_container.getInstance(CONFIG_REPO)
            control_repo = app_container.getInstance("control_carga_repo")
            return LoadOracleHandlers(config_repo, control_repo)
        app_container.bind(LOAD_HANDLERS, import_load_handlers)

        def import_resumen_event_consumer(name):
            from src.control_carga.ora_handlers.services import ResumenEventConsumer
            queue_service = app_container.getInstance('queue_service')
            # repository = app_container.getInstance(NCE_CONFIG_REPO)
            notification_service = app_container.getInstance('notification_service')
            return ResumenEventConsumer(queue_service, app_container, notification_service)
        app_container.bind(RESUMEN_EVENT_CONSUMER, import_resumen_event_consumer)
