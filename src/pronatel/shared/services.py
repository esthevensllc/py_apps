PRONATEL_CONFIG_REPO = 'src.pronatel.carga.InMemoryPronatelConfigRepository'
LOAD_PRONATEL_FROM_CONFIG = 'src.pronatel.carga.LoadPronatelFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.pronatel.carga.PronatelEventConsumerFromConfig'
EVENT_PRODUCER_FROM_CONFIG = 'src.pronatel.carga.PronatelEventProducerFromConfig'

SEND_FLAG_HFC = 'src.soporteclientes.handlers.SendFlagHfc'
SEND_FLAG_FTTH = 'src.soporteclientes.handlers.SendFlagFtth'
SEND_SCORE_HFC = 'src.soporteclientes.handlers.SendScoreHfc'
SEND_SCORE_FTTH = 'src.soporteclientes.handlers.SendScoreFtth'
SEND_OCURRENCIAS_FIJA = 'src.soporteclientes.handlers.SendOcurrenciasFija'
SEND_VMAX = 'src.soporteclientes.handlers.SendVmax'
SEND_WIFI_HFC = 'src.soporteclientes.handlers.SendWifiHfc'
SEND_REINICIOS_FTTH_HFC_DET = 'src.soporteclientes.handlers.SendReiniciosFtthHfcDet'
SEND_EQUIPO_NO_RECOMENDADO_HFC_DET = 'src.soporteclientes.handlers.SendEquipoNoRecomendadoHfcDet'
LOAD_RECLAMOS_PLANNING = 'src.soporteclientes.handlers.LoadAnaReclamosFromSoporteClientes'
SEND_RECLAMOS_MOVILES_CELDAS_AT = 'src.soporteclientes.handlers.SendReclamosMovilesCeldasAt'
SOPORTECLI_HANDLERS_EVENT_CONSUMER = 'src.soporteclientes.handlers.SoporteClientesHandlerEventConsumer'
DEPURAR_LOGS_PRONATEL = 'src.soporteclientes.logs.DepurarLogsPronatel'

class PronatelAppProvider:
    def __init__(self, app_container):
        def in_memory_pronatel_config_repo(name):
            from src.pronatel.carga.repository import InMemoryPronatelConfigRepository
            return InMemoryPronatelConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(PRONATEL_CONFIG_REPO, in_memory_pronatel_config_repo)
        
        def load_pronatel_from_config(name):
            from src.pronatel.carga.services import LoadPronatelFromConfig
            deps = app_container.getInstancesInArray(["dboracle", PRONATEL_CONFIG_REPO, "sftp_service", "control_carga_repo"])
            return LoadPronatelFromConfig(*deps)
        app_container.bind(LOAD_PRONATEL_FROM_CONFIG, load_pronatel_from_config)

        def import_event_consumer_from_config(name):
            from src.pronatel.carga.services import PronatelEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(PRONATEL_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return PronatelEventConsumerFromConfig(queue_service, app_container, repository, notification)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)
        
        def import_event_producer_from_config(name):
            from src.pronatel.carga.services import PronatelEventProducerFromConfig
            deps = app_container.getInstancesInArray([PRONATEL_CONFIG_REPO, "sftp_service", "control_carga_repo", "queue_service"])
            return PronatelEventProducerFromConfig(*deps)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)

        def send_flag_hfc_handler(name):
            from src.pronatel.handlers.services import SendFlagHfc
            return SendFlagHfc(app_container.getInstance('dboracle'), app_container.getInstance('sftp_service'))
        app_container.bind(SEND_FLAG_HFC, send_flag_hfc_handler)
        def send_flag_ftth_handler(name):
            from src.pronatel.handlers.services import SendFlagFtth
            return SendFlagFtth(app_container.getInstance('dboracle'), app_container.getInstance('sftp_service'))
        app_container.bind(SEND_FLAG_FTTH, send_flag_ftth_handler)
        def send_score_hfc_handler(name):
            from src.pronatel.handlers.services import SendScoreHfc
            return SendScoreHfc(app_container.getInstance('dboracle'), app_container.getInstance('sftp_service'))
        app_container.bind(SEND_SCORE_HFC, send_score_hfc_handler)
        def send_score_ftth_handler(name):
            from src.pronatel.handlers.services import SendScoreFtth
            return SendScoreFtth(app_container.getInstance('dboracle'), app_container.getInstance('sftp_service'))
        app_container.bind(SEND_SCORE_FTTH, send_score_ftth_handler)
        def send_ocurrencias_fija_handler(name):
            from src.pronatel.handlers.services import SendOcurrenciasFija
            return SendOcurrenciasFija(app_container.getInstance('dboracle'), app_container.getInstance('sftp_service'))
        app_container.bind(SEND_OCURRENCIAS_FIJA, send_ocurrencias_fija_handler)
        def send_vmax_handler(name):
            from src.pronatel.handlers.services import SendVmax
            return SendVmax(app_container.getInstance('dboracle'), app_container.getInstance('sftp_service'))
        app_container.bind(SEND_VMAX, send_vmax_handler)
        def send_wifi_hfc_handler(name):
            from src.pronatel.handlers.services import SendWifiHfc
            return SendWifiHfc(app_container.getInstance('dboracle'), app_container.getInstance('sftp_service'))
        app_container.bind(SEND_WIFI_HFC, send_wifi_hfc_handler)
        def send_reinicios_ftth_hfc_det_handler(name):
            from src.pronatel.handlers.services import SendReiniciosFtthHfcDet
            return SendReiniciosFtthHfcDet(app_container.getInstance('dboracle'), app_container.getInstance('sftp_service'))
        app_container.bind(SEND_REINICIOS_FTTH_HFC_DET, send_reinicios_ftth_hfc_det_handler)
        def send_equipo_no_recomendado_hfc_det_handler(name):
            from src.pronatel.handlers.services import SendEquipoNoRecomendadoHfcDet
            return SendEquipoNoRecomendadoHfcDet(app_container.getInstance('dboracle'), app_container.getInstance('sftp_service'))
        app_container.bind(SEND_EQUIPO_NO_RECOMENDADO_HFC_DET, send_equipo_no_recomendado_hfc_det_handler)
        def load_reclamos_planning_handler(name):
            from src.pronatel.handlers.services import LoadAnaReclamosFromSoporteClientes
            return LoadAnaReclamosFromSoporteClientes(app_container.getInstance('dboracle'), app_container.getInstance('dbprovider').getConnection('clickhouse_nce'))
        app_container.bind(LOAD_RECLAMOS_PLANNING, load_reclamos_planning_handler)
        def send_reclamos_moviles_celdas_at(name):
            from src.pronatel.handlers.services import SendReclamosMovilesCeldasAt
            return SendReclamosMovilesCeldasAt(app_container.getInstance('dboracle'), app_container.getInstance('sftp_service'))
        app_container.bind(SEND_RECLAMOS_MOVILES_CELDAS_AT, send_reclamos_moviles_celdas_at)

        def soportecli_handlers_event_consumer(name):
            from src.pronatel.handlers.services import SoporteClientesHandlerEventConsumer
            queue_service = app_container.getInstance('queue_service')
            notification = app_container.getInstance('notification_service')
            return SoporteClientesHandlerEventConsumer(queue_service, app_container, notification)
        app_container.bind(SOPORTECLI_HANDLERS_EVENT_CONSUMER, soportecli_handlers_event_consumer)

        def depurar_logs_pronatel_handler(name):
            from src.pronatel.logs.services import DepurarLogsPronatel
            return DepurarLogsPronatel(app_container.getInstance('sftp_service'))
        app_container.bind(DEPURAR_LOGS_PRONATEL, depurar_logs_pronatel_handler)

