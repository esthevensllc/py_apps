import cx_Oracle
import logging
import pyproj

from shapely import wkt
from shapely.geometry import Point
from shapely.strtree import STRtree
from shapely.ops import transform

from functools import partial

def buffer_in_meters(lng, lat, radius):
    wgs84_pt = Point(lng, lat)

    wgs84 = pyproj.CRS('EPSG:4326')
    utm = pyproj.CRS('EPSG:3857')

    project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
    project_to_latlng = pyproj.Transformer.from_crs(utm, wgs84, always_xy=True).transform

    utm_point = transform(project, wgs84_pt)
    
    buffer_meters = utm_point.buffer(radius)
    buffer_latlng = transform(project_to_latlng, buffer_meters)

    return buffer_latlng

logging.basicConfig(level=logging.DEBUG, format='%(message)s')

def set_process_proximity(radio):
    points = [] 
    msisdm_array = []
    temp_cellname = [] 
    distancia = {}
    i = 0

    for row in res1:
        points.append(buffer_in_meters(row[1], row[2], radio))
        points[i].msisdm = row[0]
        # msisdm_array.append(row[0])
        i += 1
    tree = STRtree(points)

    str_tree_nbr = 0

    for rowb in res2:
        polygon = ''.join(rowb[1].read())
        p2 = wkt.loads('LINESTRING('+polygon+')')
        index = 0
        for o in tree.query(p2):
            if(p2.intersects(o)):
                str_tree_nbr += 1
                update_table(radio,int(o.msisdm))
            index += 1

    print ("STRtree number: ", str_tree_nbr) 

def update_table(param1, param2):
    print("flag: {}, msisdm: {}".format(param1, param2))
    return ''
    print("----------")

    if(param1 == 250):
        sql = 'update PSO_0DATA_19_6748_TEST set flag_fo_250m = 1 where msisdm = :param2'
    else:
        sql = 'update PSO_0DATA_19_6748_TEST set flag_fo_500m = 1 where msisdm = :param2'
    try:
        # execute the insert statement
        cur.execute(sql, param2=param2)
        # commit the change
        Ocon.commit()  
    except Ocon.Error as error:
        print(error)

def select_table():
    cur.execute("select msisdm,lon_base,lat_base from PSO_0DATA_19_6748_TEST where lat_base is not null and lon_base is not null and estado=1")
    return cur.fetchall()

if __name__ == '__main__':

    cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_19_12")
    Ocon=cx_Oracle.connect('SMART','Sm4rt12$$', cx_Oracle.makedsn("scan-fcprod", 1521, service_name="SMART"))
    #Ocon=cx_Oracle.connect('SMART','Sm4rt12$$','172.17.39.66:1521/SMART')
    cur = Ocon.cursor()

    cur.execute("select cod_enlace,polygono from KML_POLYGONOS_FO where polygono is not null")
    res2 = cur.fetchall()

    res1 = select_table()

    set_process_proximity(250)
    set_process_proximity(500)