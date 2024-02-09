import cx_Oracle

class ListaHopsRepository:
    def __init__(self, db):
        self.db = db
        self.table = "gmyd_lista_hops_bd"

    def delete_all(self):
        self.db.query(f'DELETE FROM {self.table}')

    def insert_from_array(self, registros):
        template = f"""INSERT INTO {self.table}(
            ID, CODIGO_NE, NOMBRE_NE, CODIGO_FE, NOMBRE_FE, ALTURA_TORRE_NE, ALTURA_PREDIO_NE,
            ALTURA_MW_NE, ALTURA_TORRE_FE, ALTURA_PREDIO_FE, ALTURA_MW_FE, EQUIPO_NE, EQUIPO_FE,
            MARCA_IDU_ORIGEN, MARCA_IDU_DESTINO, ANTENA_NE, ANTENA_FE, DIAMETRO_NE, DIAMETRO_FE,
            GANANCIA_NE, GANANCIA_FE, ANTENA_VENDOR_ORIGEN, ANTENA_VENDOR_DESTINO, POLARIZACION,
            CONFIGURACION, AZIMUTH_NE, AZIMUTH_FE, FECHA_ULTIMO_CAMBIO, FECHA_CREACION, FECHA_APROBACION,
            FECHA_BAJA, RESP_ULTIMO_CAMBIO, RESP_CREACION, RESP_APROBACION, RESP_BAJA, PROYECTO, ESTADO,
            DISTANCIA, ID_MTC_ORIGEN, ID_MTC_DESTINO, RESOLUCION, FREC_NE, FREC_FE, FREC, BW_MTC, PTX
            CAPACIDAD, ADDDATE)
        VALUES (:ID, :CODIGO_NE, :NOMBRE_NE, :CODIGO_FE, :NOMBRE_FE, :ALTURA_TORRE_NE, :ALTURA_PREDIO_NE,
            :ALTURA_MW_NE, :ALTURA_TORRE_FE, :ALTURA_PREDIO_FE, :ALTURA_MW_FE, :EQUIPO_NE, :EQUIPO_FE,
            :MARCA_IDU_ORIGEN, :MARCA_IDU_DESTINO, :ANTENA_NE, :ANTENA_FE, :DIAMETRO_NE, :DIAMETRO_FE,
            :GANANCIA_NE, :GANANCIA_FE, :ANTENA_VENDOR_ORIGEN, :ANTENA_VENDOR_DESTINO, :POLARIZACION,
            :CONFIGURACION, :AZIMUTH_NE, :AZIMUTH_FE, :FECHA_ULTIMO_CAMBIO, :FECHA_CREACION, :FECHA_APROBACION,
            :FECHA_BAJA, :RESP_ULTIMO_CAMBIO, :RESP_CREACION, :RESP_APROBACION, :RESP_BAJA, :PROYECTO, :ESTADO,
            :DISTANCIA, :ID_MTC_ORIGEN, :ID_MTC_DESTINO, :RESOLUCION, :FREC_NE, :FREC_FE, :FREC, :BW_MTC, :PTX,
            :CAPACIDAD, TRUNC(SYSDATE, 'DD'))"""
        bindings = {
            'ID': cx_Oracle.NUMBER,
            'CODIGO_NE': cx_Oracle.STRING,
            'NOMBRE_NE': cx_Oracle.STRING,
            'CODIGO_FE': cx_Oracle.STRING,
            'NOMBRE_FE': cx_Oracle.STRING,
            'ALTURA_TORRE_NE': cx_Oracle.NUMBER,
            'ALTURA_PREDIO_NE': cx_Oracle.NUMBER,
            'ALTURA_MW_NE': cx_Oracle.NUMBER,
            'ALTURA_TORRE_FE': cx_Oracle.NUMBER,
            'ALTURA_PREDIO_FE': cx_Oracle.NUMBER,
            'ALTURA_MW_FE': cx_Oracle.NUMBER,
            'EQUIPO_NE': cx_Oracle.STRING,
            'EQUIPO_FE': cx_Oracle.STRING,
            'MARCA_IDU_ORIGEN': cx_Oracle.STRING,
            'MARCA_IDU_DESTINO': cx_Oracle.STRING,
            'ANTENA_NE': cx_Oracle.STRING,
            'ANTENA_FE': cx_Oracle.STRING,
            'DIAMETRO_NE': cx_Oracle.NUMBER,
            'DIAMETRO_FE': cx_Oracle.NUMBER,
            'GANANCIA_NE': cx_Oracle.NUMBER,
            'GANANCIA_FE': cx_Oracle.NUMBER,
            'ANTENA_VENDOR_ORIGEN': cx_Oracle.STRING,
            'ANTENA_VENDOR_DESTINO': cx_Oracle.STRING,
            'POLARIZACION': cx_Oracle.STRING,
            'CONFIGURACION': cx_Oracle.STRING,
            'AZIMUTH_NE': cx_Oracle.NUMBER,
            'AZIMUTH_FE': cx_Oracle.NUMBER,
            'FECHA_ULTIMO_CAMBIO': cx_Oracle.STRING,
            'FECHA_CREACION': cx_Oracle.STRING,
            'FECHA_APROBACION': cx_Oracle.STRING,
            'FECHA_BAJA': cx_Oracle.STRING,
            'RESP_ULTIMO_CAMBIO': cx_Oracle.STRING,
            'RESP_CREACION': cx_Oracle.STRING,
            'RESP_APROBACION': cx_Oracle.STRING,
            'RESP_BAJA': cx_Oracle.STRING,
            'PROYECTO': cx_Oracle.STRING,
            'ESTADO': cx_Oracle.STRING,
            'DISTANCIA': cx_Oracle.NUMBER,
            'ID_MTC_ORIGEN': cx_Oracle.STRING,
            'ID_MTC_DESTINO': cx_Oracle.STRING,
            'RESOLUCION': cx_Oracle.STRING,
            'FREC_NE': cx_Oracle.STRING,
            'FREC_FE': cx_Oracle.STRING,
            'FREC': cx_Oracle.STRING,
            'BW_MTC': cx_Oracle.STRING,
            'PTX': cx_Oracle.STRING,
            'CAPACIDAD': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros)