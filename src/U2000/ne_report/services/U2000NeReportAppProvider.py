REPOSITORY = 'U2000.U2000NeReportRepository'
LOAD_NE_REPORT = 'U2000.LoadNeReport'
NE_REPORT_CONSUMER = 'U2000.U2000NeReportEventConsumer'
NE_REPORT_PRODUCER = 'U2000.ne_report.NeReportProducer'

class U2000NeReportAppProvider:
    def __init__(self, app_container):
        def import_repository(name):
            from src.U2000.ne_report.repository import U2000NeReportRepository
            oracle_db = app_container.getInstance('dboracle')
            return U2000NeReportRepository(oracle_db)
        app_container.bind(REPOSITORY, import_repository)

        def import_LoadNeReport(name):
            from src.U2000.ne_report.services.LoadNeReport import LoadNeReport
            repository = app_container.getInstance(REPOSITORY)
            remote_connect = app_container.getInstance('remote_connect')
            remote_connect.useConnection('default')
            control_carga_repo = app_container.getInstance('control_carga_repo')
            return LoadNeReport(repository, remote_connect, control_carga_repo)
        app_container.bind(LOAD_NE_REPORT, import_LoadNeReport)

        def import_queue_consumer(name):
            from src.U2000.ne_report.services.U2000NeReportEventConsumer import U2000NeReportEventConsumer
            queue_service = app_container.getInstance('queue_service')
            service = app_container.getInstance(LOAD_NE_REPORT)
            return U2000NeReportEventConsumer(queue_service, service)
        app_container.bind(NE_REPORT_CONSUMER, import_queue_consumer)

        def import_queue_producer(name):
            from src.U2000.ne_report.services.NeReportProducer import NeReportProducer
            queue_service = app_container.getInstance('queue_service')
            remote_connect = app_container.getInstance('remote_connect')
            remote_connect.useConnection('default')
            control_carga_repo = app_container.getInstance('control_carga_repo')
            return NeReportProducer(queue_service, remote_connect, control_carga_repo)
        app_container.bind(NE_REPORT_PRODUCER, import_queue_producer)