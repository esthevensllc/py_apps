import cx_Oracle

class PeersRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'M_ENLACES_INTERNACIONALES_TEMP_2'

    def insert_from_array(self, registros):
        template = f"""INSERT INTO {self.table}(IRU, TIERONE, PUERTO, BUNDEL, CAPACIDAD, TIPO_IRU, ROUTER, PAIS_DESTINO, CIUDAD_DESTINO,
        PROV_CABLE_SUBM, NAME_CABLE_SUBM, ESTADO, CAPA, FECHA_CREACION, FECHA_ACTIVACION,
        FECHA_ULTIMO_CAMBIO, FECHA_BAJA, RESP_CREACION, RESP_ACTIVACION, RESP_ULTIMO_CAMBIO, RESP_BAJA
        ) VALUES (:IRU, :TIERONE, :PUERTO, :BUNDEL, :CAPACIDAD, :TIPO_IRU, :ROUTER, :PAIS_DESTINO, :CIUDAD_DESTINO,
        :PROV_CABLE_SUBM, :NAME_CABLE_SUBM, :ESTADO, :CAPA, TO_DATE(:FECHA_CREACION,'YYYY-MM-DD HH24:MI:SS'), TO_DATE(:FECHA_ACTIVACION, 'YYYY-MM-DD HH24:MI:SS'),
        TO_DATE(:FECHA_ULTIMO_CAMBIO, 'YYYY-MM-DD HH24:MI:SS'), TO_DATE(:FECHA_BAJA, 'YYYY-MM-DD HH24:MI:SS'), :RESP_CREACION, :RESP_ACTIVACION, :RESP_ULTIMO_CAMBIO, :RESP_BAJA)"""
        bindings = {
            "IRU": cx_Oracle.STRING,
            "TIERONE": cx_Oracle.STRING,
            "PUERTO": cx_Oracle.STRING,
            "BUNDEL": cx_Oracle.STRING,
            "CAPACIDAD": cx_Oracle.NUMBER,
            "TIPO_IRU": cx_Oracle.STRING,
            "ROUTER": cx_Oracle.STRING,
            "PAIS_DESTINO": cx_Oracle.STRING,
            "CIUDAD_DESTINO": cx_Oracle.STRING,
            "PROV_CABLE_SUBM": cx_Oracle.STRING,
            "NAME_CABLE_SUBM": cx_Oracle.STRING,
            "ESTADO": cx_Oracle.STRING,
            "CAPA": cx_Oracle.STRING,
            "FECHA_CREACION": cx_Oracle.STRING,
            "FECHA_ACTIVACION": cx_Oracle.STRING,
            "FECHA_ULTIMO_CAMBIO": cx_Oracle.STRING,
            "FECHA_BAJA": cx_Oracle.STRING,
            "RESP_CREACION": cx_Oracle.STRING,
            "RESP_ACTIVACION": cx_Oracle.STRING,
            "RESP_ULTIMO_CAMBIO": cx_Oracle.STRING,
            "RESP_BAJA": cx_Oracle.STRING,
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        registros = self.db.map_data_by_bindings(registros, bindings)
        self.db.save_from_array2(config, registros)

    def delete_all(self):
        self.db.query(f"truncate table {self.table}")

    def save_hist(self, result_time):
        str_result_time = result_time.strftime("%Y-%m-%d")
        self.db.query(f"""BEGIN
            PK_GMYD_CARGA.SP_ENLACES_INTERNACIONALES_HIST(TO_DATE('{str_result_time}', 'YYYY-MM-DD'));
        END;""")

    def reload_licencias_isp(self):
        self.db.callproc("PK_PSEG_INSERTDB.SP_ADDDB031", {})