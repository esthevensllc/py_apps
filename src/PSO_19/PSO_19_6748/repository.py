import cx_Oracle
import random

class PSO_19_6748_Repository:
    def __init__(self, db):
        self.db = db
        self.table = 'PSO_0DATA_19_6748_TEST'
        self.temp_table = 'PSO_0DATA_19_6748_TEMP'
        self.temp_planos_table = 'PSO_0DATA_19_6748_PLANOS_TEMP'
        self.temp_homepass_table = 'PSO_0DATA_19_HOMEPASS'

    def get_lat_lon_base_where_ubigeo_is_null(self):
        sql = "select pso.msisdm, pso.lat_base, pso.lon_base from "+self.table+" pso where pso.estado = 1 and pso.iddist is null"
        new_result = []
        result = self.db.fetch(sql)
        for row in result:
            new_result.append({'msisdm': row[0], 'lat_base': row[1], 'lon_base': row[2]})
        return new_result

    def update(self, data):
        sql = "UPDATE "+self.table+" SET LAT_BASE = {}, LON_BASE = {}, FECHA_ACTUALIZACION=SYSDATE WHERE MSISDM='{}'".format(data['lat_base'], data['lon_base'], data['msisdm'])
        self.db.query(sql)

    def create(self, data):
        sql = "INSERT INTO "+self.table+"(MSISDM,LAT_BASE,LON_BASE, FECHA_INSERCION) VALUES ('{}', {}, {}, SYSDATE)".format(data['lat_base'], data['lon_base'], data['msisdm'])
        self.db.query(sql)

    def find_by_msisdm(self, msisdm):
        sql = "SELECT * FROM "+self.table+" WHERE MSISDM='{}'".format(msisdm)
        result = self.db.fetch(sql)
        for index in range(len(result)):
            return result[index]
        return None

    def insert_from_array_to_temp_space(self, registros_to_insert):
        self.db.query("DELETE FROM "+self.temp_table)
        """insert_into_template = "INSERT INTO "+self.temp_table+"(MSISDM,LAT_BASE,LON_BASE, FECHA_INSERCION, ESTADO) VALUES ('{msisdm}', {lat_base}, {lon_base}, SYSDATE, 1)"
        self.db.save_from_array(insert_into_template, registros_to_insert, "object")"""
        
        insert_into_template = "INSERT INTO "+self.temp_table+"(MSISDM,LAT_BASE,LON_BASE, FECHA_INSERCION, ESTADO) VALUES (:msisdm, :lat_base, :lon_base, SYSDATE, 1)"
        bindings = {'msisdm': cx_Oracle.STRING, 'lat_base': cx_Oracle.STRING, 'lon_base': cx_Oracle.STRING}
        config = {'template': insert_into_template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 5000}
        self.db.save_from_array2(config, registros_to_insert)

    def load_from_temp_space(self):
        sql = """BEGIN PSO_INSERTBASE_19.SP_INSERT_19_6748_FROM_TEMP; END;"""
        self.db.query(sql)

    def update_ubigeos_from_array(self, registros_to_update):
        template = """update """+self.table+""" set
        NOMBDEP = :nombdep,
        NOMBPROV = :nombprov,
        NOMBDIST = :nombdist,
        IDDPTO = :iddpto,
        IDPROV = :idprov,
        IDDIST = :iddist
        where msisdm = :msisdm"""
        bindings = {'nombdep': cx_Oracle.STRING, 'nombprov': cx_Oracle.STRING, 'nombdist': cx_Oracle.STRING, 'iddpto': cx_Oracle.NUMBER, 'idprov': cx_Oracle.NUMBER, 'iddist': cx_Oracle.NUMBER, 'msisdm': cx_Oracle.STRING}
        config = {'template': template, 'bindings': bindings, 'row_type': 'object'}
        self.db.save_from_array2(config, registros_to_update)        

    def insert_from_array_to_planos_temp(self, registros_to_insert):
        self.db.query("DELETE FROM "+self.temp_planos_table)
        insert_into_template = "INSERT INTO "+self.temp_planos_table+"(ID, NOMBRE, GEOMETRY, FECHA_INSERCION) VALUES (:ID, :NOMBRE, :GEOMETRY, SYSDATE)"
        bindings = {'ID': cx_Oracle.NUMBER, 'NOMBRE': cx_Oracle.STRING, 'GEOMETRY': cx_Oracle.CLOB}
        config = {'template': insert_into_template, 'bindings': bindings, 'row_type': 'object'}
        self.db.save_from_array2(config, registros_to_insert)
    
    def insert_planos_from_planos_temp(self):
        sql = """BEGIN PSO_INSERTBASE_19.SP_INSERT_19_6748_PLANOS_FROM_TEMP; END;"""
        self.db.query(sql)

    def get_planos_duplicados_in_temp(self):
        sql = """        
        SELECT a.ID, a.NOMBRE, a.GEOMETRY, TO_CHAR(a.FECHA_INSERCION, 'YYYY-MM-DD HH24:MI:SS'), TO_CHAR(a.FECHA_ACTUALIZACION, 'YYYY-MM-DD HH24:MI:SS'), a.ESTADO
        FROM PSO_0DATA_19_6748_PLANOS_TEMP a
        INNER JOIN (
            SELECT NOMBRE, COUNT(*) as counter FROM PSO_0DATA_19_6748_PLANOS_TEMP GROUP BY NOMBRE HAVING COUNT(*)>1
        ) b on b.nombre = a.nombre
        order by a.nombre
        """
        result = self.db.fetch(sql)
        result_temp = []
        # last_nombre = ''
        colors = {}
        counter = 0
        for index in range(len(result)):
            row = list(result[index])
            if row[1] not in colors.keys():
                counter = counter + 1
                colors[row[1]] = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
            row[2] = row[2].read()
            row.append(colors[row[1]])
            result_temp.append(row)
            # last_nombre = row[0]
        print(counter)
        print(colors)
        return result_temp

    def recargar_from_array_to_homepass_temp(self, registros_to_insert):
        self.db.query("DELETE FROM "+self.temp_homepass_table)
        insert_into_template = "INSERT INTO "+self.temp_homepass_table+"(ITEM, IDPLANO, DESCRIPCION, HHPP_TOTALES) VALUES (:item, :idplano, :descripcion, :hhpp_totales)"
        bindings = {'item': cx_Oracle.NUMBER, 'idplano': cx_Oracle.STRING, 'descripcion': cx_Oracle.STRING, 'hhpp_totales': cx_Oracle.NUMBER}
        config = {'template': insert_into_template, 'bindings': bindings, 'row_type': 'object'}
        self.db.save_from_array2(config, registros_to_insert)

class PSO_19_6748_PLANOS_Repository:
    def __init__(self, db):
        self.db = db
        self.table = 'PSO_0DATA_19_6748_PLANOS'

    def get_geometry(self):
        sql = """select pl.nombre, pl2.geometry from (
            select max(rowid) rowid_, MAX(ID) ID, NOMBRE from """+self.table+"""
            GROUP BY NOMBRE
        ) pl
        inner join """+self.table+""" pl2 on pl2.rowid = pl.rowid_
        where pl2.estado=1"""
        result = self.db.fetch(sql)
        new_result = []
        for row in result:
            new_result.append({'nombre': row[0], 'geometry': row[1].read()})
        return new_result


    
