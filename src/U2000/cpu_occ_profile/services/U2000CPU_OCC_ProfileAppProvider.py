REPOSITORY = 'U2000.U2000CPU_OCC_ProfileRepository'
LOAD_CPU_OCC_PROF = 'U2000.LoadCPU_OCC_Profile'
CPU_OCC_PROF_CONSUMER = 'U2000.U2000CPU_OCC_ProfileEventConsumer'
CPU_OCC_PROF_PRODUCER = 'U2000.U2000CPU_OCC_ProfileProducer'

class U2000CPU_OCC_ProfileAppProvider:
    def __init__(self, app_container):
        def import_repository(name):
            from src.U2000.cpu_occ_profile.repository import U2000CPU_OCC_ProfileRepository
            oracle_db = app_container.getInstance('dboracle')
            return U2000CPU_OCC_ProfileRepository(oracle_db)
        app_container.bind(REPOSITORY, import_repository)

        def import_LoadCPU_OCC_Profile(name):
            from src.U2000.cpu_occ_profile.services.LoadCPU_OCC_Profile import LoadCPU_OCC_Profile
            repository = app_container.getInstance(REPOSITORY)
            remote_connect = app_container.getInstance('remote_connect')
            remote_connect.useConnection('default')
            control_carga_repo = app_container.getInstance('control_carga_repo')
            return LoadCPU_OCC_Profile(repository, remote_connect, control_carga_repo)
        app_container.bind(LOAD_CPU_OCC_PROF, import_LoadCPU_OCC_Profile)

        def import_queue_consumer(name):
            from src.U2000.cpu_occ_profile.services.U2000CPU_OCC_ProfileEventConsumer import U2000CPU_OCC_ProfileEventConsumer
            queue_service = app_container.getInstance('queue_service')
            service = app_container.getInstance(LOAD_CPU_OCC_PROF)
            return U2000CPU_OCC_ProfileEventConsumer(queue_service, service)
        app_container.bind(CPU_OCC_PROF_CONSUMER, import_queue_consumer)

        def import_queue_producer(name):
            from src.U2000.cpu_occ_profile.services.U2000CPU_OCC_ProfileProducer import U2000CPU_OCC_ProfileProducer
            queue_service = app_container.getInstance('queue_service')
            remote_connect = app_container.getInstance('remote_connect')
            remote_connect.useConnection('default')
            control_carga_repo = app_container.getInstance('control_carga_repo')
            return U2000CPU_OCC_ProfileProducer(queue_service, remote_connect, control_carga_repo)
        app_container.bind(CPU_OCC_PROF_PRODUCER, import_queue_producer)