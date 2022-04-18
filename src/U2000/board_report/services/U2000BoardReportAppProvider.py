REPOSITORY = 'U2000.U2000BoardReportRepository'
LOAD_BOARD_REPORT = 'U2000.LoadBoardReport'
BOARD_REPORT_CONSUMER = 'U2000.U200BoardReportEventConsumer'
BOARD_REPORT_PRODUCER = 'U2000.BoardReportEventProducer'

class U2000BoardReportAppProvider:
    def __init__(self, app_container):
        def import_repository(name):
            from src.U2000.board_report.repository import U2000BoardReportRepository
            oracle_db = app_container.getInstance('dboracle')
            return U2000BoardReportRepository(oracle_db)
        app_container.bind(REPOSITORY, import_repository)

        def import_LoadBoardReport(name):
            from src.U2000.board_report.services.LoadBoardReport import LoadBoardReport
            repository = app_container.getInstance(REPOSITORY)
            remote_connect = app_container.getInstance('remote_connect')
            remote_connect.useConnection('default')
            control_carga_repo = app_container.getInstance('control_carga_repo')
            return LoadBoardReport(repository, remote_connect, control_carga_repo)
        app_container.bind(LOAD_BOARD_REPORT, import_LoadBoardReport)

        def import_queue_consumer(name):
            from src.U2000.board_report.services.U2000BoardReportEventConsumer import U2000BoardReportEventConsumer
            queue_service = app_container.getInstance('queue_service')
            service = app_container.getInstance(LOAD_BOARD_REPORT)
            return U2000BoardReportEventConsumer(queue_service, service)
        app_container.bind(BOARD_REPORT_CONSUMER, import_queue_consumer)

        def import_queue_producer(name):
            from src.U2000.board_report.services.BoardReportEventProducer import BoardReportEventProducer
            queue_service = app_container.getInstance('queue_service')
            remote_connect = app_container.getInstance('remote_connect')
            remote_connect.useConnection('default')
            control_carga_repo = app_container.getInstance('control_carga_repo')
            return BoardReportEventProducer(queue_service, remote_connect, control_carga_repo)
        app_container.bind(BOARD_REPORT_PRODUCER, import_queue_producer)