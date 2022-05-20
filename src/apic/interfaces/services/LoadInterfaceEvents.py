import datetime
from src.apic.shared.services import BaseApicService

class LoadInterfaceEvents(BaseApicService):
    def __init__(self, event_repo, fault_repo, health_repo, apic_service):
        self.event_repo = event_repo
        self.fault_repo = fault_repo
        self.health_repo = health_repo
        self.apic_service = apic_service

    def execute(self):
        fecha2 = datetime.datetime.now().replace(minute=0, second=0)
        fecha1 = fecha2 - datetime.timedelta(hours=12)

        print("apic.load_interfaces_events")
        nodes_by_topology = {'1': []}
        to_template = None
        registros_to_insert = []
        registros_to_delete = []
        faults_to_insert = []
        faults_to_delete = []
        healths_to_insert = []
        healths_to_delete = []
        for top in list(nodes_by_topology):
            nodes_by_topology[top] = self._get_nodesid_by_topology(top)
            #nodes_by_topology[top] = list(filter(lambda r: r == '119', nodes_by_topology[top]))
            for node_id in nodes_by_topology[top]:
                interfaces_id = self.__get_interfacesid_by_topology_and_node(top, node_id)
                #interfaces_id = list(filter(lambda r: r == 'eth1/10', interfaces_id))
                print(f"[{node_id}]: {len(interfaces_id)}")
                for int_id in interfaces_id:
                    events_of_int, min_date, max_date = self.__get_interface_events_by_topology_node_interface(top, node_id, int_id, fecha1, fecha2)
                    if len(events_of_int) > 0:
                        registros_to_insert = registros_to_insert + events_of_int
                        registros_to_delete.append({'interface_id': f"{top}-{node_id}-{int_id}", 'fec_ini': min_date, 'fec_fin': max_date})
                    
                    faults_of_int, min_date, max_date = self.__get_interface_faults_by_topology_node_interface(top, node_id, int_id, fecha1, fecha2)
                    if len(faults_of_int) > 0:
                        faults_to_insert = faults_to_insert + faults_of_int
                        faults_to_delete.append({'interface_id': f"{top}-{node_id}-{int_id}", 'fec_ini': min_date, 'fec_fin': max_date})

                    """healths_of_int, min_date, max_date = self.__get_interface_healths_by_topology_node_interface(top, node_id, int_id, fecha1, fecha2)
                    if len(healths_of_int) > 0:
                        healths_to_insert = healths_to_insert + healths_of_int
                        healths_to_delete.append({'interface_id': f"{top}-{node_id}-{int_id}", 'fec_ini': min_date, 'fec_fin': max_date})
                    """

        print(f"Events: {len(registros_to_insert)}")
        self.event_repo.delete_from_array_where_collectiontime_between(registros_to_delete)
        self.event_repo.insert_from_array(registros_to_insert)

        print(f"Faults: {len(faults_to_insert)}")
        self.fault_repo.delete_from_array_where_collectiontime_between(faults_to_delete)
        self.fault_repo.insert_from_array(faults_to_insert)

        #self.health_repo.delete_from_array_where_collectiontime_between(healths_to_delete)
        #self.health_repo.insert_from_array(healths_to_insert)
        """
        print(f"events: {len(registros_to_insert)}")
        print(f"faults: {len(faults_to_insert)}")
        template, bindings, table_temp = self._make_template_load('APIC_INTERFACE_FAULT', faults_to_insert[0], [])
        print(template)
        print()
        print(bindings)
        print()
        print(table_temp)
        """

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

    def __get_interface_events_by_topology_node_interface(self, top_id, node_id, int_id, fecha1, fecha2):
        str_fecha1 = fecha1.strftime('%Y-%m-%dT%H:%M:%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%dT%H:%M:%S')
        params = {
            'rsp-subtree-include': 'event-logs,no-scoped,subtree',
            'rsp-subtree-filter': f'and(ge(eventRecord.created,"{str_fecha1}"), lt(eventRecord.created,"{str_fecha2}"))',
            'order-by': 'eventRecord.created|desc'
        }
        response = self.apic_service.get(f'node/mo/topology/pod-{top_id}/node-{node_id}/sys/phys-[{int_id}].json', {'params': params}).json()
        events = []
        dates = []
        min_date = None
        max_date = None
        for row in response['imdata']:
            attr = row['eventRecord']['attributes']
            to_add = attr
            dates.append(self._format_str_dt(to_add['created'], to_format='%Y%m%d%H%M%S'))
            to_add['created'] = self._format_str_dt(to_add['created'])
            to_add['interface_id'] = f"{top_id}-{node_id}-{int_id}"
            to_add['e_user'] =  to_add['user']
            to_add.pop('user')
            events.append(to_add)
        if len(dates) > 0:
            min_str_date = min(dates)
            max_str_date = max(dates)
            min_date = datetime.datetime.strptime(min_str_date, '%Y%m%d%H%M%S')
            max_date = datetime.datetime.strptime(max_str_date, '%Y%m%d%H%M%S')
        return events, min_date, max_date

    def __get_interface_faults_by_topology_node_interface(self, top_id, node_id, int_id, fecha1, fecha2):
        str_fecha1 = fecha1.strftime('%Y-%m-%dT%H:%M:%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%dT%H:%M:%S')
        params = {
            'rsp-subtree-include': 'fault-records,no-scoped,subtree',
            'rsp-subtree-filter': f'and(ge(faultRecord.created,"{str_fecha1}"), lt(faultRecord.created,"{str_fecha2}"))',
            'order-by': 'faultRecord.created|desc'
        }
        response = self.apic_service.get(f'node/mo/topology/pod-{top_id}/node-{node_id}/sys/phys-[{int_id}].json', {'params': params}).json()
        events = []
        dates = []
        min_date = None
        max_date = None
        for row in response['imdata']:
            attr = row['faultRecord']['attributes']
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