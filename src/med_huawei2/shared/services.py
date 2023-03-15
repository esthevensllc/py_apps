CONFIG_REPO = 'src.med_huawei2.mediciones.MedHuawei2ConfigRepository'
SHARED_REPO = 'src.med_huawei2.mediciones.SharedRepo'
LOAD_MEDICIONES = 'src.med_huawei2.mediciones.CargaMediciones'
EVENT_CONSUMER = 'src.med_huawei2.mediciones.MedHuawei2EventConsumer'
#LOAD_MITIGATIONS = 'med_huawei2.mitigations.LoadMitigations'

class MedHuawei2AppProvider:
    def __init__(self, app_container):
        def import_config_repo(name):
            from src.med_huawei2.mediciones.repository import MedHuawei2ConfigRepository
            oracle_db = app_container.getInstance('dboracle')
            return MedHuawei2ConfigRepository(oracle_db)
        app_container.bind(CONFIG_REPO, import_config_repo)

        def import_shared_repo(name):
            from src.med_huawei2.mediciones.repository import SharedRepository
            oracle_db = app_container.getInstance('dboracle')
            return SharedRepository(oracle_db)
        app_container.bind(SHARED_REPO, import_shared_repo)

        def import_load_mediciones(name):
            from src.med_huawei2.mediciones.services import CargaMediciones
            shared_repo = app_container.getInstance(SHARED_REPO)
            config_repo = app_container.getInstance(CONFIG_REPO)
            control_carga_repo = app_container.getInstance('control_carga_repo')
            return CargaMediciones(shared_repo, config_repo, control_carga_repo, app_container)
        app_container.bind(LOAD_MEDICIONES, import_load_mediciones)

        def import_event_consumer(name):
            from src.med_huawei2.mediciones.services import MedHuawei2EventConsumer
            queue_service = app_container.getInstance('queue_service')
            notification_service = app_container.getInstance('notification_service')
            return MedHuawei2EventConsumer(queue_service, app_container, notification_service)
        app_container.bind(EVENT_CONSUMER, import_event_consumer)
