import datetime as dt
import cx_Oracle

class LoadResumenDelay:
    def __init__(self, oracle, sqlserver):
        self.oracle = oracle
        self.sqlserver = sqlserver
        self.table = "TX_RESUMEN_DELAY_GMD"

    def execute(self, fecha=dt.datetime.now().strftime('%Y-%m-%d')):
        data = self.get_data(fecha)
        print(f"load_resumen_delay {len(data)}")
        print(f"Fecha recarga oracle: {fecha}")
        self.reload_table(fecha, data)

    def get_data(self, fecha: str):
        fields = ["fecha_fc", "proyecto", "area_responsable", "site", "region", "node_name", "pap"]
        query = "select [FECHA FC], PROYECTO, [AREA RESPONSABLE], SITE, REGION, NODE_NAME, PAP from dbo.resumen_delay$"
        data = self.sqlserver.fetch_as_df(query, fields)
        # str_date = dt.datetime.strptime(fecha, '%Y-%m-%d')
        for index in range(len(data)):
            data[index]['result_time'] = fecha
        return data

    def reload_table(self, fecha: str, data: list):
        query = f"DELETE FROM {self.table} WHERE result_time = TO_DATE(:result_time, 'YYYY-MM-DD')"
        self.oracle.query(query, {"result_time": fecha})
        
        template = f"""INSERT INTO {self.table}(result_time, fecha_fc, proyecto, area_responsable, site, region, node_name, pap)
        VALUES (to_date(:result_time, 'yyyy-mm-dd'), :fecha_fc, :proyecto, :area_responsable, :site, :region, :node_name, :pap)"""
        bindings = {
            'result_time': cx_Oracle.STRING,
            'fecha_fc': cx_Oracle.STRING,
            'proyecto': cx_Oracle.STRING,
            'area_responsable': cx_Oracle.STRING,
            'site': cx_Oracle.STRING,
            'region': cx_Oracle.STRING,
            'node_name': cx_Oracle.STRING,
            'pap': cx_Oracle.STRING
        }
        
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 5000}
        self.oracle.save_from_array2(config, data)
