import requests
import json
from src.shared.config import (STORAGE_DIR)

class LoadgeojsonPlanos:
    def __init__(self, repository):
        self.repository = repository
        # self.geojson_url="http://172.17.27.157/portalmonitoreo/assets/map/map_19_6748.json"
        self.geojson_path = f"{STORAGE_DIR}pso_cobfija/map_19_6748.json"

    def execute(self):
        #geojson = requests.get(self.geojson_url)
        #geojson = geojson.json()
        #geojson_features = geojson['features']
        print(f"Cargando planos")
        duplicados = {}
        try:
            file = open(self.geojson_path, 'r', encoding="utf-8")
            geojson = json.loads(file.read())
            file.close()
            geojson_features = geojson['features']
            planos = []
            # carga planos en array
            for index in range(len(geojson_features)):
                plano_to_add = {}
                for propIndex in geojson_features[index]['properties']:
                    plano_to_add[propIndex.lower()] = geojson_features[index]['properties'][propIndex]
                if 'geometry' not in geojson_features[index].keys():
                    print(geojson_features[index])
                    plano_to_add['geometry'] = None
                else:
                    plano_to_add['geometry'] = json.dumps(geojson_features[index]['geometry'])
                planos.append(plano_to_add)

                if duplicados.get(plano_to_add['nombre']) is None:
                    duplicados[plano_to_add['nombre']] = 0
                duplicados[plano_to_add['nombre']] += 1
            
            self.repository.delete_all()
            self.repository.insert_from_array(planos)

            self.repository.delete_all_backup()
            self.repository.insert_backup()
            print(f"planos cargados: {len(planos)}")

            # genera geojson duplicados
            duplicados = list(filter(lambda name: duplicados[name] > 1, list(duplicados)))
            print(f"duplicados: {len(duplicados)}")
            geojson['features'] = list(filter(lambda index: index['properties']['Nombre'] in duplicados, geojson_features))
            file = open(self.geojson_path.replace('.json', '_duplicados.json'), 'w')
            file.write(json.dumps(geojson))
            file.close()
        except BaseException as e:
            self.repository.delete_all()
            self.repository.insert_from_backup()
            print(f"planos cargados desde backup")
            raise e

        self.repository.exec_procedure('PSO_INSERTBASE_19.SP_PLANOS_MAESTRO')
        import src.pso_cobfija.planos.extra.load_ubigeos_faltantes
        self.repository.exec_procedure('PSO_INSERTBASE_19.SP_PLANOS_MAESTRO_ADD_UBIGEO_DATA')
