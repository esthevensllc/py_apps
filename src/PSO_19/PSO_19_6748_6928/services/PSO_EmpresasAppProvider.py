REPOSITORY = 'PSO_19.PSO_19_6748_6928.PSO_19_6748_6928Repository'
UPDATE_FLAG_COBERTURA = 'PSO_19.PSO_19_6748_6928.UpdateFlagCoberturaEmpresas'

class PSO_EmpresasAppProvider:
    def __init__(self, app_container):
        def import_repository(name):
            from src.PSO_19.PSO_19_6748_6928.repository import PSO_19_6748_6928Repository
            oracle_db = app_container.getInstance('dboracle')
            return PSO_19_6748_6928Repository(oracle_db)
        app_container.bind(REPOSITORY, import_repository)

        def import_update_flag_cobertura(name):
            from src.PSO_19.PSO_19_6748.services.PSO_19_6748AppProvider import PLANOS_REPOSITORY
            from src.PSO_19.PSO_19_6748_6928.services.UpdateFlagCoberturaEmpresas import UpdateFlagCoberturaEmpresas
            dependencies = app_container.getInstancesInArray([REPOSITORY, PLANOS_REPOSITORY])
            return UpdateFlagCoberturaEmpresas(*dependencies)
        app_container.bind(UPDATE_FLAG_COBERTURA, import_update_flag_cobertura)