import cx_Oracle

class SiteOnAirRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'PSEG_0DATAGMDTX'

    def delete_all(self):
        self.db.query(f'DELETE FROM {self.table}')

    def insert_from_array(self, registros):
        template = f"INSERT INTO {self.table}(TSOA_ID, TSOA_CODIGO, TSOA_NOMBRE, TTT_TIPO, TSOA_DIRECCION, TSOA_LATITUD, TSOA_LONGITUD, TSOA_ROUTER_AGREG, EQUIPO, TSOA_ESTADO, TTE_ID, ADDDATE, TERCERO, SATELITAL) VALUES (:tsoa_id, :tsoa_codigo, :tsoa_nombre, :ttt_tipo, :tsoa_direccion, :tsoa_latitud, :tsoa_longitud, :tsoa_router_agreg, :equipo, :tsoa_estado, :tte_id, sysdate, :tercero, :satelital)"
        bindings = {
            'tsoa_id': cx_Oracle.STRING,
            'tsoa_codigo': cx_Oracle.STRING,
            'tsoa_nombre': cx_Oracle.STRING,
            'ttt_tipo': cx_Oracle.STRING,
            'tsoa_direccion': cx_Oracle.STRING,
            'tsoa_latitud': cx_Oracle.STRING,
            'tsoa_longitud': cx_Oracle.STRING,
            'tsoa_router_agreg': cx_Oracle.STRING,
            'equipo': cx_Oracle.STRING,
            'tsoa_estado': cx_Oracle.STRING,
            'tte_id': cx_Oracle.STRING,
            'tercero': cx_Oracle.STRING,
            'satelital': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros)

        