import cx_Oracle

class SitesRepository:
    def __init__(self, db):
        self.db = db
        self.table = "PSEG_0DATAGMDTX_API"

    def delete_all(self):
        self.db.query(f'DELETE FROM {self.table}')

    def insert_from_array(self, registros):
        template = f"""INSERT INTO {self.table}(
        id_site, codigo, nombre, direccion, latitud, longitud, router_agregacion, router_acceso, fecha_creacion,
        resp_creacion, fecha_cambio, resp_cambio, fecha_baja, resp_baja, altura_torre, altura_predio, altitud,
        id_tx, id_integ, id_estado, id_torre, id_tipo, ccpp, id_mtc, prob_gub, id_tipo_gub, con_gps, tx,
        integracion, estado, tipo, permiso_gub,
        adddate) VALUES (
        :id_site, :codigo, :nombre, :direccion, :latitud, :longitud, :router_agregacion, :router_acceso, to_date(:fecha_creacion, 'yyyy-mm-dd hh24:mi:ss'),
        :resp_creacion, to_date(:fecha_cambio, 'yyyy-mm-dd hh24:mi:ss'), :resp_cambio, to_date(:fecha_baja, 'yyyy-mm-dd hh24:mi:ss'), :resp_baja, :altura_torre, :altura_predio, :altitud,
        :id_tx, :id_integ, :id_estado, :id_torre, :id_tipo, :ccpp, :id_mtc, :prob_gub, :id_tipo_gub, :con_gps, :tx,
        :integracion, :estado, :tipo, :permiso_gub,
        TRUNC(SYSDATE, 'DD'))"""
        bindings = {
            'id_site': cx_Oracle.NUMBER,
            'codigo': cx_Oracle.STRING,
            'nombre': cx_Oracle.STRING,
            'direccion': cx_Oracle.STRING,
            'latitud': cx_Oracle.STRING,
            'longitud': cx_Oracle.STRING,
            'router_agregacion': cx_Oracle.STRING,
            'router_acceso': cx_Oracle.STRING,
            'fecha_creacion': cx_Oracle.STRING,
            'resp_creacion': cx_Oracle.STRING,
            'fecha_cambio': cx_Oracle.STRING,
            'resp_cambio': cx_Oracle.STRING,
            'fecha_baja': cx_Oracle.STRING,
            'resp_baja': cx_Oracle.STRING,
            'altura_torre': cx_Oracle.NUMBER,
            'altura_predio': cx_Oracle.NUMBER,
            'altitud': cx_Oracle.NUMBER,
            'id_tx': cx_Oracle.NUMBER,
            'id_integ': cx_Oracle.NUMBER,
            'id_estado': cx_Oracle.NUMBER,
            'id_torre': cx_Oracle.NUMBER,
            'id_tipo': cx_Oracle.NUMBER,
            'ccpp': cx_Oracle.STRING,
            'id_mtc': cx_Oracle.STRING,
            'prob_gub': cx_Oracle.NUMBER,
            'id_tipo_gub': cx_Oracle.NUMBER,
            'con_gps': cx_Oracle.STRING,
            'tx': cx_Oracle.STRING,
            'integracion': cx_Oracle.STRING,
            'estado': cx_Oracle.STRING,
            'tipo': cx_Oracle.STRING,
            'permiso_gub': cx_Oracle.STRING,
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros)