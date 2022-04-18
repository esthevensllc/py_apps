import json
from src.shared.config import (STORAGE_DIR, TIMEZONE)
import datetime
import pytz

class LoadRouterCustomerTraffic:
    def __init__(self, repository, arbor_api):
        self.repository = repository
        self.arbor_api = arbor_api
        self.tzlocal = pytz.timezone(TIMEZONE)
    
    def execute(self, fecha1, fecha2):
        str_fecha1 = fecha1.strftime('%Y-%m-%d %H:%M:%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%d %H:%M:%S')
        print("Recarga Arbor.router_customer_traffic {} - {}".format(str_fecha1, str_fecha2))

        # app_peer_traffic_response = self.__get_traffic_from_file(fecha1, fecha2)
        app_peer_traffic_response = self.__get_traffic_from_api(fecha1, fecha2)
        app_peer_traffic = app_peer_traffic_response['data']['attributes']['results']
        # print(app_peer_traffic.keys())
        print("Traffic {} - {}".format(app_peer_traffic_response['data']['attributes']['query_start_time'], app_peer_traffic_response['data']['attributes']['query_end_time']))
        traffic_to_insert = []
        for traffic in app_peer_traffic:
            row = traffic['traffic_classes']
            row_to_add = {'granularidad': row['in']['step']/60}
            
            for item in traffic['facet_values']:
                row_to_add[item['facet'].lower()] = item['name']
            
            fecha_recorrido = fecha1
            for index in range(len(row['in']['timeseries'])):
                row_to_add['collectiontime'] = fecha_recorrido.strftime('%Y-%m-%d %H:%M:%S')
                row_to_add['in_bps'] = row['in']['timeseries'][index]
                row_to_add['out_bps'] = row['out']['timeseries'][index]
                traffic_to_insert.append(row_to_add.copy())

                fecha_recorrido = fecha_recorrido + datetime.timedelta(minutes=(row['in']['step']/60))

        self.repository.delete_where_collectiontime_between(fecha1, fecha2)
        self.repository.insert_from_array(traffic_to_insert)
        
        print("Registros: {}".format(len(traffic_to_insert)))

    def __get_traffic_from_file(self, fecha1, fecha2):
        to_zone = pytz.timezone(TIMEZONE)

        fecha2 = fecha2 - datetime.timedelta(minutes=1)

        str_fecha1 = fecha1.strftime('%Y-%m-%dT%H_%M_%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%dT%H_%M_%S')

        srt_utc_fecha1 = fecha1.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S%z')
        srt_utc_fecha2 = fecha2.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S%z')
        print("UTC: {} - {}".format(srt_utc_fecha1, srt_utc_fecha2))

        file = open(STORAGE_DIR+'arbor-os/traffic_queries_routercust_'+str_fecha1+'__'+str_fecha2+'.json', 'r')
        file_content = file.read()
        file.close()
        return json.loads(file_content)
    
    def __get_traffic_from_api(self, fecha1, fecha2):
        f1 = self.tzlocal.localize(fecha1)
        f2 = self.tzlocal.localize(fecha2 - datetime.timedelta(minutes=1))
        srt_utc_fecha1 = f1.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S%z')
        srt_utc_fecha2 = f2.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S%z')

        body_data = {
            'data': {
                'attributes': {
                    'filters': [
                        {'facet': "Router", 'values': [], 'groupby': True},
                        {'facet': "Customer", 'values': [], 'groupby': True}
                    ],
                    'limit': 999999999,
                    'query_start_time': srt_utc_fecha1,
                    'query_end_time': srt_utc_fecha2,
                    'unit': "bps"
                }
            }
        }
        print(f'utc {srt_utc_fecha1} - {srt_utc_fecha2}')
        resp = self.arbor_api.post('api/sp/traffic_queries/', {'data': json.dumps(body_data)})
        return resp.json()

    def event_handler(self, event):
        self.__guard(event)
        date_format = event['msg_body']['format']
        if event['msg_body']['format'] == 'dxd':
            date_format = '%Y-%m-%d'
        elif event['msg_body']['format'] == 'hxh':
            date_format = '%Y-%m-%d %H'
        elif event['msg_body']['format'] == 'mxm':
            date_format = '%Y-%m-%d %H:%M'
        
        fecha1 = datetime.datetime.strptime(event['msg_body']['fec_ini'], date_format)
        fecha2 = datetime.datetime.strptime(event['msg_body']['fec_fin'], date_format)
        self.execute(fecha1, fecha2)

    def __guard(self, event):
        msg_body_keys = event['msg_body'].keys()
        if 'fec_ini' not in msg_body_keys or ('fec_fin' not in msg_body_keys) or ('format' not in msg_body_keys):
            raise QueueBadArguments("Error no se encontro el atributo 'fec_ini', 'fec_fin' o 'format'")