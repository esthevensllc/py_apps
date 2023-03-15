import cx_Oracle

class CapacidadSatRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'tx_capacidad_sat_gmd'

    def delete_by_f_actualizacion(self, f_actualizacion):
        query = f"DELETE FROM {self.table} WHERE F_ACTUALIZACION = TO_DATE('{f_actualizacion}', 'YYYY-MM-DD')"
        self.db.query(query)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(F_ACTUALIZACION, codigo, sede, capacidad) VALUES (TRUNC(SYSDATE, 'DD'), :codigo, :sede, :capacidad)"
        bindings = {
            'codigo': cx_Oracle.STRING,
            'sede': cx_Oracle.STRING,
            'capacidad': cx_Oracle.NUMBER
        }
        
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 5000}
        self.db.save_from_array2(config, registros_to_insert)