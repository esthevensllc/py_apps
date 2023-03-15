import cx_Oracle

class PrtltxAlarmasRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'PRTLTX_ALARMAS_MYSQL'

    def delete_where_between(self, fecha1, fecha2):
        fecha1_str = fecha1.strftime('%Y%m%d%H%M%S')
        fecha2_str = fecha2.strftime('%Y%m%d%H%M%S')
        date_field = 'FECHA_INICALARMA'
        sql = f"DELETE FROM {self.table} WHERE {date_field}>=TO_DATE('{fecha1_str}', 'YYYYMMDDHH24MISS') and {date_field}<=TO_DATE('{fecha2_str}', 'YYYYMMDDHH24MISS')"
        self.db.query(sql)
    
    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(IDLOG_SERIAL,NOMBRE_RED,CODIGO_RED,CODIGO_ALARMA,NOMBRE_ALARMA,TIPO_ALARMA,ESTADO_ACTUAL,SEVERIDAD_ALARMA,FECHA_INICALARMA,FECHA_FINALARMA,DETALLE_ALAR,CAUSAS) VALUES (:idlog_serial, :nombre_red, :codigo_red, :codigo_alarma, :nombre_alarma, :tipo_alarma, :estado_actual, :severidad_alarma, to_date(:fecha_ini, 'yyyy-mm-dd hh24:mi:ss'), to_date(:fecha_fin, 'yyyy-mm-dd hh24:mi:ss'), :detalle_alar, :causas)"
        bindings = {
            'idlog_serial': cx_Oracle.NUMBER,
            'nombre_red': cx_Oracle.STRING,
            'codigo_red': cx_Oracle.STRING,
            'codigo_alarma': cx_Oracle.STRING,
            'nombre_alarma': cx_Oracle.STRING,
            'tipo_alarma': cx_Oracle.STRING,
            'estado_actual': cx_Oracle.STRING,
            'severidad_alarma': cx_Oracle.STRING,
            'fecha_ini': cx_Oracle.STRING,
            'fecha_fin': cx_Oracle.STRING,
            'detalle_alar': cx_Oracle.STRING,
            'causas': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings.copy(), 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)

    def callproc(self, procedure, params):
        self.db.callproc(procedure, params)
