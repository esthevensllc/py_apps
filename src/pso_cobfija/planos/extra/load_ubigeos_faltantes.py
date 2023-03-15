import cx_Oracle
import logging

from shapely import wkt
from shapely.geometry import Polygon
from shapely.strtree import STRtree
from shapely.validation import make_valid
import json

logging.basicConfig(level=logging.DEBUG, format='%(message)s')

def set_process():
    polygons = []
    i = 0
    for row in res2:
        # polygon = ''.join(row[1].read())
        # p2 = wkt.loads('POLYGON(('+polygon+'))')
        polygon = row[1].read()
        p2 = wkt.loads('POLYGON(('+polygon+'))')
        p2.ubigeo = row[0]
        polygons.append(p2)
        i += 1
    inei_tree = STRtree(polygons)

    # poligonos portal
    str_tree_nbr = 0
    for row in res1:
        # print(row[1].read())
        error_ocurred = False
        geometry = json.loads(row[1].read())
        p2 = Polygon(geometry['coordinates'][0][0])
        if not p2.is_valid:
            p2 = make_valid(p2)
            # error_ocurred = True
        ubigeo_finded = {'name': row[0], 'ubigeo': '', 'intersection': 0}
        ubigeos = []
        index = 0
        for o in inei_tree.query(p2):
            if(o.intersects(p2)):
                area = 0
                try:
                    area = o.intersection(p2).area
                except:
                    area = o.intersection(make_valid(p2)).area
                    error_ocurred = True
                if ubigeo_finded['intersection'] < area:
                    ubigeo_finded = {'name': row[0], 'ubigeo': o.ubigeo, 'intersection': area}
                ubigeos.append({'ubigeo': o.ubigeo, 'intersection': area})
            index += 1
        if error_ocurred:
            print(ubigeos)
            print(ubigeo_finded)
        else:
            if ubigeo_finded['ubigeo'] != '':
                update_table(ubigeo_finded['ubigeo'], ubigeo_finded['name'])
                str_tree_nbr += 1
    print ("STRtree number: ", str_tree_nbr)

def update_table(param1, param2):
    # print("ubigeo:{}, name:{}".format(param1, param2))
    sql = 'update FIJA_PLANOS_MAESTRO SET ubigeo = :param1 WHERE PLANO = :param2'
    try:
        # execute the insert statement
        cur.execute(sql, param1=param1, param2=param2)
        # commit the change
        Ocon.commit()  
    except Ocon.Error as error:
        print(error)

#if __name__ == '__main__':
#cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_19_12")
Ocon=cx_Oracle.connect('SMART','Sm4rt12$$', cx_Oracle.makedsn("scan-fcprod", 1521, service_name="SMART"))
cur = Ocon.cursor()

sql = """select pso.PLANO, pl.geometry from FIJA_PLANOS_MAESTRO pso
INNER join (
    select pl.id, pl.nombre, pl2.geometry from (
        select max(rowid) rowid_, MAX(ID) ID, NOMBRE from FIJA_PLANOS_SGA
        WHERE GEOMETRY IS NOT NULL
        GROUP BY NOMBRE
    ) pl
    inner join FIJA_PLANOS_SGA pl2 on pl2.rowid = pl.rowid_
) pl on pl.nombre = pso.PLANO
where pso.UBIGEO IS NULL"""
cur.execute(sql)
res1 = cur.fetchall()

cur.execute("select ubigeo, polygono from cvm_mtv_kml_inei where ubigeo is not null and polygono is not null")
res2 = cur.fetchall()

result = set_process()
# en proyecto