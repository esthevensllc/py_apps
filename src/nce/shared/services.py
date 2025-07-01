CARGA_CONFIG_REPOSITORY = 'src.nce.cargas.repository.NCECargaConfigRepository'
SHARED_REPOSITORY = 'src.nce.cargas.repository.SharedRepository'
PM_IG30029_EVENT_PRODUCER = 'src.nce.cargas.services.pm_ig30029_producer'
PM_IG64_EVENT_PRODUCER = 'src.nce.cargas.services.pm_ig64_producer'
BASE_EVENT_PRODUCER = 'src.nce.cargas.services.base_event_producer'
CARGAS_EVENT_PRODUCER = 'src.nce.cargas.services.CargasEventProducer'
LOAD_CSV = 'src.nce.cargas.services.LoadCSV'
LOAD_ORACLE_HANDLER = 'src.nce.cargas.services.LoadOracleHandlers'
LOAD_ORACLE_DAY_HANDLER = 'src.nce.cargas.services.LoadOracleDayHandlers'
NCE_ASYNC_EVENT_CONSUMER = 'src.nce.shared.services.nce_async_event_consumer'
# nce clickhouse
CLICKHOUSE_CONFIG_REPOSITORY = 'src.nce.cargas.repository.ClickHouseNCECargaConfigRepository'
CLICKHOUSE_SHARED_REPOSITORY = 'src.nce.cargas.repository.ClickHouseSharedRepository'
CLICKHOUSE_LOAD_CSV = 'src.nce.cargas.services.ClickHouseLoadCSV'
CLICKHOUSE_CARGAS_EVENT_PRODUCER = 'src.nce.cargas.services.ClikHouseCargasEventProducer'
CLICKHOUSE_NCE_ASYNC_EVENT_CONSUMER = "src.nce.shared.services.ch_nce_async_event_consumer"
CLICKHOUSE_DELETER = "src.nce.shared.services.ch_nce_deleter"

NCE_CONFIG_REPO = 'src.nce.alarmas.NCEConfigRepository'
LOAD_NCE_FROM_CONFIG = 'src.nce.alarmas.LoadNCEDataFromConfig'
NCE_EVENT_PRODUCER_FROM_CONFIG = 'src.nce.alarmas.NCEEventProducer'
NCE_EVENT_CONSUMER_FROM_CONFIG = 'src.nce.alarmas.NCEEventConsumerFromConfig'

NCE_INVENTARIO_CONFIG_REPO = 'src.nce.inventario.NCEInventarioConfigRepository'
LOAD_NCE_INVENTARIO_FROM_CONFIG = 'src.nce.inventario.LoadNCEInventarioFromConfig'
NCE_INVENTARIO_EVENT_PRODUCER = 'src.nce.inventario.NCEInventarioEventProducer'
NCE_INVENTARIO_EVENT_CONSUMER = 'src.nce.inventario.NCEInventarioEventConsumerFromConfig'

class NCEAppProvider:
    def __init__(self, app_container):
        def import_pm_ig30029_producer(name):
            from src.nce.PM_IG30029.services.PM_IG30029EventProducer import PM_IG30029EventProducer
            queue_service = app_container.getInstance('queue_service')
            remote_connect = app_container.getInstance('sftp_service')
            remote_connect.useConnection('nce')
            remote_connect.connect()
            control_carga_repo = app_container.getInstance('control_carga_repo')
            # deps = app_container.getInstancesInArray([queue_service, remote_connect, control_carga_repo])
            return PM_IG30029EventProducer(queue_service, remote_connect, control_carga_repo)
        app_container.bind(PM_IG30029_EVENT_PRODUCER, import_pm_ig30029_producer)

        def import_pm_ig64_producer(name):
            from src.nce.PM_IG64.services.PM_IG64EventProducer import PM_IG64EventProducer
            queue_service = app_container.getInstance('queue_service')
            remote_connect = app_container.getInstance('sftp_service')
            remote_connect.useConnection('nce')
            remote_connect.connect()
            control_carga_repo = app_container.getInstance('control_carga_repo')
            # deps = app_container.getInstancesInArray([queue_service, remote_connect, control_carga_repo])
            return PM_IG64EventProducer(queue_service, remote_connect, control_carga_repo)
        app_container.bind(PM_IG64_EVENT_PRODUCER, import_pm_ig64_producer)

        def import_base_event_producer(name):
            from src.nce.cargas.services.BaseGenericEventProducer import BaseGenericEventProducer
            queue_service = app_container.getInstance('queue_service')
            remote_connect = app_container.getInstance('sftp_service')
            remote_connect.useConnection('nce')
            remote_connect.connect()
            control_carga_repo = app_container.getInstance('control_carga_repo')
            # deps = app_container.getInstancesInArray([queue_service, remote_connect, control_carga_repo])
            return BaseGenericEventProducer(queue_service, remote_connect, control_carga_repo)
        app_container.bind(BASE_EVENT_PRODUCER, import_base_event_producer)
        
        def import_cargas_event_producer(name):
            from src.nce.cargas.services.CargasEventProducer import CargasEventProducer
            deps = app_container.getInstancesInArray(['sftp_service', CARGA_CONFIG_REPOSITORY, 'control_carga_repo', 'queue_service', 'cache'])
            return CargasEventProducer(*deps)
        app_container.bind(CARGAS_EVENT_PRODUCER, import_cargas_event_producer)

        def import_clickhouse_cargas_event_producer(name):
            from src.nce.cargas.services.CargasEventProducer import ClickHouseCargasEventProducer
            deps = app_container.getInstancesInArray(['sftp_service', CLICKHOUSE_CONFIG_REPOSITORY, 'control_carga_repo', 'queue_service', 'cache'])
            return ClickHouseCargasEventProducer(*deps)
        app_container.bind(CLICKHOUSE_CARGAS_EVENT_PRODUCER, import_clickhouse_cargas_event_producer)


        def import_carga_config_repository(name):
            from src.nce.cargas.repository import NCECargaConfigRepository
            return NCECargaConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(CARGA_CONFIG_REPOSITORY, import_carga_config_repository)

        def import_clickhouse_config_repository(name):
            from src.nce.cargas.repository import ClickHouseNCECargaConfigRepository
            return ClickHouseNCECargaConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(CLICKHOUSE_CONFIG_REPOSITORY, import_clickhouse_config_repository)
        

        def import_shared_repository(name):
            from src.nce.cargas.repository import SharedRepository
            return SharedRepository(app_container.getInstance('dboracle'))
        app_container.bind(SHARED_REPOSITORY, import_shared_repository)

        def import_clickhouse_shared_repository(name):
            from src.nce.cargas.repository import ClickHouseSharedRepository
            clickhouse = app_container.getInstance('clickhouse')
            clickhouse.useConnection("clickhouse_nce")
            return ClickHouseSharedRepository(clickhouse, app_container.getInstance('dboracle'))
        app_container.bind(CLICKHOUSE_SHARED_REPOSITORY, import_clickhouse_shared_repository)

        def import_load_csv(name):
            from src.nce.cargas.services.LoadCSV import LoadCSV
            from src.nce.cargas.services.CargasEventProducer import NceSftpWrapper
            repository = app_container.getInstance(CARGA_CONFIG_REPOSITORY)
            shared_repository = app_container.getInstance(SHARED_REPOSITORY)
            control_carga_repo = app_container.getInstance('control_carga_repo')
            
            sftp_service = app_container.getInstance('sftp_service')
            sftp_service = NceSftpWrapper(sftp_service, app_container.getInstance('cache'))
            sftp_service.useConnection('nce')
            sftp_service.connect()
            #remote_connect = app_container.getInstance('remote_connect')
            #remote_connect.useConnection('nce')
            return LoadCSV(repository, shared_repository, control_carga_repo, sftp_service)
        app_container.bind(LOAD_CSV, import_load_csv)

        def import_clickhouse_load_csv(name):
            from src.nce.cargas.services.LoadCSV import LoadCSV
            from src.nce.cargas.services.CargasEventProducer import NceSftpWrapper
            repository = app_container.getInstance(CLICKHOUSE_CONFIG_REPOSITORY)
            shared_repository = app_container.getInstance(CLICKHOUSE_SHARED_REPOSITORY)
            control_carga_repo = app_container.getInstance('control_carga_repo')
            sftp_service = app_container.getInstance('sftp_service')
            sftp_service = NceSftpWrapper(sftp_service, app_container.getInstance('cache'))
            sftp_service.useConnection('nce')
            sftp_service.connect()
            return LoadCSV(repository, shared_repository, control_carga_repo, sftp_service)
        app_container.bind(CLICKHOUSE_LOAD_CSV, import_clickhouse_load_csv)

        def import_load_oracle_handlers(name):
            from src.nce.cargas.services.LoadOracleHandlers import LoadOracleHandlers
            return LoadOracleHandlers(app_container.getInstance('dboracle'))
        app_container.bind(LOAD_ORACLE_HANDLER, import_load_oracle_handlers)

        def import_load_oracle_day_handlers(name):
            from src.nce.cargas.services.LoadOracleDayHandlers import LoadOracleDayHandlers
            return LoadOracleDayHandlers(app_container.getInstance('dboracle'))
        app_container.bind(LOAD_ORACLE_DAY_HANDLER, import_load_oracle_day_handlers)

        def import_nce_async_event_consumer(name):
            from src.nce.shared.NCEAsyncEventConsumer import NCEAsyncEventConsumer
            repository = app_container.getInstance(CARGA_CONFIG_REPOSITORY)
            notification_service = app_container.getInstance('notification_service')
            return NCEAsyncEventConsumer(app_container.getInstance('queue_service'), app_container, repository, notification_service)
        app_container.bind(NCE_ASYNC_EVENT_CONSUMER, import_nce_async_event_consumer)

        def import_clickhouse_nce_async_event_consumer(name):
            from src.nce.shared.NCEAsyncEventConsumer import ClickHouseNCEAsyncEventConsumer
            repository = app_container.getInstance(CLICKHOUSE_CONFIG_REPOSITORY)
            notification_service = app_container.getInstance('notification_service')
            return ClickHouseNCEAsyncEventConsumer(app_container.getInstance('queue_service'), app_container, repository, notification_service)
        app_container.bind(CLICKHOUSE_NCE_ASYNC_EVENT_CONSUMER, import_clickhouse_nce_async_event_consumer)

        def import_nce_config_repository(name):
            from src.nce.alarmas.repository import NCEConfigRepository
            return NCEConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(NCE_CONFIG_REPO, import_nce_config_repository)
        def import_load_nce_from_config(name):
            from src.nce.alarmas.services import LoadNCEDataFromConfig
            oracle = app_container.getInstance('dboracle')
            repository = app_container.getInstance(NCE_CONFIG_REPO)
            control_carga_repo = app_container.getInstance('control_carga_repo')
            sftp_service = app_container.getInstance('sftp_service')
            #sftp_service.useConnection('nce')
            #sftp_service.connect()
            #remote_connect = app_container.getInstance('remote_connect')
            #remote_connect.useConnection('nce')
            return LoadNCEDataFromConfig(oracle, repository, sftp_service, control_carga_repo)
        app_container.bind(LOAD_NCE_FROM_CONFIG, import_load_nce_from_config)
        def import_nce_event_producer_from_config(name):
            from src.nce.alarmas.services import NCEEventProducer
            repository = app_container.getInstance(NCE_CONFIG_REPO)
            sftp_service = app_container.getInstance('sftp_service')
            control_carga_repo = app_container.getInstance('control_carga_repo')
            queue_service = app_container.getInstance('queue_service')
            return NCEEventProducer(repository, sftp_service, control_carga_repo, queue_service)
        app_container.bind(NCE_EVENT_PRODUCER_FROM_CONFIG, import_nce_event_producer_from_config)
        def import_nce_event_consumer_from_config(name):
            from src.nce.alarmas.services import NCEEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(NCE_CONFIG_REPO)
            notification_service = app_container.getInstance('notification_service')
            return NCEEventConsumerFromConfig(queue_service, app_container, repository, notification_service)
        app_container.bind(NCE_EVENT_CONSUMER_FROM_CONFIG, import_nce_event_consumer_from_config)

        def import_nce_inventario_repository(name):
            from src.nce.inventario.repository import NCEInventarioConfigRepository
            return NCEInventarioConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(NCE_INVENTARIO_CONFIG_REPO, import_nce_inventario_repository)
        def import_load_nce_inventario_from_config(name):
            from src.nce.inventario.services import LoadNCEInventarioFromConfig
            deps = app_container.getInstancesInArray(["dboracle", NCE_INVENTARIO_CONFIG_REPO, 'sftp_service', 'control_carga_repo'])
            return LoadNCEInventarioFromConfig(*deps)
        app_container.bind(LOAD_NCE_INVENTARIO_FROM_CONFIG, import_load_nce_inventario_from_config)
        def import_load_nce_inventario_event_producer(name):
            from src.nce.inventario.services import NCEInventarioEventProducer
            deps = app_container.getInstancesInArray([NCE_INVENTARIO_CONFIG_REPO, 'sftp_service', 'control_carga_repo', 'queue_service'])
            return NCEInventarioEventProducer(*deps)
        app_container.bind(NCE_INVENTARIO_EVENT_PRODUCER, import_load_nce_inventario_event_producer)
        def import_load_nce_inventario_event_consumer(name):
            from src.nce.inventario.services import NCEInventarioEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(NCE_INVENTARIO_CONFIG_REPO)
            notification_service = app_container.getInstance('notification_service')
            return NCEInventarioEventConsumerFromConfig(queue_service, app_container, repository, notification_service)
        app_container.bind(NCE_INVENTARIO_EVENT_CONSUMER, import_load_nce_inventario_event_consumer)

        """def import_clickhousr_deleter(name):
            from src.nce.cargas.services.deleter import ChTableDeleter
            # queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(CLICKHOUSE_CONFIG_REPOSITORY)
            clickhouse = app_container.getInstance('clickhouse')
            clickhouse.useConnection("clickhouse_nce")
            return ChTableDeleter(repository, clickhouse)
        app_container.bind(CLICKHOUSE_DELETER, import_clickhousr_deleter)
        """

