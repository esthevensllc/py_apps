import datetime as dt
import re
from src.shared.config import DTFORMAT_BY_ALIAS, TDINTERVAL_BY_ALIAS
from src.control_carga.shared.services import LOAD_HANDLERS
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer

class LoadOracleHandlers:
    def __init__(self, repository, control_carga_repo):
        self.repository = repository
        self.control_carga_repo = control_carga_repo

    def execute(self, config_id="0", event_body={}):
        config = self.repository.find_by_id(config_id)
        if config is None:
            raise Exception(f"No se econtro una configuración de handlers para '{config_id}'")
        elif config['status'] != 1:
            raise Exception(f"La configuracíon para '{config_id}' no esta activa")

        print(f"{config['name']}-handlers")
        
        cargas = []
        has_control = len(event_body.keys()) > 0
        if config["query"] is None and len(event_body.keys()) > 0:
            date_format = DTFORMAT_BY_ALIAS[event_body['format']]
            fecha = dt.datetime.strptime(event_body['fec_ini'], date_format)
            cargas = [{'proyecto': config_id, 'fecha': fecha}]
        else:
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
            n_procedures = len(handlers)
            n_procedures_procesed = 0
            has_error = False
            error = None
            for h in handlers:
                start_time = dt.datetime.now()
                subHandlers = h['handler'].strip().split(";")
                subHandlers = list(map(lambda handler: handler.strip(), subHandlers))
                subHandlers = list(filter(lambda handler: handler != "", subHandlers))
                to_execute_list = []
                connection_type = self.get_connection_type(h['connection'])
                for subHandler in subHandlers:
                    handler, params = self.__get_params_to_handler(connection_type, subHandler, def_params.copy())
                    to_execute_list.append({
                        'connection': h['connection'],
                        'connection_type': connection_type,
                        'handler': handler,
                        'params': params
                    })
                handler_to_print = ";".join(list(map(lambda to_exec: to_exec["handler"][:100]+("..." if len(to_exec["handler"])>100 else ""), to_execute_list)))
                params_to_print = list(map(lambda to_exec: to_exec["params"], to_execute_list))
                print(f"[{h['norder']}] {handler_to_print}:")
                if len(subHandlers) > 1:
                    print(f"    {params_to_print}")
                else:
                    print(f"    {params_to_print[0]}")
                
                try:
                    for to_exec in to_execute_list:
                        self.repository.callproc(to_exec["connection"], to_exec["connection_type"], to_exec["handler"], to_exec["params"])
                    n_procedures_procesed += 1
                except BaseException as e:
                    has_error = True
                    error = e

                if has_error == True:
                    break
                
            end_time = dt.datetime.now()
            if has_control == True:
                self.control_carga_repo.save_carga(
                    row['proyecto'],
                    f"{row['proyecto']}_{row['fecha'].strftime('%Y%m%dT%H:%M:%S')}",
                    n_procedures_procesed,
                    n_procedures,
                    start_time,
                    end_time,
                    "CARGADO" if has_error == False else "ERROR",
                    str(error) if error is not None else '',
                    row['fecha']
                )
            if error is not None:
                raise error

            counter = counter + 1

    def __get_params_to_handler(self, connection_type, handler, def_params):
        index_1 = None
        index_2 = None
        params_to_return = {}
        templates = {}
        bindings_map_by_dbtype = {
            "oracle": {"string": ":%s"},
            "clickhouse": {"string": "{%s:String}"},
        }
        bindings_map = bindings_map_by_dbtype[connection_type]
        
        handler = handler.strip()
        for p in def_params.keys():
            if f"[{p}]" in handler:
                params_to_return[p] = def_params[p]
                strbind = (bindings_map["string"] % (p))
                handler = handler.replace(f"[{p}]", strbind)
        return handler, params_to_return

    def get_connection_type(self, connection):
        if connection is None or "oracle" in connection:
            return "oracle"
        elif "clickhouse" in connection:
            return "clickhouse"
        else:
            raise Exception("Database type is not supported")

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