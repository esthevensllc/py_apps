import requests
import json
from src.shared.config import (BASE_DIR, STORAGE_DIR)
from src.PSO_19.PSO_19_6748.repository import PSO_19_6748_Repository

class Load_geojson_planos:
    def __init__(self, repository):
        self.repository = repository
        self.geojson_url="http://localhost/portalmonitoreo/assets/map/Cobertura_FTTH-HFC.json"

    def execute(self):
        geojson = requests.get(self.geojson_url)
        geojson = geojson.json()
        geojson_features = geojson['features']
        planos = []
        for index in range(len(geojson_features)):
            plano_to_add = geojson_features[index]['properties']
            plano_to_add['GEOMETRY'] = json.dumps(geojson_features[index]['geometry'])
            if 'ID' not in plano_to_add.keys():
                plano_to_add['ID'] = None
            planos.append(plano_to_add)
        
        print("cargando planos PSO_0DATA_19_6748_PLANOS")
        self.repository.insert_from_array_to_planos_temp(planos)
        self.repository.insert_planos_from_planos_temp()