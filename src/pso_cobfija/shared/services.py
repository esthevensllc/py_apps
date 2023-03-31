PLANO_REPOSITORY = 'src.pso_cobfija.planos.PlanoRepository'
LOAD_GEJSON_PLANOS = 'src.pso_cobfija.planos.LoadgeojsonPlanos'
CREATE_GEOJSON_FROMDB = 'src.pso_cobfija.planos.CreateGeojsonFromDB'
GEOJSON_CONSUMER = 'src.pso_cobfija.planos.GeojsonConsumer'

class PsoCobfijaAppProvider:
    def __init__(self, app_container):
        def import_plano_repo(name):
            from src.pso_cobfija.planos.repository import PlanoRepository
            oracle_db = app_container.getInstance('dboracle')
            return PlanoRepository(oracle_db)
        app_container.bind(PLANO_REPOSITORY, import_plano_repo)

        def import_LoadgeojsonPlanos(name):
            from src.pso_cobfija.planos.services import LoadgeojsonPlanos
            repo = app_container.getInstance(PLANO_REPOSITORY)
            return LoadgeojsonPlanos(repo)
        app_container.bind(LOAD_GEJSON_PLANOS, import_LoadgeojsonPlanos)

        def import_CreateGeojsonFromDB(name):
            from src.pso_cobfija.planos.services import CreateGeojsonFromDB
            sftp_service = app_container.getInstance('sftp_service')
            return CreateGeojsonFromDB(app_container.getInstance('dboracle'), sftp_service)
        app_container.bind(CREATE_GEOJSON_FROMDB, import_CreateGeojsonFromDB)

        def import_geojson_consumer(name):
            from src.pso_cobfija.planos.services import GeojsonConsumer
            queue_service = app_container.getInstance('queue_service')
            notification_service = app_container.getInstance('notification_service')
            return GeojsonConsumer(queue_service, app_container, notification_service)
        app_container.bind(GEOJSON_CONSUMER, import_geojson_consumer)