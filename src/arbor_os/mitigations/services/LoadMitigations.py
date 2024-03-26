import json
import datetime
import pytz
from src.shared.config import TIMEZONE

class LoadMitigations:
    def __init__(self, repository, arbor_api):
        self.repository = repository
        self.arbor_api = arbor_api
        self.tzone = pytz.timezone(TIMEZONE)
        self.def_mitigation = {
            'id': None,
            'description': None,
            'ip_version': None,
            'name': None,
            'ongoing': None,
            'is_automitigation': None,
            'start': None,
            'stop': None,
            'subtype': None,
            'user': None,
            'alert_id': None,
            'subobject': {}
        }

    def execute(self):
        # resp = self.arbor_api.get('api/sp/mitigations/?perPage=9999').json()
        data = self.arbor_api.get_all('api/sp/mitigations/')
        print(f"datacount: {len(data)}")
        registros_to_insert = []
        for mitigation in data:
            temp_attr = mitigation['attributes'].copy()
            temp_attr.pop('subobject')
            mi = dict(self.def_mitigation, **temp_attr)
            mi['id'] = mitigation['id']
            mi['mi_user'] = mi['user']
            mi['start_time'] = self.__strutc_to_localdt(mi['start'], '%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%d %H:%M:%S')
            mi['stop_time'] = self.__strutc_to_localdt(mi['stop'], '%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%d %H:%M:%S')
            mi['ongoing'] = 1 if mi['ongoing'] == True else 0
            mi['is_automitigation'] = 1 if mi['is_automitigation'] == True else 0
            mi['alert_id'] = self.__get_relation_id(mitigation['relationships'], 'alert')
            try:
                mi['subobject'] = json.dumps(mitigation['attributes']['subobject'])
            except:
                print(mi['id'])
            mi.pop('user')
            mi.pop('start')
            mi.pop('stop')
            if mi['start_time'] is not None:
                registros_to_insert.append(mi)
            else:
                print(mi['id'])
        
        self.repository.delete_all()
        self.repository.insert_from_array(registros_to_insert)
        print("Registros: {}".format(len(registros_to_insert)))

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