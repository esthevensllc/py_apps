import datetime as dt
import re

class LoadOracleHandlers:
    def __init__(self, repository):
        self.repository = repository

    def execute(self, config_id="0"):
        config = self.repository.find_by_id(config_id)
        if config is None:
            raise Exception(f"No se econtro una configuración de handlers para '{config_id}'")
        elif config['status'] != 1:
            raise Exception(f"La configuracíon para '{config_id}' no esta activa")

        print(f"{config['name']}-handlers")
        
        cargas = self.repository.get_last_cargas(config['id'])
        counter = 1
        for row in cargas:
            handlers = self.repository.get_ora_handlers_by_proyecto(row['proyecto'], config['format'])
            p_farchivo_hxh = row['fecha']
            p_farchivo_fin_hxh = row['fecha'] + dt.timedelta(hours=1)
            p_farchivo_fin_dxd = row['fecha'] + dt.timedelta(days=1)
            def_params = {
                'p_farchivo_hxh': p_farchivo_hxh.strftime('%Y-%m-%d %H:%M:%S'),
                'p_farchivo_fin_hxh': p_farchivo_fin_hxh.strftime('%Y-%m-%d %H:%M:%S'),
                'p_farchivo_hxh_f1': p_farchivo_hxh.strftime('%d/%m/%Y %H'),
                'p_farchivo_fin_hxh_f1': p_farchivo_fin_hxh.strftime('%d/%m/%Y %H'),
                'p_farchivo_dxd_f1': p_farchivo_hxh.strftime('%d/%m/%Y'),
                'p_farchivo_fin_dxd_f1': p_farchivo_fin_dxd.strftime('%d/%m/%Y')
            }
            print()
            print(row['proyecto'])
            for h in handlers:
                handler, params = self.__get_params_to_handler(h['handler'], def_params)
                print(f"[{h['norder']}] {handler}:")
                print(f"    {params}")
                
                self.repository.callproc(handler, params)
            counter = counter + 1

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