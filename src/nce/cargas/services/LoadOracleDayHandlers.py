import datetime as dt
import re

class LoadOracleDayHandlers:
    def __init__(self, db):
        self.db = db

    def execute(self):
        handlers = self.__get_day_handlers()
        fecha_fin = dt.datetime.now()
        fecha_ini = fecha_fin - dt.timedelta(days=2)
        fecha_recorrido = fecha_ini
        while fecha_recorrido < fecha_fin:
            print(fecha_recorrido)
            p_farchivo_hxh = fecha_recorrido
            p_farchivo_fin_hxh = p_farchivo_hxh + dt.timedelta(hours=1)
            p_farchivo_dxd = fecha_recorrido
            p_farchivo_fin_dxd = fecha_recorrido + dt.timedelta(days=1)
            def_params = {
                'p_farchivo_hxh_f1': p_farchivo_hxh.strftime('%d/%m/%Y %H'),
                'p_farchivo_fin_hxh_f1': p_farchivo_fin_hxh.strftime('%d/%m/%Y %H'),
                'p_farchivo_dxd_f1': p_farchivo_dxd.strftime('%d/%m/%Y'),
                'p_farchivo_fin_dxd_f1': p_farchivo_fin_dxd.strftime('%d/%m/%Y')
            }
            #print(row['proyecto'])
            for h in handlers:
                handler, params = self.__get_params_to_handler(h['handler'], def_params)
                print(f"[{h['norder']}] {handler}: {params}")
                self.db.callproc(handler, params)
            fecha_recorrido = fecha_recorrido + dt.timedelta(days=1)


    def __get_day_handlers(self):
        result = self.db.fetch(F"""
        select proyecto, handler, norder from padm_carga_resumen_handler
        where estado=1 and format='dxd' and proyecto is null
        order by norder
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