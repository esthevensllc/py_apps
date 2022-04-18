import json
from src.shared.config import STORAGE_DIR

class create_geojson_planos_duplicados:
    def __init__(self, repository):
        self.repository = repository
        self.storage_dir = STORAGE_DIR+'pso_19/'

    def execute(self):
        planos = self.repository.get_planos_duplicados_in_temp()
        geojson = {'type': 'FeatureCollection', 'features': []}

        for index in range(len(planos)):
            plano = planos[index]
            feature_to_add = {"type": "Feature", "properties": {}, "geometry": {}}
            feature_to_add['properties'] = {'ID': plano[0], 'NOMBRE': plano[1], 'FECHA_INSERCION': plano[3], 'FECHA_ACTUALIZACION': plano[4], 'ESTADO': plano[5], "fillColor": plano[6]}
            feature_to_add['geometry'] = json.loads(plano[2])
            geojson['features'].append(feature_to_add)
        file = open(self.storage_dir+'map_19_6748_temp.json', 'w')
        file.write(json.dumps(geojson))
        file.close()