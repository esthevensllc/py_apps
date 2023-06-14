import cx_Oracle

class PeersRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'M_ENLACES_INTERNACIONALES_TEMP_2'

    def insert_from_array(self, registros):
        template = f"INSERT INTO {self.table}(ID, IRU, ID_IRU, TIERONE, ID_TIERONE, ASN, PUERTO, BUNDEL, CAPACIDAD, ID_PROV_CABLE_SUBM, ID_NAME_CABLE_SUBM, ID_PAIS_DESTINO, ID_CIUDAD_DESTINO, ID_TIPO_IRU, ID_ROUTER, ID_ESTADO, FECHA_CREACION, FECHA_ACTIVACION, FECHA_BAJA, RESP_CREACION, RESP_ACTIVACION, RESP_BAJA, RESP_ULTIMO_CAMBIO, FECHA_ULTIMO_CAMBIO, ID_CAPA, TIPO_IRU, ROUTER, PAIS_DESTINO, CIUDAD_DESTINO, PROV_CABLE_SUBM, NAME_CABLE_SUBM, ESTADO, CAPA) VALUES (:ID, :IRU, :ID_IRU, :TIERONE, :ID_TIERONE, :ASN, :PUERTO, :BUNDEL, :CAPACIDAD, :ID_PROV_CABLE_SUBM, :ID_NAME_CABLE_SUBM, :ID_PAIS_DESTINO, :ID_CIUDAD_DESTINO, :ID_TIPO_IRU, :ID_ROUTER, :ID_ESTADO, TO_DATE(:FECHA_CREACION, 'YYYY-MM-DD HH24:MI:SS'), TO_DATE(:FECHA_ACTIVACION, 'YYYY-MM-DD HH24:MI:SS'), TO_DATE(:FECHA_BAJA, 'YYYY-MM-DD HH24:MI:SS'), :RESP_CREACION, :RESP_ACTIVACION, :RESP_BAJA, :RESP_ULTIMO_CAMBIO, TO_DATE(:FECHA_ULTIMO_CAMBIO, 'YYYY-MM-DD HH24:MI:SS'), :ID_CAPA, :TIPO_IRU, :ROUTER, :PAIS_DESTINO, :CIUDAD_DESTINO, :PROV_CABLE_SUBM, :NAME_CABLE_SUBM, :ESTADO, :CAPA)"
        bindings = {
            "ID": cx_Oracle.NUMBER,
            "IRU": cx_Oracle.STRING,
            "ID_IRU": cx_Oracle.STRING,
            "TIERONE": cx_Oracle.STRING,
            "ID_TIERONE": cx_Oracle.STRING,
            "ASN": cx_Oracle.STRING,
            "PUERTO": cx_Oracle.STRING,
            "BUNDEL": cx_Oracle.STRING,
            "CAPACIDAD": cx_Oracle.NUMBER,
            "ID_PROV_CABLE_SUBM": cx_Oracle.NUMBER,
            "ID_NAME_CABLE_SUBM": cx_Oracle.NUMBER,
            "ID_PAIS_DESTINO": cx_Oracle.NUMBER,
            "ID_CIUDAD_DESTINO": cx_Oracle.NUMBER,
            "ID_TIPO_IRU": cx_Oracle.NUMBER,
            "ID_ROUTER": cx_Oracle.NUMBER,
            "ID_ESTADO": cx_Oracle.NUMBER,
            "FECHA_CREACION": cx_Oracle.STRING,
            "FECHA_ACTIVACION": cx_Oracle.STRING,
            "FECHA_BAJA": cx_Oracle.STRING,
            "RESP_CREACION": cx_Oracle.STRING,
            "RESP_ACTIVACION": cx_Oracle.STRING,
            "RESP_BAJA": cx_Oracle.STRING,
            "RESP_ULTIMO_CAMBIO": cx_Oracle.STRING,
            "FECHA_ULTIMO_CAMBIO": cx_Oracle.STRING,
            "ID_CAPA": cx_Oracle.NUMBER,
            "TIPO_IRU": cx_Oracle.STRING,
            "ROUTER": cx_Oracle.STRING,
            "PAIS_DESTINO": cx_Oracle.STRING,
            "CIUDAD_DESTINO": cx_Oracle.STRING,
            "PROV_CABLE_SUBM": cx_Oracle.STRING,
            "NAME_CABLE_SUBM": cx_Oracle.STRING,
            "ESTADO": cx_Oracle.STRING,
            "CAPA": cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        registros = self.db.map_data_by_bindings(registros, bindings)
        self.db.save_from_array2(config, registros)

    def delete_all(self):
        self.db.query(f"truncate table {self.table}")

    def save_hist(self, result_time):
        str_result_time = result_time.strftime("%Y-%m-%d")
        self.db.query(f"""BEGIN
        DELETE FROM GMYD_ENLACES_INTERNACIONALES_HIST
        WHERE RESULT_TIME = TO_DATE('{str_result_time}', 'YYYY-MM-DD');
        COMMIT;

        INSERT INTO GMYD_ENLACES_INTERNACIONALES_HIST(
        RESULT_TIME,
        ID,IRU,ID_IRU,TIERONE,ID_TIERONE,ASN,PUERTO,BUNDEL,CAPACIDAD,ID_PROV_CABLE_SUBM,ID_NAME_CABLE_SUBM,
        ID_PAIS_DESTINO,ID_CIUDAD_DESTINO,ID_TIPO_IRU,ID_ROUTER,ID_ESTADO,FECHA_CREACION,FECHA_ACTIVACION,
        FECHA_BAJA,RESP_CREACION,RESP_ACTIVACION,RESP_BAJA,RESP_ULTIMO_CAMBIO,FECHA_ULTIMO_CAMBIO,ID_CAPA,
        TIPO_IRU,ROUTER,PAIS_DESTINO,CIUDAD_DESTINO,PROV_CABLE_SUBM,NAME_CABLE_SUBM,ESTADO,CAPA
        )
        SELECT TO_DATE('{str_result_time}', 'YYYY-MM-DD') RESULT_TIME,
        ID,IRU,ID_IRU,TIERONE,ID_TIERONE,ASN,PUERTO,BUNDEL,CAPACIDAD,ID_PROV_CABLE_SUBM,ID_NAME_CABLE_SUBM,
        ID_PAIS_DESTINO,ID_CIUDAD_DESTINO,ID_TIPO_IRU,ID_ROUTER,ID_ESTADO,FECHA_CREACION,FECHA_ACTIVACION,
        FECHA_BAJA,RESP_CREACION,RESP_ACTIVACION,RESP_BAJA,RESP_ULTIMO_CAMBIO,FECHA_ULTIMO_CAMBIO,ID_CAPA,
        TIPO_IRU,ROUTER,PAIS_DESTINO,CIUDAD_DESTINO,PROV_CABLE_SUBM,NAME_CABLE_SUBM,ESTADO,CAPA
        FROM {self.table};
        COMMIT;

        DELETE FROM M_ENLACES_INTERNACIONALES_HIST
        WHERE RESULT_TIME = TO_DATE('{str_result_time}', 'YYYY-MM-DD');
        COMMIT;
        
        INSERT INTO M_ENLACES_INTERNACIONALES_HIST(
        RESULT_TIME, ENLACE, RESOURCE_NAME, INTERFACE_DESCRIPTION, CIUDAD, ESTADO, ID
        )
        SELECT
            A.RESULT_TIME,
            A.TIERONE AS ENLACE,
            A.RESOURCE_NAME,
            B.INTERFACE_DESCRIPTION,
            a.CIUDAD_DESTINO AS CIUDAD,
            A.ESTADO AS ESTADO,
            A.ID
        FROM (
            SELECT
            CASE WHEN CAPACIDAD=100
            THEN router||'/100GE'||puerto
            ELSE router||'/GigabitEthernet'||puerto END AS RESOURCE_NAME,
            A.*
            FROM GMYD_ENLACES_INTERNACIONALES_HIST A
            WHERE A.RESULT_TIME = TO_DATE('{str_result_time}', 'YYYY-MM-DD')
        )A
        LEFT JOIN (
            SELECT * FROM TX_DESCRIPTION_100G_HIST WHERE RESULT_TIME = (SELECT MAX(RESULT_TIME) FROM TX_DESCRIPTION_100G_HIST)
        ) B ON B.RESOURCE_NAME = A.RESOURCE_NAME
        WHERE A.ESTADO = 'ACTIVO';
        COMMIT;
        END;""")

    def reload_licencias_isp(self):
        self.db.callproc("PK_PSEG_INSERTDB.SP_ADDDB031", {})