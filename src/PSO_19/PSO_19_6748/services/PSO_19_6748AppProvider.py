REPOSITORY = 'PSO_19.PSO_19_6748.repository.PSO_19_6748_Repository'
PLANOS_REPOSITORY = 'PSO_19.PSO_19_6748.repository.PSO_19_6748_PLANOS_Repository'
LOAD_UBICACION_USUARIOS = 'PSO_19.PSO_19_6748.load_ubicacion_usuarios'
LOAD_PLANOS_SGA = 'PSO_19.PSO_19_6748.load_planos_sga'
LOAD_GEOJSON_PLANOS = 'PSO_19.PSO_19_6748.load_geojson_planos'
UPDATE_UBIGEOS_FALTANTES = 'PSO_19.PSO_19_6748.update_ubigeos_faltantes'

class PSO_19_6748AppProvider:
    def __init__(self, app_container):
        def import_repository(name):
            from src.PSO_19.PSO_19_6748.repository import PSO_19_6748_Repository
            oracle_db = app_container.getInstance('dboracle')
            return PSO_19_6748_Repository(oracle_db)
        app_container.bind(REPOSITORY, import_repository)

        def import_planos_repository(name):
            from src.PSO_19.PSO_19_6748.repository import PSO_19_6748_PLANOS_Repository
            oracle_db = app_container.getInstance('dboracle')
            return PSO_19_6748_PLANOS_Repository(oracle_db)
        app_container.bind(PLANOS_REPOSITORY, import_planos_repository)

        def import_load_ubicacion_usuarios(name):
            from src.PSO_19.PSO_19_6748.services.load_ubicacion_usuarios import load_ubicacion_usuarios
            dependencies = app_container.getInstancesInArray([REPOSITORY])
            return load_ubicacion_usuarios(*dependencies)
        app_container.bind(LOAD_UBICACION_USUARIOS, import_load_ubicacion_usuarios)

        def import_Load_planos_sga(name):
            from src.PSO_19.PSO_19_6748.services.load_planos_sga import load_planos_sga
            dependencies = app_container.getInstancesInArray([REPOSITORY])
            return load_planos_sga(*dependencies)
        app_container.bind(LOAD_PLANOS_SGA, import_Load_planos_sga)

        def import_load_geojson_planos(name):
            from src.PSO_19.PSO_19_6748.services.load_geojson_planos import Load_geojson_planos
            dependencies = app_container.getInstancesInArray([REPOSITORY])
            return Load_geojson_planos(*dependencies)
        app_container.bind(LOAD_GEOJSON_PLANOS, import_load_geojson_planos)

        def import_update_ubigeos_faltantes(name):
            from src.PSO_19.PSO_19_6748.services.update_ubigeos_faltantes import update_ubigeos_faltantes
            dependencies = app_container.getInstancesInArray([REPOSITORY, 'inei_repo'])
            return update_ubigeos_faltantes(*dependencies)
        app_container.bind(UPDATE_UBIGEOS_FALTANTES, import_update_ubigeos_faltantes)
        