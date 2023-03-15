import datetime as dt
import re

class LoadOracleHandlers:
    def __init__(self, db):
        self.db = db

    def execute(self):
        cargas = self.__get_last_cargas()
        counter = 1
        for row in cargas:
            handlers = self.__get_ora_handlers_by_proyecto(row['proyecto'])
            p_farchivo_hxh = row['fecha']
            p_farchivo_fin_hxh = row['fecha'] + dt.timedelta(hours=1)
            def_params = {
                'p_farchivo_hxh': p_farchivo_hxh.strftime('%Y-%m-%d %H:%M:%S'),
                'p_farchivo_fin_hxh': p_farchivo_fin_hxh.strftime('%Y-%m-%d %H:%M:%S'),
                'p_farchivo_hxh_f1': p_farchivo_hxh.strftime('%d/%m/%Y %H'),
                'p_farchivo_fin_hxh_f1': p_farchivo_fin_hxh.strftime('%d/%m/%Y %H')
            }
            print(row['proyecto'])
            for h in handlers:
                handler, params = self.__get_params_to_handler(h['handler'], def_params)
                print(f"[{h['norder']}] {handler}: {params}")
                
                self.db.callproc(handler, params)
            counter = counter + 1

    def __get_last_cargas(self):
        fecha_limit = dt.datetime.now() - dt.timedelta(hours=2)
        str_fecha_limit = fecha_limit.strftime('%Y-%m-%d %H:%M:%S')
        print(str_fecha_limit)
        result = self.db.fetch(f"""
        select
        cc.proyecto, trunc(fecha_archivo, 'hh24') fecha, count(*) counter, max(tx.granularidad) granularidad
        from padm_carga_control cc
        inner join (
            select a.*, 'nce.'||lower(codigo_medicion)||'_'||granularidad||'_min' proyecto from tx_tabla a where estado=1
        ) tx on tx.proyecto = cc.proyecto
        where cc.proyecto like 'nce.%' and cc.FIN >= TO_DATE('{str_fecha_limit}', 'YYYY-MM-DD HH24:MI:SS')
        group by cc.proyecto, trunc(fecha_archivo, 'hh24')
        having (
            select count(distinct a.fecha_archivo) from padm_carga_control a 
            where a.proyecto = cc.proyecto and trunc(a.fecha_archivo, 'hh24') = trunc(cc.fecha_archivo, 'hh24')
            group by a.proyecto, trunc(a.fecha_archivo, 'hh24')
        ) = (60 / max(tx.granularidad))
        order by cc.proyecto
        """)
        resp = []
        for row in result:
            resp.append({'proyecto': row[0], 'fecha': row[1]})
        return resp

    def __get_ora_handlers_by_proyecto(self, proyecto, format='hxh'):
        result = self.db.fetch(F"""
        select proyecto, handler, norder from padm_carga_resumen_handler
        where estado=1 and proyecto='{proyecto}' and format='{format}'
        order by proyecto, norder
        """)
        resp = []
        for row in result:
            resp.append({'proyecto': row[0], 'handler': row[1], 'norder': row[2]})
        return resp

    def __get_params_to_handler(self, handler, def_params):
        index_1 = None
        index_2 = None
        params_to_return = {}
        templates = {}
        try:
            index_1 = handler.index('(')
            index_2 = handler.index(')')
        except:
            pass
        if index_1 is not None and index_2 is not None:
            proc_params = handler.replace(' ','')
            #print(proc_params)
            for p in list(def_params):
                pattern = re.compile(f".*\[{p}\].*")
                if pattern.match(proc_params):
                    if f":{p}" in templates:
                        handler = handler.replace(f":{p}", templates[f":{p}"])
                    params_to_return[p] = def_params[p]
                    handler = handler.replace(f"[{p}]", f":{p}")
        return handler, params_to_return