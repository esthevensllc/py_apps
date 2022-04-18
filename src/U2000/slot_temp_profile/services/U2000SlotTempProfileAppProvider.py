REPOSITORY = 'U2000.U2000SlotTempProfileRepository'
LOAD_SLOT_TEMP_PROF = 'U2000.LoadSlotTempProfile'
SLOT_TEMP_PROF_CONSUMER = 'U2000.U2000SlotTempProfileEventConsumer'
SLOT_TEMP_PROF_PRODUCER = 'U2000.U2000SlotTempProfileProducer'

class U2000SlotTempProfileAppProvider:
    def __init__(self, app_container):
        def import_repository(name):
            from src.U2000.slot_temp_profile.repository import U2000SlotTempProfileRepository
            oracle_db = app_container.getInstance('dboracle')
            return U2000SlotTempProfileRepository(oracle_db)
        app_container.bind(REPOSITORY, import_repository)

        def import_LoadSlotTempProfile(name):
            from src.U2000.slot_temp_profile.services.LoadSlotTempProfile import LoadSlotTempProfile
            repository = app_container.getInstance(REPOSITORY)
            remote_connect = app_container.getInstance('remote_connect')
            remote_connect.useConnection('default')
            control_carga_repo = app_container.getInstance('control_carga_repo')
            return LoadSlotTempProfile(repository, remote_connect, control_carga_repo)
        app_container.bind(LOAD_SLOT_TEMP_PROF, import_LoadSlotTempProfile)

        def import_queue_consumer(name):
            from src.U2000.slot_temp_profile.services.U2000SlotTempProfileEventConsumer import U2000SlotTempProfileEventConsumer
            queue_service = app_container.getInstance('queue_service')
            service = app_container.getInstance(LOAD_SLOT_TEMP_PROF)
            return U2000SlotTempProfileEventConsumer(queue_service, service)
        app_container.bind(SLOT_TEMP_PROF_CONSUMER, import_queue_consumer)

        def import_queue_consumer(name):
            from src.U2000.slot_temp_profile.services.U2000SlotTempProfileProducer import U2000SlotTempProfileProducer
            queue_service = app_container.getInstance('queue_service')
            remote_connect = app_container.getInstance('remote_connect')
            remote_connect.useConnection('default')
            control_carga_repo = app_container.getInstance('control_carga_repo')
            return U2000SlotTempProfileProducer(queue_service, remote_connect, control_carga_repo)
        app_container.bind(SLOT_TEMP_PROF_PRODUCER, import_queue_consumer)