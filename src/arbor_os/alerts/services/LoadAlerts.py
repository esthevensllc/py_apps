import json
import datetime
import pytz
from src.shared.config import TIMEZONE

class LoadAlerts:
    def __init__(self, repository, srcprefixes_repo, srccountry_repo, pattern_repo, arbor_api):
        self.repository = repository
        self.srcprefixes_repo = srcprefixes_repo
        self.srccountry_repo = srccountry_repo
        self.pattern_repo = pattern_repo
        self.tzone = pytz.timezone(TIMEZONE)
        self.arbor_api = arbor_api
        self.def_attr = {
            'id': None,
            'alert_class': None,
            'alert_type': None,
            'classification': None,
            'importance': None,
            'ongoing': None,
            'start_time': None,
            'stop_time': None,
        }
        self.def_suboject_by_class = {
            'bgp': {
                'aspath': None,
                'bgp_prefix': None,
                'local_prefix': None,
                'new_aspath': None,
                'new_nexthop': None,
                'old_aspath': None,
                'old_nexthop': None,
                'trap_type': None,
                'updates': None,
            },
            'cloudsignal': {'fault_description': None},
            'data': {'bgp_session_name': None},
            'dos': {
                'countries': None,
                'destination_mac_address': None,
                'direction': None,
                'dot1q_vlan_id': None,
                'fast_detected': None,
                'host_address': None,
                'impact_boundary': None,
                'impact_bps': None,
                'impact_pps': None,
                'ip_version': None,
                'misuse_types': [],
                'protocols': [],
                'severity_percent': None,
                'severity_threshold': None,
                'severity_unit': None,
            },
            'smart_thresh': {
                'alert_view': {},
                'name': None,
                'observed': None,
                'threshold': None,
                'unit': None
            },
            'tms': {
                'description': None,
                'dst_address': None,
                'expected': None,
                'mean': None,
                'name': None
            },
            'system_error': {
                'description': None,
                'entity_count': None,
                'entity_limit': None,
                'entity_type': None,
                'type': None,
                'threshold': None,
                'value': None
            },
            'system_event': {
                'username': None,
                'version': None
            },
            'traffic': {
                'interface_gid': None,
                'interface_name': None,
                'interface_speed': None,
                'threshold': None,
                'type': None,
                'unit': None,
                'usage': None
            }
        }
        self.srcprefixes_unit = 'pps'
        self.srccountries_unit = 'pps'
        self.def_patterns = {
            'id': None,
            'protocol': None,
            'timeseries_start': None,
            'all_tcp_flags': [],
            'timeseries_end': None,
            'step': None,
            'dst_port_range': {'high': None, 'low': None},
            'dst_prefix': None,
            'src_port_range': {'high': None, 'low': None},
            'traffic_data': {'current': None, 'max': None, 'pct95': None, 'avg': None},
            'src_prefix': None
        }
    
    def execute(self, fecha1, fecha2):
        str_fecha1 = fecha1.strftime('%Y-%m-%d %H:%M:%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%d %H:%M:%S')
        print("Recarga Arbor.alerts {} - {}".format(str_fecha1, str_fecha2))

        # app_customer_traffic_response = self.__get_traffic_from_file(fecha1, fecha2)
        alerts_resp = self.__get_from_api(fecha1, fecha2)
        def_all_subobject = self.__get_def_all_subobject()
        alerts = alerts_resp['data']
        registros_to_insert = []
        for row in alerts:
            attributes = row['attributes'].copy()
            attributes.pop('subobject')
                
            attr = dict(self.def_attr, **attributes)
            alert_class = attr['alert_class']
            if alert_class == 'system':
                alert_class = 'system_error'
            subobject = dict(self.def_suboject_by_class[alert_class], **row['attributes']['subobject'])
            new_subobject = {}
            for field in list(self.def_suboject_by_class[alert_class]):
                new_subobject[f'{alert_class}_{field}'] = subobject[field]
            
            subobject = dict(def_all_subobject, **new_subobject)
            alert = dict(attr, **subobject)
            try:
                alert['id'] = row['id']
                alert['ongoing'] = 1 if alert['ongoing'] == True else 0
                alert['dos_fast_detected'] = 1 if alert['dos_fast_detected'] == True else 0
                alert['dos_misuse_types'] = json.dumps(alert['dos_misuse_types'])
                alert['dos_protocols'] = json.dumps(alert['dos_protocols'])
                alert['smart_thresh_alert_view'] = json.dumps(alert['smart_thresh_alert_view'])
                alert['start_time'] = self.__strutc_to_localdt(alert['start_time'], '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S')
                alert['stop_time'] = self.__strutc_to_localdt(alert['stop_time'], '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S')
                alert['application_id'] = self.__get_relation_id(row['relationships'], 'application')
                alert['config_change_host_id'] = self.__get_relation_id(row['relationships'], 'config_change_host')
                alert['device_id'] = self.__get_relation_id(row['relationships'], 'device')
                alert['fingerprint_id'] = self.__get_relation_id(row['relationships'], 'fingerprint')
                alert['global_detection_settings_id'] = self.__get_relation_id(row['relationships'], 'global_detection_settings')
                alert['managed_object_id'] = self.__get_relation_id(row['relationships'], 'managed_object')
                alert['mitigation_id'] = self.__get_relation_id(row['relationships'], 'mitigation')
                alert['router_id'] = self.__get_relation_id(row['relationships'], 'router')
                alert['service_id'] = self.__get_relation_id(row['relationships'], 'service')
                alert['traffic_id'] = self.__get_relation_id(row['relationships'], 'traffic')
                alert['moved_mitigation_id'] = self.__get_relation_id(row['relationships'], 'moved_mitigation')
                alert['src_group_id'] = self.__get_relation_id(row['relationships'], 'src_group')
                alert['dest_group_id'] = self.__get_relation_id(row['relationships'], 'dest_group')
                alert['source_ip_addresses_id'] = self.__get_relation_id(row['relationships'], 'source_ip_addresses')
                registros_to_insert.append(alert)
            except:
                print(alert)

        self.repository.delete_where_collectiontime_between(fecha1, fecha2)
        self.repository.insert_from_array(registros_to_insert)
        print("Registros: {}".format(len(registros_to_insert)))

        mapped_id = list(map(lambda v: v['id'], registros_to_insert))
        
        print("srcprefixes")
        self.srcprefixes_repo.delete_where_alerts_id(mapped_id)

        srcprefixes_to_insert = []
        for alert_id in mapped_id:
            resp = self.arbor_api.get(f'api/sp/alerts/{alert_id}/traffic/src_prefixes/?query_unit={self.srcprefixes_unit}&query_limit=10')
            if resp.status_code == 200:
                resp = resp.json()
                counter = 1
                for srcprefix in resp['data']:
                    to_add = srcprefix['attributes']['view']['network']['unit'][self.srcprefixes_unit]
                    to_add['id'] = srcprefix['id']
                    to_add['alert_id'] = alert_id
                    to_add['timeseries'] = json.dumps(to_add['timeseries'])
                    to_add['timeseries_start'] = self.__strutc_to_localdt(to_add['timeseries_start'], '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S')
                    to_add['unit'] = self.srcprefixes_unit
                    to_add['ranking'] = counter
                    srcprefixes_to_insert.append(to_add)
                    counter += 1
        self.srcprefixes_repo.insert_from_array(srcprefixes_to_insert)

        print("srccountry")
        self.srccountry_repo.delete_where_alerts_id(mapped_id)

        srccountries_to_insert = []
        for alert_id in mapped_id:
            resp = self.arbor_api.get(f'api/sp/alerts/{alert_id}/traffic/src_countries/?query_unit={self.srccountries_unit}&query_limit=5')
            if resp.status_code == 200:
                resp = resp.json()
                counter = 1
                for srcprefix in resp['data']:
                    to_add = srcprefix['attributes']['view']['network']['unit'][self.srccountries_unit]
                    to_add['id'] = srcprefix['id']
                    to_add['alert_id'] = alert_id
                    to_add['timeseries'] = json.dumps(to_add['timeseries'])
                    to_add['timeseries_start'] = self.__strutc_to_localdt(to_add['timeseries_start'], '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S')
                    to_add['unit'] = self.srccountries_unit
                    to_add['ranking'] = counter
                    srccountries_to_insert.append(to_add)
                    counter += 1
            else:
                print(f'alert_id: {alert_id}')
        self.srccountry_repo.insert_from_array(srccountries_to_insert)

        self.__load_patterns(mapped_id)

    def __get_from_api(self, fecha1, fecha2):
        f1 = self.tzone.localize(fecha1 - datetime.timedelta(seconds=1))
        f2 = self.tzone.localize(fecha2)
        #  - datetime.timedelta(seconds=1)
        srt_utc_fecha1 = f1.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S')
        srt_utc_fecha2 = f2.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S')
        print(f'{srt_utc_fecha1} - {srt_utc_fecha2}')

        p_filter = f'/data/attributes/start_time>{srt_utc_fecha1} AND /data/attributes/start_time<{srt_utc_fecha2}'
        resp = self.arbor_api.get('api/sp/alerts/', {'params': {'filter': p_filter, 'perPage': 9999}})
        return resp.json()

    def __load_patterns(self, alerts_id):
        print("pattern")
        self.pattern_repo.delete_where_alerts_id(alerts_id)

        patterns_to_insert = []
        for alert_id in alerts_id:
            resp = self.arbor_api.get(f'api/sp/alerts/{alert_id}/patterns/?query_limit=15')
            if resp.status_code == 200:
                resp = resp.json()
                counter = 1
                for pattern in resp['data']:
                    router = list(pattern['attributes']['view'])
                    router = router[0] if len(router)>0 else None
                    to_add = dict(self.def_patterns)
                    to_add['id'] = pattern['id']
                    if router is not None:
                        to_add = dict(to_add, **pattern['attributes']['view'][router])
                        to_add['alert_id'] = alert_id
                        to_add['router'] = router
                        to_add['all_tcp_flags'] = json.dumps(to_add['all_tcp_flags'])
                        to_add['dst_port_range'] = dict(self.def_patterns['dst_port_range'], **to_add['dst_port_range'])
                        to_add['src_port_range'] = dict(self.def_patterns['src_port_range'], **to_add['src_port_range'])
                        to_add['traffic_data'] = dict(self.def_patterns['traffic_data'], **to_add['traffic_data'])
                        to_add['timeseries_start'] = self.__strutc_to_localdt(to_add['timeseries_start'], '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S')
                        to_add['timeseries_end'] = self.__strutc_to_localdt(to_add['timeseries_end'], '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S')
                        to_add['ranking'] = counter

                        to_add['dst_port_range_high'] = to_add['dst_port_range']['high']
                        to_add['dst_port_range_low'] = to_add['dst_port_range']['low']
                        to_add['src_port_range_high'] = to_add['src_port_range']['high']
                        to_add['src_port_range_low'] = to_add['src_port_range']['low']
                        to_add['traffic_data_current'] = to_add['traffic_data']['current']
                        to_add['traffic_data_max'] = to_add['traffic_data']['max']
                        to_add['traffic_data_pct95'] = to_add['traffic_data']['pct95']
                        to_add['traffic_data_avg'] = to_add['traffic_data']['avg']

                        to_add.pop('dst_port_range')
                        to_add.pop('src_port_range')
                        to_add.pop('traffic_data')
                        patterns_to_insert.append(to_add)
                    counter += 1
        self.pattern_repo.insert_from_array(patterns_to_insert)
        # print(patterns_to_insert[0])

    def __get_def_all_subobject(self):
        all_subobj = {}
        for subobj in list(self.def_suboject_by_class):
            for field in self.def_suboject_by_class[subobj]:
                all_subobj[f'{subobj}_{field}'] = self.def_suboject_by_class[subobj][field]
        return all_subobj
    
    def __strutc_to_localdt(self, strdt, strf1, strf2):
        if strdt is None:
            return None
        dt = datetime.datetime.strptime(strdt, strf1).replace(tzinfo=None)
        return pytz.utc.localize(dt).astimezone(self.tzone).strftime(strf2)
    
    def __get_relation_id(self, relationships, rel_name):
        if rel_name in relationships.keys():
            if type(relationships[rel_name]['data']) == type([]):
                ids = list(map(lambda v: v['id'], relationships[rel_name]['data']))
                return json.dumps(ids)
            else:
                return relationships[rel_name]['data']['id']
        return None
    
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