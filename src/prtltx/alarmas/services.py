import datetime as dt
import calendar

class LoadPrtltxAlarmas:
    def __init__(self, repository, mysql):
        self.repository = repository
        self.mysql = mysql
    
    def execute(self, str_fecha1=None, str_fecha2=None):
        fecha = (dt.datetime.now() - dt.timedelta(days=1))
        fecha1, fecha2  = self._get_range_from_date(fecha)
        if str_fecha1 is not None and str_fecha2 is not None:
            fecha1 = dt.datetime.strptime(str_fecha1, '%Y-%m-%d')
            fecha2 = dt.datetime.strptime(str_fecha2, '%Y-%m-%d')

        print("prtltx alarmas")
        self._make_load(fecha1, fecha2)

    def _get_range_from_date(self, fecha):
        str_fecha1 = fecha.strftime('%Y-%m')+"-01"
        days_of_month = calendar.monthrange(int(fecha.strftime('%Y')), int(fecha.strftime('%m')))[1]
        fecha1 = dt.datetime.strptime(str_fecha1, '%Y-%m-%d')
        fecha2 = fecha1 + dt.timedelta(days=days_of_month)
        return fecha1, fecha2

    def _make_load(self, fecha1, fecha2):
        print(f"{fecha1} - {fecha2}")
        registros = self._get_alarmas(fecha1, fecha2)
        for row in registros:
            row['fecha_ini'] = row['fecha_ini'].strftime('%Y-%m-%d %H:%M:%S') if row['fecha_ini'] is not None else None
            row['fecha_fin'] = row['fecha_fin'].strftime('%Y-%m-%d %H:%M:%S') if row['fecha_fin'] is not None else None

        if len(registros) != 0:
            self.repository.delete_where_between(fecha1, fecha2)
            self.repository.insert_from_array(registros)
            params = {'p_fecini': fecha1.strftime('%Y-%m-%d'), 'p_fecfin': fecha2.strftime('%Y-%m-%d')}
            self.repository.callproc("PK_PRTLTX_ALARMA.SP_MAIN_LOAD_ALARMAS(TO_DATE(:p_fecini, 'YYYY-MM-DD'), TO_DATE(:p_fecfin, 'YYYY-MM-DD'))", params)
        
        print(len(registros))

    def _get_alarmas(self, fecha1, fecha2):
        fields = ['idlog_serial', 'nombre_red', 'codigo_red', 'codigo_alarma', 'nombre_alarma', 'tipo_alarma', 'estado_actual', 'severidad_alarma', 'fecha_ini', 'fecha_fin', 'detalle_alar', 'causas']

        str_fecha1 = fecha1.strftime('%d/%m/%Y')
        str_fecha2 = fecha2.strftime('%d/%m/%Y')

        registros = self.mysql.fetch_as_df(f"""SELECT
        IDLOG_SERIAL, NOMBRE_RED, CODIGO_RED, CODIGO_ALARMA, NOMBRE_ALARMA, TIPO_ALARMA, ESTADO_ACTUAL,
        SEVERIDAD_ALARMA,
        #DATE_FORMAT(FECHA_INI, '%Y-%m-%d %H:%i:%s') as FECHA_INI,
        FECHA_INI,
        #DATE_FORMAT(FECHA_FIN, '%Y-%m-%d %H:%i:%s') as FECHA_FIN,
        FECHA_FIN,
        DETALLE_ALAR, CAUSAS
        FROM (
            SELECT
            IDLOG_SERIAL, NOMBRE_RED, CODIGO_RED, CODIGO_ALARMA, NOMBRE_ALARMA, TIPO_ALARMA, ESTADO_ACTUAL,
            SEVERIDAD_ALARMA, STR_TO_DATE(REPLACE(FECHA_INICALARMA, '.', ''),'%d/%m/%Y %h:%i:%s %p') as FECHA_INI,
            STR_TO_DATE(REPLACE(FECHA_FINALARMA, '.', ''),'%d/%m/%Y %h:%i:%s %p') as FECHA_FIN,
            DETALLE_ALAR, CAUSAS
            from PRTLTX_ALARMA
        ) a where STR_TO_DATE('{str_fecha1}','%d/%m/%Y') <= FECHA_INI and FECHA_INI < STR_TO_DATE('{str_fecha2}','%d/%m/%Y')""", fields)
        return registros