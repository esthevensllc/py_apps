CONFIG_REPO = 'src.control_carga.ora_handlers.OracleHandlersRepository'
LOAD_HANDLERS = 'src.control_carga.ora_handlers.LoadOracleHandlers'
#LOAD_MITIGATIONS = 'med_huawei2.mitigations.LoadMitigations'

class ControlCargaAppProvider:
    def __init__(self, app_container):
        def import_config_repo(name):
            from src.control_carga.ora_handlers.repository import OracleHandlersRepository
            oracle_db = app_container.getInstance('dboracle')
            return OracleHandlersRepository(oracle_db)
        app_container.bind(CONFIG_REPO, import_config_repo)

        def import_load_handlers(name):
            from src.control_carga.ora_handlers.services import LoadOracleHandlers
            config_repo = app_container.getInstance(CONFIG_REPO)
            return LoadOracleHandlers(config_repo)
        app_container.bind(LOAD_HANDLERS, import_load_handlers)
