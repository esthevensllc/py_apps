from shapely import wkt
from shapely.geometry import Polygon
from shapely.strtree import STRtree
from shapely.validation import make_valid
import json

class LoadDataFijaUbigeosFaltantes:
    def __init__(self, repository, inei_repository):
        self.repository = repository
        self.inei_repository = inei_repository

    def execute(self):
        data_fija_list = self.repository.get_with_geometry_where_ubigeo_is_null()
        inei_ubigeos = self.inei_repository.get_ubigeos_with_poligono()
        inei_tree = self.__get_inei_strtree(inei_ubigeos)

        print("data_fija_list: {}".format(len(data_fija_list)))
        print("inei_ubigeos: {}".format(len(inei_ubigeos)))

        str_tree_nbr = 0
        registros_to_update = []
        for row in data_fija_list:
            # print(row[1].read())
            error_ocurred = False
            geometry = json.loads(row['geometry'])
            p2 = Polygon(geometry['coordinates'][0][0])
            if not p2.is_valid:
                p2 = make_valid(p2)
                # error_ocurred = True
            ubigeo_finded = {'name': row['name'], 'ubigeo': None, 'intersection': 0}
            ubigeos = []
            for o in inei_tree.query(p2):
                if(o.intersects(p2)):
                    area = 0
                    try:
                        area = o.intersection(p2).area
                    except:
                        area = o.intersection(make_valid(p2)).area
                        error_ocurred = True
                    if ubigeo_finded['intersection'] < area:
                        ubigeo_data = o.data.copy()
                        ubigeo_data['name'] = row['name']
                        ubigeo_data['intersection'] = area
                        ubigeo_finded = ubigeo_data
                    ubigeos.append(ubigeo_data)
            if error_ocurred:
                print(ubigeos)
                print(ubigeo_finded)
            else:
                if ubigeo_finded['ubigeo'] is not None:
                    # update_table(ubigeo_finded['ubigeo'], ubigeo_finded['name'])
                    ubigeo_finded.pop('intersection')
                    ubigeo_finded.pop('ubigeo_dpto')
                    ubigeo_finded.pop('ubigeo_prov')
                    ubigeo_finded.pop('ubigeo_dist')
                    registros_to_update.append(ubigeo_finded)
                    str_tree_nbr += 1
        
        self.repository.update_ubigeos_from_array(registros_to_update)
        print("Registros actualizados: ", str_tree_nbr)

        
    def __get_inei_strtree(self, inei_ubigeos):
        polygons = []
        for row in inei_ubigeos:
            data = row.copy()
            data.pop('polygono')

            p2 = wkt.loads('POLYGON(('+row['polygono']+'))')
            p2.data = data
            polygons.append(p2)
        inei_tree = STRtree(polygons)
        return inei_tree