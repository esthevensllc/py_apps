from shapely import wkt
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.strtree import STRtree
from shapely.validation import make_valid
import json

class update_ubigeos_faltantes:
    def __init__(self, repository, inei_repo):
        self.repository = repository
        self.inei_repo = inei_repo

    def execute(self):
        pso_list = self.repository.get_lat_lon_base_where_ubigeo_is_null()
        ubigeos_inei = self.inei_repo.get_ubigeos_with_poligono()

        print('inei_poligonos: {}'.format(len(ubigeos_inei)))
        print('pso_19_6748: {}'.format(len(pso_list)))

        self.change_ubigeos_of_19_6748(ubigeos_inei, pso_list)

    def change_ubigeos_of_19_6748(self, inei_poligonos, pso_19_6748):
        # print(PSO_0DATA_19_6748_TEST)
        inei_tree = self.get_tree_polygons(inei_poligonos)

        registros_to_update = []
        for row in pso_19_6748:
            point = Point(row['lon_base'], row['lat_base'])
            # print(len(inei_tree.query(point)))
            for polygon in inei_tree.query(point):
                if polygon.contains(point):
                    data_to_add = polygon.data.copy()
                    data_to_add['msisdm'] = row['msisdm']
                    # print(polygon.data)
                    registros_to_update.append(data_to_add)
        
        self.repository.update_ubigeos_from_array(registros_to_update)
        print("Registros actualizados: ", len(registros_to_update))

    def get_tree_polygons(self, inei_poligonos):
        polygons = []
        i = 0
        for row in inei_poligonos:
            # polygon = ''.join(row[1].read())
            # p2 = wkt.loads('POLYGON(('+polygon+'))')
            # polygon = row[1].read()
            p2 = wkt.loads('POLYGON(('+row['polygono']+'))')
            p2.data = {'nombdep': row['departamento'], 'nombprov': row['provincia'], 'nombdist': row['distrito'], 'iddpto': row['ubigeo_dpto'], 'idprov':row['ubigeo_prov'], 'iddist':row['ubigeo_dist']}
            polygons.append(p2)
            i += 1
        inei_tree = STRtree(polygons)
        return inei_tree
