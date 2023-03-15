PLANO_REPOSITORY = 'src.pso_cobfija.planos.PlanoRepository'
LOAD_GEJSON_PLANOS = 'src.pso_cobfija.planos.LoadgeojsonPlanos'

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