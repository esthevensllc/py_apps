from src.U2000.alarmas.services.LoadAlarmasU2000 import LoadAlarmasU2000

REPOSITORY = 'AlarmasU2000_Repository'
LOAD_ALARMAS_U2000 = 'LoadAlarmasU2000'
ALARMAS_U2000_COMSUMER = 'U2000AlarmasEventConsumer'
ALARMAS_U2000_PRODUCER = 'U2000AlarmasEventProducer'

class U2000AlarmasAppProvider:
    def __init__(self, app_container):
        def import_repository(name):
            from src.U2000.alarmas.repository import AlarmasU2000_Repository
            oracle_db = app_container.getInstance('dboracle')
            return AlarmasU2000_Repository(oracle_db)
        app_container.bind(REPOSITORY, import_repository)

        def import_LoadAlarmasU2000(name):
            from src.U2000.alarmas.services.LoadAlarmasU2000 import LoadAlarmasU2000
            repository = app_container.getInstance(REPOSITORY)
            remote_connect = app_container.getInstance('remote_connect')
            remote_connect.useConnection('default')
            control_carga_repo = app_container.getInstance('control_carga_repo')
            return LoadAlarmasU2000(repository, remote_connect, control_carga_repo)
        app_container.bind(LOAD_ALARMAS_U2000, import_LoadAlarmasU2000)

        def import_queue_consumer(name):
            from src.U2000.alarmas.services.U2000AlarmasEventConsumer import U2000AlarmasEventConsumer
            queue_service = app_container.getInstance('queue_service')
            service = app_container.getInstance(LOAD_ALARMAS_U2000)
            return U2000AlarmasEventConsumer(queue_service, service)
        app_container.bind(ALARMAS_U2000_COMSUMER, import_queue_consumer)

        def import_event_producer(name):
            from src.U2000.alarmas.services.U2000AlarmasEventProducer import U2000AlarmasEventProducer
            queue_service = app_container.getInstance('queue_service')
            remote_connect = app_container.getInstance('remote_connect')
            remote_connect.useConnection('default')
            control_carga_repo = app_container.getInstance('control_carga_repo')
            return U2000AlarmasEventProducer(queue_service, remote_connect, control_carga_repo)
        app_container.bind(ALARMAS_U2000_PRODUCER, import_event_producer)
