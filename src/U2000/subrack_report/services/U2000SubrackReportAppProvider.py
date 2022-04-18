REPOSITORY = 'U2000.U2000SubrackReportRepository'
LOAD_SUBRACK_REPORT = 'U2000.LoadSubrackReport'
SUBRACK_REPORT_CONSUMER = 'U2000.U2000SubrackReportEventConsumer'
SUBRACK_REPORT_PRODUCER = 'U2000.SubrackReportProducer'

class U2000SubrackReportAppProvider:
    def __init__(self, app_container):
        def import_repository(name):
            from src.U2000.subrack_report.repository import U2000SubrackReportRepository
            oracle_db = app_container.getInstance('dboracle')
            return U2000SubrackReportRepository(oracle_db)
        app_container.bind(REPOSITORY, import_repository)

        def import_LoadSubrackReport(name):
            from src.U2000.subrack_report.services.LoadSubrackReport import LoadSubrackReport
            repository = app_container.getInstance(REPOSITORY)
            remote_connect = app_container.getInstance('remote_connect')
            remote_connect.useConnection('default')
            control_carga_repo = app_container.getInstance('control_carga_repo')
            return LoadSubrackReport(repository, remote_connect, control_carga_repo)
        app_container.bind(LOAD_SUBRACK_REPORT, import_LoadSubrackReport)

        def import_queue_consumer(name):
            from src.U2000.subrack_report.services.U2000SubrackReportEventConsumer import U2000SubrackReportEventConsumer
            queue_service = app_container.getInstance('queue_service')
            service = app_container.getInstance(LOAD_SUBRACK_REPORT)
            return U2000SubrackReportEventConsumer(queue_service, service)
        app_container.bind(SUBRACK_REPORT_CONSUMER, import_queue_consumer)

        def import_queue_producer(name):
            from src.U2000.subrack_report.services.SubrackReportProducer import SubrackReportProducer
            queue_service = app_container.getInstance('queue_service')
            remote_connect = app_container.getInstance('remote_connect')
            remote_connect.useConnection('default')
            control_carga_repo = app_container.getInstance('control_carga_repo')
            return SubrackReportProducer(queue_service, remote_connect, control_carga_repo)
        app_container.bind(SUBRACK_REPORT_PRODUCER, import_queue_producer)