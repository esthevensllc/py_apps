import datetime as dt
import re
from src.shared.config import DTFORMAT_BY_ALIAS, TDINTERVAL_BY_ALIAS
from src.control_carga.shared.services import LOAD_HANDLERS
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer

class LoadOracleHandlers:
    def __init__(self, repository):
        self.repository = repository

    def execute(self, config_id="0", event_body={}):
        config = self.repository.find_by_id(config_id)
        if config is None:
            raise Exception(f"No se econtro una configuración de handlers para '{config_id}'")
        elif config['status'] != 1:
            raise Exception(f"La configuracíon para '{config_id}' no esta activa")

        print(f"{config['name']}-handlers")
        
        cargas = self.repository.get_last_cargas(config['id'], event_body)
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

    def event_handler(self, event):
        self.__guard(event)
        date_format = DTFORMAT_BY_ALIAS[event['msg_body']['format']]
        queue_id = event['queue_id']
        # config_id = event['msg_body']['config_id']
        fecha1 = dt.datetime.strptime(event['msg_body']['fec_ini'], date_format)
        fecha2 = None
        if 'fec_fin' in event['msg_body'].keys():
            fecha2 = dt.datetime.strptime(event['msg_body']['fec_fin'], date_format)
        else:
            fecha2 = fecha1 + dt.timedelta(**TDINTERVAL_BY_ALIAS[event['msg_body']['format']])

        event_body = event['msg_body']
        event_body["fec_ini"] = fecha1.strftime(date_format)
        event_body["fec_fin"] = fecha2.strftime(date_format)

        self.execute(queue_id, event_body)

    def __guard(self, event):
        msg_body_keys = event['msg_body'].keys()
        if ('fec_ini' not in msg_body_keys) or ('format' not in msg_body_keys): 
            raise Exception("Error no se encontro el atributo 'fec_ini' o 'format'")

        if event['msg_body']['format'] not in list(DTFORMAT_BY_ALIAS):
            raise Exception(f"Formato '{event['msg_body']['format']}' no valido")


class ResumenEventConsumer(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.1
        self.loop = False

    def execute(self, group_id):
        queues = self.queue_service.get_configs_by_group_id(group_id)

        for row in queues:
            self.queue_handlers[row["id"]] = {'handler': LOAD_HANDLERS, 'callback': lambda s, e: s.event_handler(e)}
        self.queue_ids = list(self.queue_handlers)

        super().execute()