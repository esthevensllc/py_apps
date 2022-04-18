class ControlCargaRepository:
    def __init__(self, db):
        self.db = db
    
    def getOfProyectWhereFechaArchivo(self, proyect, fecha1, fecha2):
        sql = """select
        id, FECHA_CREACION, PROYECTO, ARCHIVO, REGISTROS_CARGADOS, REGISTROS_TOTALES, INICIO, FIN, ESTADO, MENSAJE, FECHA_ARCHIVO
        from PADM_CARGA_CONTROL WHERE PROYECTO='{}' AND FECHA_ARCHIVO >= TO_DATE('{}', 'YYYYMMDDHH24MI') and FECHA_ARCHIVO < TO_DATE('{}', 'YYYYMMDDHH24MI')""".format(proyect, fecha1.strftime('%Y%m%d%H%M'), fecha2.strftime('%Y%m%d%H%M'))

        result = self.db.fetch(sql)
        new_result = []
        for index in range(len(result)):
            row = result[index]
            archivo = row[3]
            archivo_updated = None
            if row[3] is not None:
                if '|' in row[3]:
                    archivo = row[3].split('|')[1]
                    archivo_updated = row[3].split('|')[0]
            new_result.append({'id': row[0], 'fecha_creacion': row[1], 'proyecto': row[2], 'archivo': archivo, 'archivo_updated': archivo_updated, 'registros_cargados': row[4], 'registros_totales': row[5], 'inicio': row[6], 'fin': row[7], 'estado': row[8], 'mensaje': row[9], 'fecha_archivo': row[10]})
        return new_result

    def save_carga(self, proyect, archivo, registros_cargados, registros_totales, fec_ini, fec_fin, estado, mensaje, fecha_archivo):
        # sql = "BEGIN PK_GTF.SP_INSERTAR_EVENTO_CARGA_CSV('{}', '{}', '{}', '{}',  '{}', '{}', '{}', '{}', '{}'); END;".format(proyect, archivo, registros_cargados, registros_totales, fec_ini, fec_fin, estado, mensaje, fecha_archivo)
        # print([proyect, archivo, registros_cargados, registros_totales, fec_ini, fec_fin, estado, mensaje, fecha_archivo])
        sql = """
        declare
            v_count_find number := 0;
            V_PROYECTO varchar2(200) := :1;
            V_ARCHIVO varchar2(200) := :2;
            V_REGISTROS_CARGADOS NUMBER := :3;
            V_REGISTROS_TOTALES NUMBER := :4;
            V_FEC_INI DATE := TO_DATE(:5, 'YYYY-MM-DD HH24:MI:SS');
            V_FEC_FIN DATE := TO_DATE(:6, 'YYYY-MM-DD HH24:MI:SS');
            V_ESTADO VARCHAR2(100) := :7;
            V_MESSAGE VARCHAR2(100) := :8;
            V_FECHA_ARCHIVO DATE := TO_DATE(:9, 'YYYY-MM-DD HH24:MI:SS');
        begin
            select count(*) into v_count_find from PADM_CARGA_CONTROL
            WHERE PROYECTO = V_PROYECTO AND FECHA_ARCHIVO = V_FECHA_ARCHIVO;
            
            IF v_count_find > 0 THEN
                UPDATE PADM_CARGA_CONTROL SET
                    ARCHIVO = V_ARCHIVO,
                    REGISTROS_CARGADOS = V_REGISTROS_CARGADOS,
                    REGISTROS_TOTALES = V_REGISTROS_TOTALES,
                    INICIO = V_FEC_INI,
                    FIN = V_FEC_FIN,
                    ESTADO = V_ESTADO,
                    MENSAJE = V_MESSAGE
                WHERE PROYECTO = V_PROYECTO AND FECHA_ARCHIVO = V_FECHA_ARCHIVO;
                COMMIT;
            ELSE
                PK_GTF.SP_INSERTAR_EVENTO_CARGA_CSV(
                    V_PROYECTO,
                    V_ARCHIVO,
                    TO_CHAR(V_REGISTROS_CARGADOS),
                    TO_CHAR(V_REGISTROS_TOTALES),
                    TO_CHAR(V_FEC_INI,'YYYY-MM-DD HH24:MI:SS'),
                    TO_CHAR(V_FEC_FIN,'YYYY-MM-DD HH24:MI:SS'),
                    V_ESTADO,
                    V_MESSAGE,
                    TO_CHAR(V_FECHA_ARCHIVO,'YYYY-MM-DD HH24:MI')
                );
            END IF;
        end;""".format(proyect, archivo, registros_cargados, registros_totales, fec_ini.strftime('%Y-%m-%d %H:%M:%S'), fec_fin.strftime('%Y-%m-%d %H:%M:%S'), estado, mensaje, fecha_archivo.strftime('%Y-%m-%d %H:%M:%S'))
        # print(sql)
        # self.db.query(sql)
        data = [proyect, archivo, registros_cargados, registros_totales, fec_ini.strftime('%Y-%m-%d %H:%M:%S'), fec_fin.strftime('%Y-%m-%d %H:%M:%S'), estado, mensaje, fecha_archivo.strftime('%Y-%m-%d %H:%M:%S')]
        self.db.save(sql, data, 'array')