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
        A.ENLACE,
        A.RESOURCE_NAME,
        B.INTERFACE_DESCRIPTION,
        A.CIUDAD,
        A.ESTADO,
        A.ID
        FROM (
            SELECT DISTINCT
            A.RESULT_TIME,
            A.TIERONE AS ENLACE,
            CASE
            WHEN N.RESOURCENAME IS NOT NULL AND M.RESOURCENAME IS NOT NULL THEN M.RESOURCENAME
            WHEN N.RESOURCENAME IS NULL AND M.RESOURCENAME IS NOT NULL THEN M.RESOURCENAME
            WHEN N.RESOURCENAME IS NOT NULL AND M.RESOURCENAME IS NULL THEN N.RESOURCENAME
            ELSE M.RESOURCENAME END RESOURCE_NAME,
            A.CIUDAD_DESTINO AS CIUDAD,
            A.ESTADO AS ESTADO,
            A.ID
            FROM  
            (
                SELECT
                REGEXP_SUBSTR(PUERTO,'\d+\/\d+\/\d+\.{{0,1}}\d*',1,1) PUERTO2,X.*
                FROM GMYD_ENLACES_INTERNACIONALES_HIST X
                WHERE X.RESULT_TIME = TO_DATE('{str_result_time}', 'YYYY-MM-DD')
                AND X.ESTADO = 'ACTIVO'
            ) A
            LEFT JOIN    
            (SELECT * FROM TX_MAESTRO_INTRFCS_DIARIO WHERE COLLECTIONTIME=(SELECT MAX(COLLECTIONTIME) FROM TX_MAESTRO_INTRFCS_DIARIO)) M
            ON A.ROUTER=M.DEVICENAME AND A.PUERTO2=M.PUERTO
            LEFT JOIN
            (SELECT * FROM TX_MAESTRO_INTRFCS_DIARIO WHERE COLLECTIONTIME=(SELECT MAX(COLLECTIONTIME) FROM TX_MAESTRO_INTRFCS_DIARIO)) N
            ON A.ROUTER=N.DEVICENAME AND A.BUNDEL=N.PUERTO
            WHERE NOT REGEXP_LIKE(M.RESOURCENAME,'Cellular|HP-GE|LoopBack|MEth|MTunnel|NULL|ServiceIf|Sip|Stack-Port|Tunnel|Vbdif|VBridge|Virtual-Ethernet|Virtual-Template|Vlanif|Wlan-Bss|XGigabitEthernet')
        )A
        LEFT JOIN TX_NUEVO_MAETRO2 B ON B.RESOURCE_NAME = A.RESOURCE_NAME;
        COMMIT;
        END;""")

    def reload_licencias_isp(self):
        self.db.callproc("PK_PSEG_INSERTDB.SP_ADDDB031", {})