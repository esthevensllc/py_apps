from src.san.shared.services import BaseSanService
import xml.etree.ElementTree as ET
import datetime as dt
import json
import cx_Oracle
from src.shared.config import DTFORMAT_BY_ALIAS, TDINTERVAL_BY_ALIAS

class LoadDataFromConfig(BaseSanService):
    def __init__(self, db, repository, san_service, control_carga_repo):
        self.db = db
        self.repository = repository
        self.san_service = san_service
        self.control_carga_repo = control_carga_repo

    def execute(self, config_id, fecha1, fecha2):
        #config_id = '2'
        #fecha1 = dt.datetime.strptime('2022-06-16 17:00:00', '%Y-%m-%d %H:%M:%S')
        #fecha2 = dt.datetime.strptime('2022-06-16 18:00:00', '%Y-%m-%d %H:%M:%S')
        fecha_recorrido = fecha1
        while fecha_recorrido < fecha2:
            self.__load_data_between(config_id, fecha_recorrido, fecha_recorrido + dt.timedelta(hours=1))
            fecha_recorrido = fecha_recorrido + dt.timedelta(hours=1)
            print("")

    def __load_data_between(self, config_id = None, fecha1 = None, fecha2 = None):
        start_time = dt.datetime.now()

        config = self.repository.find(config_id)
        if config is None:
            raise Exception(f"La configuracion '{config_id}' no existe")
        fields_config = self.repository.get_fields_by_id(config_id)
        if len(fields_config) == 0:
            raise Exception(f"La configuracion '{config_id}' no tiene campos activos")
        #print(fields_config)
        print(config['name'])
        print(f"{fecha1} - {fecha2}")
        registros = self.__get_data(config['query'], json.loads(config['root_data']), fecha1, fecha2)
        range_registros = range(len(registros))
        for i in range_registros:
            row = registros[i]
            row_to_add = {}
            for field in fields_config:
                value = row[field['api_fieldname']]
                if field['map_with'] is not None:
                    #print(field['map_with'])
                    value = eval(f"f\"{field['map_with']}\"")
                row_to_add[field['fieldname']] = value
            registros[i] = row_to_add
        print(len(registros))

        #carga
        fields_to_use = list(filter(lambda f: f['to_reload'] is not None, fields_config))
        str_fields = ', '.join(list(map(lambda r: r['fieldname'], fields_config)))
        str_bind_fields = ', '.join(list(map(lambda r: f":{r['fieldname']}" if r['type'] != 'date' else f"TO_DATE(:{r['fieldname']}, 'yyyy-mm-dd hh24:mi:ss')", fields_config)))
        bindings = {}
        for f in fields_config:
            bindings[f['fieldname']] = cx_Oracle.NUMBER if f['type'] == 'number' else cx_Oracle.STRING

        insert_template = f"INSERT INTO {config['tablename']}({str_fields}) VALUES ({str_bind_fields})"
        if config['type'] == 'statistics':
            date_field = fields_to_use[0]
            str_fecha1 = fecha1.strftime('%Y-%m-%d %H:%M:%S')
            str_fecha2 = fecha2.strftime('%Y-%m-%d %H:%M:%S')
            delete_template = f"""DELETE FROM {config['tablename']}
            WHERE TO_DATE('{str_fecha1}', 'yyyy-mm-dd hh24:mi:ss') <= {date_field['fieldname']}
            AND {date_field['fieldname']} < TO_DATE('{str_fecha2}', 'yyyy-mm-dd hh24:mi:ss')"""
            #print(registros[0])
            #print(insert_template)
            #print(delete_template)
            registros = self.db.map_data_by_bindings(registros, bindings)
            self.db.query(delete_template)
            insert_config = {'template': insert_template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': config['limit_to_commit']}
            self.db.save_from_array2(insert_config, registros)

        end_time = dt.datetime.now()
        
        self.control_carga_repo.save_carga(
            config['queue_id'],
            config['name'],
            len(registros),
            len(registros),
            start_time,
            end_time,
            'CARGADO',
            '',
            fecha1
        )
        
            

    def __get_data(self, query, children_set_lvl, fecha1, fecha2):
        #<requestID>bgp.PeerStats</requestID>
        #equipment.InterfaceStats
        fecha1_f1 = int(fecha1.timestamp()*1000)
        fecha2_f1 = int(fecha2.timestamp()*1000)
        params = {
            'fecha1_f1': fecha1_f1,
            'fecha2_f1': fecha2_f1
        }
        body = query.format(**params)
        response = self.san_service.invoke({'data': body})
        root = ET.fromstring(response.text)

        for i in children_set_lvl:
            root = root[i]
        registros = self._map_entryset_to_row(root)
        return registros

    def event_handler(self, event):
        self.__guard(event)
        date_format = DTFORMAT_BY_ALIAS[event['msg_body']['format']]
        queue_id = event['queue_id']
        config_id = event['msg_body']['config_id']
        fecha1 = dt.datetime.strptime(event['msg_body']['fec_ini'], date_format)
        fecha2 = None
        if 'fec_fin' in event['msg_body'].keys():
            fecha2 = dt.datetime.strptime(event['msg_body']['fec_fin'], date_format)
        else:
            fecha2 = fecha1 + dt.timedelta(**TDINTERVAL_BY_ALIAS[event['msg_body']['format']])

        self.execute(config_id, fecha1, fecha2)

    def __guard(self, event):
        msg_body_keys = event['msg_body'].keys()
        if 'config_id' not in msg_body_keys or ('fec_ini' not in msg_body_keys) or ('format' not in msg_body_keys):
            raise Exception("Error no se encontro el atributo 'mediciones', 'fec_ini' o 'format'")

        if type(event['msg_body']['config_id']) != type(''):
            raise Exception("El config_id deven ser una cadena")

        if event['msg_body']['format'] not in list(DTFORMAT_BY_ALIAS):
            raise Exception(f"Formato '{event['msg_body']['format']}' no valido")


class SanEventProducer:
    def __init__(self, repository, queue_service):
        self.repository = repository
        self.queue_service = queue_service

    def execute(self):
        fecha1 = dt.datetime.now() - dt.timedelta(hours=1)
        cargas_config = self.repository.get()
        msg_body = {"fec_ini": fecha1.strftime('%Y-%m-%d %H'), "format": "hxh"}
        for row in cargas_config:
            data = {'queue_id': row['queue_id'], 'msg_body': json.dumps(msg_body)}
            self.queue_service.createEvent(data)
            print(data)
            
