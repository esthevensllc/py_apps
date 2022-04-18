REPOSITORY = 'PSO_19.data_fija.DataFijaRepository'
LOAD_DATA_FIJA_UBIGEOS_FALTANTES = 'PSO_19.data_fija.LoadDataFijaUbigeosFaltantes'

class DataFijaAppProvider:
    def __init__(self, app_container):
        def import_repository(name):
            from src.PSO_19.data_fija.repository import DataFijaRepository
            dependencies = app_container.getInstancesInArray(['dboracle'])
            return DataFijaRepository(*dependencies)
        app_container.bind(REPOSITORY, import_repository)

        def import_LOAD_DATA_FIJA_UBIGEOS_FALTANTES(name):
            from src.PSO_19.data_fija.services.LoadDataFijaUbigeosFaltantes import LoadDataFijaUbigeosFaltantes
            dependencies = app_container.getInstancesInArray([REPOSITORY, 'inei_repo'])
            return LoadDataFijaUbigeosFaltantes(*dependencies)
        app_container.bind(LOAD_DATA_FIJA_UBIGEOS_FALTANTES, import_LOAD_DATA_FIJA_UBIGEOS_FALTANTES)