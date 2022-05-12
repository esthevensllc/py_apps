CARGA_CONFIG_REPOSITORY = 'src.nce.cargas.repository.NCECargaConfigRepository'
SHARED_REPOSITORY = 'src.nce.cargas.repository.SharedRepository'
PM_IG30029_EVENT_PRODUCER = 'src.nce.cargas.services.pm_ig30029_producer'
PM_IG64_EVENT_PRODUCER = 'src.nce.cargas.services.pm_ig64_producer'
BASE_EVENT_PRODUCER = 'src.nce.cargas.services.base_event_producer'
CARGAS_EVENT_PRODUCER = 'src.nce.cargas.services.CargasEventProducer'
LOAD_CSV = 'src.nce.cargas.services.LoadCSV'
NCE_ASYNC_EVENT_CONSUMER = 'src.nce.shared.services.nce_async_event_consumer'

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
            deps = app_container.getInstancesInArray([CARGA_CONFIG_REPOSITORY, BASE_EVENT_PRODUCER])
            return CargasEventProducer(*deps)
        app_container.bind(CARGAS_EVENT_PRODUCER, import_cargas_event_producer)


        def import_carga_config_repository(name):
            from src.nce.cargas.repository import NCECargaConfigRepository
            return NCECargaConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(CARGA_CONFIG_REPOSITORY, import_carga_config_repository)

        def import_shared_repository(name):
            from src.nce.cargas.repository import SharedRepository
            return SharedRepository(app_container.getInstance('dboracle'))
        app_container.bind(SHARED_REPOSITORY, import_shared_repository)

        def import_load_csv(name):
            from src.nce.cargas.services.LoadCSV import LoadCSV
            repository = app_container.getInstance(CARGA_CONFIG_REPOSITORY)
            shared_repository = app_container.getInstance(SHARED_REPOSITORY)
            control_carga_repo = app_container.getInstance('control_carga_repo')
            sftp_service = app_container.getInstance('sftp_service')
            sftp_service.useConnection('nce')
            sftp_service.connect()
            #remote_connect = app_container.getInstance('remote_connect')
            #remote_connect.useConnection('nce')
            return LoadCSV(repository, shared_repository, control_carga_repo, sftp_service)
        app_container.bind(LOAD_CSV, import_load_csv)

        def import_nce_async_event_consumer(name):
            from src.nce.shared.NCEAsyncEventConsumer import NCEAsyncEventConsumer
            repository = app_container.getInstance(CARGA_CONFIG_REPOSITORY)
            return NCEAsyncEventConsumer(app_container.getInstance('queue_service'), app_container, repository)
        app_container.bind(NCE_ASYNC_EVENT_CONSUMER, import_nce_async_event_consumer)

