# from shapely import wkt
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.strtree import STRtree
import json

class UpdateFlagCoberturaEmpresas:
    def __init__(self, repository, pso_19_6748_planos_repo):
        self.repository = repository
        self.pso_19_6748_planos_repo = pso_19_6748_planos_repo
    
    def execute(self):
        pso_list = self.repository.get_lat_lon_where_flag_cobertura_is_null()
        pso_planos = self.pso_19_6748_planos_repo.get_geometry()

        print(pso_list[0])
        print("PSO_0DATA_19_6748_6928_TEST: {}".format(len(pso_list)))
        print("Planos: {}".format(len(pso_planos)))

        planos_tree = self.get_strtree_polygons(pso_planos)

        registros_to_update = []
        for row in pso_list:
            point = Point(row['longitud'], row['latitud'])
            for polygon in planos_tree.query(point):
                if polygon.contains(point):
                    registros_to_update.append({'ndoc': row['ndoc'], 'flag_cobertura': 1})
        
        self.repository.update_flat_cobertura_from_array(registros_to_update)
        print ("Registros actualizados: ", len(registros_to_update))
    
    def get_strtree_polygons(self, planos):
        polygons = []
        i = 0
        for row in planos:
            geometry = json.loads(row['geometry'])
            p2 = Polygon(geometry['coordinates'][0][0])
            p2.nombre = row['nombre']
            polygons.append(p2)
            i += 1
        str_tree = STRtree(polygons)
        return str_tree
