import cx_Oracle

class SitesRepository:
    def __init__(self, db):
        self.db = db
        self.table = "PSEG_0DATAGMDTX_API"

    def delete_all(self):
        self.db.query(f'DELETE FROM {self.table}')

    def insert_from_array(self, registros):
        template = f"INSERT INTO {self.table}(CODIGO, NOMBRE, ROUTER_ACCESO, TX, INTEGRACION, ADDDATE) VALUES (:CODIGO, :NOMBRE, :ROUTER_ACCESO, :TX, :INTEGRACION, TRUNC(SYSDATE, 'DD'))"
        bindings = {
            'CODIGO': cx_Oracle.STRING,
            'NOMBRE': cx_Oracle.STRING,
            'ROUTER_ACCESO': cx_Oracle.STRING,
            'TX': cx_Oracle.STRING,
            'INTEGRACION': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros)