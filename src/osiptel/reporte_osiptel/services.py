import csv
import datetime as dt
from src.shared.config import STORAGE_DIR

class GenerarReporteOsiptelCsv:
    def __init__(self, db):
        self.db = db
        self.config = {}
        
        # smart.PK_PRG_OSIPTEL_PROCESOS.SP_OSIPTEL_TH_4G
        self.config['4G_F1'] = {
            'query': """
            select
                to_char(RESULT_TIME,'dd/mm/yyyy hh24') AS FECHA_HORA,
                DEPARTAMENTO,
                'HUAWEI' AS PROVEEDOR,
                '4G' AS TECNOLOGIA,
                SITE_NAME AS CODIGO_EB, -- DUDA
                SITE_ADDRESS AS NOMBRE_EB, --DUDA
                CELLNAME AS CELL_ID,
                CASE WHEN SUM(a.ave_dl_user_thrp_kbps_f3_den)>0 THEN SUM(ave_dl_user_thrp_kbps_f3_num)/SUM(ave_dl_user_thrp_kbps_f3_den)/1000 END AS TR_DL_AV_USER,
                CASE WHEN SUM(a.ave_Ul_user_thrp_kbps_f3_den)>0 THEN SUM(ave_Ul_user_thrp_kbps_f3_num)/SUM(ave_Ul_user_thrp_kbps_f3_den)/1000 END AS TR_UL_AV_USER,
                SUM(A.DL_TRAFFIC_VOL_MB) AS TOTAL_TRAF_DL,
                SUM(A.UL_TRAFFIC_VOL_MB) AS TOTAL_TRAF_UL,
                MAX(LATITUD) AS LATITUD,
                MAX(LONGITUD) AS LONGITUD
            from INDI_KPI_HXH_4G_CELL A 
            INNER JOIN maestro_4g_huawei_nm B 
            ON A.ID_CELDA = B.ID_CELDA
            WHERE RESULT_TIME >= to_date('{str_fecha1}', 'yyyy-mm-dd') AND 
                RESULT_TIME < to_date('{str_fecha2}', 'yyyy-mm-dd') --AND IND_IRRADIANDO = 1
            GROUP BY RESULT_TIME,
                DEPARTAMENTO,
                SITE_NAME, -- DUDA
                SITE_ADDRESS,
                CELLNAME
            """,
            'headers': ['FECHA_HORA','DEPARTAMENTO','PROVEEDOR','TECNOLOGIA','CODIGO EB','NOMBRE EB','CELL_ID','TR_DL_AV_USER','TR_UL_AV_USER','TOTAL_TRAF_DL','TOTAL_TRAF_UL','LATITUD','LONGITUD'],
            'csv_name': "4G_FORMATO_1_{str_trimestre}_{year}.csv"
        }
        # smart.PK_PRG_OSIPTEL_PROCESOS.SP_OSIPTEL_USO_4G
        self.config['4G_F2'] = {
            'query': """
            select 
                ubigeo_inei as UBIGEO,
                to_char(RESULT_TIME,'dd/mm/yyyy hh24') AS FECHA_HORA,
                'HUAWEI' AS PROVEEDOR,
                '4G' AS TECNOLOGIA,
                SITE_ADDRESS AS NOMBRE_EB, --DUDA
                SITE_NAME AS CODIGO_EB, -- DUDA
                CELLNAME AS CELL_ID,
                CASE WHEN SUM(A.AVG_DL_PRB_USAGE_DEN) >0 THEN SUM(A.AVG_DL_PRB_USAGE_NUM)/SUM(A.AVG_DL_PRB_USAGE_DEN) END * 100 AS UTILIZACION_MAX_DL,
                CASE WHEN SUM(A.AVG_uL_PRB_USAGE_DEN) >0 THEN SUM(A.AVG_UL_PRB_USAGE_NUM)/SUM(A.AVG_UL_PRB_USAGE_DEN) END * 100 AS UTILIZACION_MAX_UL,
                MAX(LATITUD) AS LATITUD,
                MAX(LONGITUD) AS LONGITUD
            from INDI_KPI_HXH_4G_CELL A 
            INNER JOIN maestro_4g_huawei_nm B 
            ON A.ID_CELDA = B.ID_CELDA
            WHERE RESULT_TIME >= to_date('{str_fecha1}', 'yyyy-mm-dd') AND 
                RESULT_TIME < to_date('{str_fecha2}', 'yyyy-mm-dd') --AND IND_IRRADIANDO = 1
            GROUP BY 
                ubigeo_inei,
                RESULT_TIME,
                DEPARTAMENTO,
                SITE_NAME,
                SITE_ADDRESS,
                CELLNAME
            """,
            'headers': ['UBIGEO','FECHA_HORA','PROVEEDOR','TECNOLOGIA','NOMBRE EB','CODIGO EB','CELLID','UTILIZACION_MAX_DL','UTILIZACION_MAX_UL','LATITUD','LONGITUD'],
            'csv_name': "4G_FORMATO_2_{str_trimestre}_{year}.csv"
        }
        # smart.PK_PRG_OSIPTEL_PROCESOS.SP_OSIPTEL_TH_3G
        self.config['3G_F1'] = {
            'query': """
            select
            to_char(RESULT_TIME,'dd/mm/yyyy hh24') AS FECHA_HORA,
            DEPARTAMENTO,
            'HUAWEI' AS PROVEEDOR,
            '3G' AS TECNOLOGIA,
            SITE_NAME AS CODIGO_EB, -- DUDA
            SITE_ADDRESS AS NOMBRE_EB, --DUDA
            CELLNAME AS CELL_ID,
            avg(throughput_hsdpa_kbps)/1000 AS TR_DL_AV_USER,
            avg(throughput_hsupa_kbps)/1000 AS TR_UL_AV_USER,
            sum((nvl(TOTAL_KBYTES_PS_DL,0) + nvl(TOTAL_KBYTES_HSDPA,0))/1024) AS TOTAL_TRAF_DL,
            sum((nvl(TOTAL_KBYTES_PS_UL,0) + nvl(TOTAL_KBYTES_HSUPA,0))/1024) AS TOTAL_TRAF_UL,
            MAX(LATITUD) AS LATITUD,
            MAX(LONGITUD) AS LONGITUD
            from INDI_KPI_HXH_3G_CELL A 
            INNER JOIN maestro_3g_huawei_nm B 
            ON A.ID_CELDA = B.ID_CELDA
            WHERE RESULT_TIME >= to_date('{str_fecha1}', 'yyyy-mm-dd') AND
            RESULT_TIME < to_date('{str_fecha2}', 'yyyy-mm-dd')
            GROUP BY RESULT_TIME,
            DEPARTAMENTO,
            SITE_NAME, -- DUDA
            SITE_ADDRESS,
            CELLNAME
            """,
            'headers': ['FECHA_HORA','DEPARTAMENTO','PROVEEDOR','TECNOLOGIA','CODIGO EB','NOMBRE EB','CELL_ID','TR_DL_AV_USER','TR_UL_AV_USER','TOTAL_TRAF_DL','TOTAL_TRAF_UL','LATITUD','LONGITUD'],
            'csv_name': "3G_FORMATO_1_{str_trimestre}_{year}.csv"
        }
        # smart.PK_PRG_OSIPTEL_PROCESOS.SP_OSIPTEL_USO_3G
        self.config['3G_F2'] = {
            'query': """
            select 
                ubigeo_inei as UBIGEO,
                to_char(RESULT_TIME,'dd/mm/yyyy hh24') AS FECHA_HORA,
                'HUAWEI' AS PROVEEDOR,
                '3G' AS TECNOLOGIA,
                SITE_ADDRESS AS NOMBRE_EB, --DUDA
                SITE_NAME AS CODIGO_EB, -- DUDA
                CELLNAME AS CELL_ID,
                CASE WHEN SUM(A.Ce_Dl_capacidad) >0 THEN SUM(A.Ce_Dl_Avg)/SUM(A.Ce_Dl_capacidad) END * 100 AS UTILIZACION_MAX_DL,
                CASE WHEN SUM(A.Ce_Ul_capacidad) >0 THEN SUM(A.Ce_Ul_Avg)/SUM(A.Ce_Dl_capacidad) END * 100 AS UTILIZACION_MAX_UL,
                MAX(LATITUD) AS LATITUD,
                MAX(LONGITUD) AS LONGITUD
            from INDI_KPI_HXH_3G_CELL A 
            INNER JOIN maestro_3g_huawei_nm B 
            ON A.ID_CELDA = B.ID_CELDA
            WHERE RESULT_TIME >= to_date('{str_fecha1}', 'yyyy-mm-dd') AND 
                RESULT_TIME < to_date('{str_fecha2}', 'yyyy-mm-dd') --AND IND_IRRADIANDO = 1
            GROUP BY 
                ubigeo_inei,
                RESULT_TIME,
                DEPARTAMENTO,
                SITE_NAME, 
                SITE_ADDRESS,
                CELLNAME
            """,
            'headers': ['UBIGEO','FECHA_HORA','PROVEEDOR','TECNOLOGIA','NOMBRE EB','CODIGO EB','CELL_ID','UTILIZACION_MAX_DL','UTILIZACION_MAX_UL','LATITUD','LONGITUD'],
            'csv_name': "3G_FORMATO_2_{str_trimestre}_{year}.csv"
        }

        self.config['5G_F1'] = {
            'query': """
            select 
            to_char(RESULT_TIME,'dd/mm/yyyy hh24') AS FECHA_HORA,
            DEPARTAMENTO,
            'HUAWEI' AS PROVEEDOR,
            '5G' AS TECNOLOGIA,
            SITE_NAME AS CODIGO_EB, -- DUDA
            SITE_ADDRESS AS NOMBRE_EB, --DUDA
            CELLNAME AS CELL_ID,
            CASE WHEN SUM(TH_USER_DL_KB_DEN)>0 THEN SUM(TH_USER_DL_KB_NUM)/SUM(TH_USER_DL_KB_DEN) END*1000 AS TR_DL_AV_USER,
            CASE WHEN SUM(TH_USER_UL_KB_DEN)>0 THEN SUM(TH_USER_UL_KB_NUM)/SUM(TH_USER_UL_KB_DEN) END*1000 AS TR_UL_AV_USER,  
            SUM(TRAFICO_DL_GB)*1024 AS TOTAL_TRAF_DL,
            SUM(trafico_ul_gb)*1024 AS TOTAL_TRAF_UL,
            MAX(LATITUD) AS LATITUD,
            MAX(LONGITUD) AS LONGITUD
            from INDICADORES_HXH_5G_CELL A 
            INNER JOIN MAESTRO_5G_HUAWEI B 
            ON A.ID_CELDA = B.ID_CELDA
            WHERE RESULT_TIME >= to_date('{str_fecha1}', 'yyyy-mm-dd') AND 
            RESULT_TIME < to_date('{str_fecha2}', 'yyyy-mm-dd') --AND IND_IRRADIANDO = 1
            GROUP BY RESULT_TIME,
            DEPARTAMENTO,
            SITE_NAME, -- DUDA
            SITE_ADDRESS,
            CELLNAME
            """,
            'headers': ['FECHA_HORA','DEPARTAMENTO','PROVEEDOR','TECNOLOGIA','CODIGO EB','NOMBRE EB','CELL_ID','TR_DL_AV_USER','TR_UL_AV_USER','TOTAL_TRAF_DL','TOTAL_TRAF_UL','LATITUD','LONGITUD'],
            'csv_name': "5G_FORMATO_1_{str_trimestre}_{year}.csv"
        }

        self.config['5G_F2'] = {
            'query': """
            select
            ubigeo_inei as UBIGEO,
            to_char(RESULT_TIME,'dd/mm/yyyy hh24') AS FECHA_HORA,
            'HUAWEI' AS PROVEEDOR,
            '5G' AS TECNOLOGIA,
            SITE_ADDRESS AS NOMBRE_EB, --DUDA
            SITE_NAME AS CODIGO_EB, -- DUDA
            CELLNAME AS CELL_ID,
            CASE WHEN SUM(A.RES_BLOCK_UTIL_DL_DEN) >0 THEN SUM(A.RES_BLOCK_UTIL_DL_NUM)/SUM(A.RES_BLOCK_UTIL_DL_DEN) END * 100 AS UTILIZACION_MAX_DL,
            CASE WHEN SUM(A.RES_BLOCK_UTIL_UL_DEN) >0 THEN SUM(A.RES_BLOCK_UTIL_UL_NUM)/SUM(A.RES_BLOCK_UTIL_UL_DEN) END * 100 AS UTILIZACION_MAX_UL,
            MAX(LATITUD) AS LATITUD,
            MAX(LONGITUD) AS LONGITUD
            from INDICADORES_HXH_5G_CELL A 
            INNER JOIN MAESTRO_5G_HUAWEI B 
            ON A.ID_CELDA = B.ID_CELDA
            WHERE RESULT_TIME >= to_date('{str_fecha1}', 'yyyy-mm-dd') AND 
            RESULT_TIME < to_date('{str_fecha2}', 'yyyy-mm-dd') --AND IND_IRRADIANDO = 1
            GROUP BY 
            ubigeo_inei,
            RESULT_TIME,
            DEPARTAMENTO,
            SITE_NAME, 
            SITE_ADDRESS,
            CELLNAME
            """,
            'headers': ['UBIGEO','FECHA_HORA','PROVEEDOR','TECNOLOGIA','NOMBRE EB','CODIGO DE ENODEB','CELL_ID','UTILIZACION_MAX_DL','UTILIZACION_MAX_UL','LATITUD','LONGITUD'],
            'csv_name': "5G_FORMATO_2_{str_trimestre}_{year}.csv"
        }

        self.trimestre_config = {
            '1T': {'fecha1': '01-01', 'fecha2': '04-01', 'label': 'TRIMESTRE_1'},
            '2T': {'fecha1': '04-01', 'fecha2': '07-01', 'label': 'TRIMESTRE_2'},
            '3T': {'fecha1': '07-01', 'fecha2': '10-01', 'label': 'TRIMESTRE_3'},
            '4T': {'fecha1': '10-01', 'fecha2': '01-01', 'label': 'TRIMESTRE_4'},
        }

    def execute(self, year=2023, tecnologia='4G', trimestre='4T', format='2'):
        # year = dt.datetime.now().strftime("%Y")
        # year = 2023
        trim = self.trimestre_config[trimestre]
        trim['fecha1'] = f"{year}-{trim['fecha1']}"
        if trimestre == "4T":
            trim['fecha2'] = f"{year+1}-{trim['fecha2']}"
        else:
            trim['fecha2'] = f"{year}-{trim['fecha2']}"

        fecha_ini = dt.datetime.strptime(trim['fecha1'], '%Y-%m-%d')
        fecha_fin = dt.datetime.strptime(trim['fecha2'], '%Y-%m-%d')

        config = self.config[f'{tecnologia}_F{format}']
        csv_name = config['csv_name'].format(str_trimestre=trim['label'], year=year)
        headers = [config['headers']]
        query = config['query']

        print(f"{fecha_ini} - {fecha_fin} => {csv_name}")

        with open(f"D:/pronatel-reportes/{csv_name}", 'w', encoding="utf-8",  newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(headers)
            
            fecha_recorrido = fecha_ini
            while fecha_recorrido < fecha_fin:
                next_fecha = fecha_recorrido + dt.timedelta(days=1)

                result = self.__get_data(query, fecha_recorrido, next_fecha)
                writer.writerows(result)
                print(f"{fecha_recorrido} - {next_fecha}: {len(result)}")
                fecha_recorrido = next_fecha
            
        print("Writing complete")

    def __get_data(self, query, fecha1, fecha2):
        str_fecha1 = fecha1.strftime('%Y-%m-%d')
        str_fecha2 = fecha2.strftime('%Y-%m-%d')
        sql = query.format(str_fecha1=str_fecha1, str_fecha2=str_fecha2)

        #FETCH FIRST '1' ROWS ONLY
        result = self.db.fetch(sql)
        _range = range(len(result))
        for i in _range:
            result[i] = list(result[i])
        return result
