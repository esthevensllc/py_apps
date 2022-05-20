import datetime
from src.apic.shared.services import BaseApicService

class LoadInterfaceHealth(BaseApicService):
    def __init__(self, health_repo, apic_service):
        self.health_repo = health_repo
        self.apic_service = apic_service

    def execute(self):
        fecha2 = datetime.datetime.now().replace(minute=0, second=0)
        fecha1 = fecha2 - datetime.timedelta(hours=12)
        print("apic.load_interfaces_health")
        healths_to_insert = []
        healths_to_delete = []
        nodes_by_topology = {'1': []}
        for top in list(nodes_by_topology):
            nodes_by_topology[top] = self._get_nodesid_by_topology(top)
            for node_id in nodes_by_topology[top]:
                interfaces_id = self.__get_interfacesid_by_topology_and_node(top, node_id)
                print(f"[{node_id}]: {len(interfaces_id)}")
                for int_id in interfaces_id:
                    healths_of_int, min_date, max_date = self.__get_interface_healths_by_topology_node_interface(top, node_id, int_id, fecha1, fecha2)
                    if len(healths_of_int) > 0:
                        healths_to_insert = healths_to_insert + healths_of_int
                        healths_to_delete.append({'interface_id': f"{top}-{node_id}-{int_id}", 'fec_ini': min_date, 'fec_fin': max_date})

        self.health_repo.delete_from_array_where_collectiontime_between(healths_to_delete)
        self.health_repo.insert_from_array(healths_to_insert)

    def __get_interfacesid_by_topology_and_node(self, top_id, node_id):
        params = {
            'rsp-subtree': 'children',
            'rsp-subtree-class': 'ethpmPhysIf',
            'order-by': 'l1PhysIf.monPolDn|asc'
        }
        response = self.apic_service.get(f'node/class/topology/pod-{top_id}/node-{node_id}/l1PhysIf.json', {'params': params})
        response = response.json()
        interfaces_id = []
        for row in response['imdata']:
            attributes = row['l1PhysIf']['attributes']
            interfaces_id.append(attributes['id'])
        return interfaces_id

    def __get_interface_healths_by_topology_node_interface(self, top_id, node_id, int_id, fecha1, fecha2):
        str_fecha1 = fecha1.strftime('%Y-%m-%dT%H:%M:%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%dT%H:%M:%S')
        params = {
            'rsp-subtree-include': 'fault-records,no-scoped,subtree',
            'query-target-filter': f'and(not(wcard(healthRecord.dn,"__ui_")),eq(healthRecord.affected,"topology/pod-{top_id}/node-{node_id}/sys/phys-[{int_id}]"))',
            #'rsp-subtree-filter': f'and(ge(faultRecord.created,"{str_fecha1}"), lt(faultRecord.created,"{str_fecha2}"))',
            'order-by': 'healthRecord.created|desc'
        }
        response = self.apic_service.get(f'node/class/healthRecord.json', {'params': params}).json()
        events = []
        dates = []
        min_date = None
        max_date = None
        for row in response['imdata']:
            attr = row['healthRecord']['attributes']
            to_add = attr
            dates.append(self._format_str_dt(to_add['created'], to_format='%Y%m%d%H%M%S'))
            to_add['created'] = self._format_str_dt(to_add['created'])
            to_add['interface_id'] = f"{top_id}-{node_id}-{int_id}"
            events.append(to_add)
        if len(dates) > 0:
            min_str_date = min(dates)
            max_str_date = max(dates)
            min_date = datetime.datetime.strptime(min_str_date, '%Y%m%d%H%M%S')
            max_date = datetime.datetime.strptime(max_str_date, '%Y%m%d%H%M%S')
        return events, min_date, max_date