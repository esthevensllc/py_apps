import datetime

class LoadAllInterfacesTraffic:
    def __init__(self, repository, interface_error_repo, interface_egress_repo, apic_service):
        self.repository = repository
        self.interface_error_repo = interface_error_repo
        self.interface_egress_repo = interface_egress_repo
        self.apic_service = apic_service

    def execute(self):
        fecha2 = datetime.datetime.now().replace(minute=0, second=0)
        fecha1 = fecha2 - datetime.timedelta(hours=1)

        params = {
            'query-target': 'children',
            'target-subtree-class': 'fabricNode',
            'query-target-filter': 'and(not(wcard(fabricNode.dn,"__ui_")),and(ne(fabricNode.role,"controller")))'
        }
        response = self.apic_service.get('node/mo/topology/pod-1.json', {'params': params})
        response = response.json()
        nodes_id = list(map(lambda row: f"{row['fabricNode']['attributes']['id']}", response['imdata']))

        print(f"Nodos: {len(nodes_id)}")

        for node_id in nodes_id:
            interfaces_id = self.get_interfaces_id_for_node(1, node_id)
            print(f"[{node_id}]: {len(interfaces_id)}")

            for int_id in interfaces_id:
                self.load_ingress_to_interface(fecha1, fecha2, 1, node_id, int_id)
                #self.load_ingress_error_to_interface(fecha1, fecha2, 1, node_id, int_id)
                #self.load_egress_to_interface(fecha1, fecha2, 1, node_id, int_id)

    def get_interfaces_id_for_node(self, topology_id, node_id):
        params = {
            'rsp-subtree': 'children',
            'rsp-subtree-class': 'ethpmPhysIf',
            'order-by': 'l1PhysIf.monPolDn|asc'
        }
        response = self.apic_service.get(f'node/class/topology/pod-{topology_id}/node-{node_id}/l1PhysIf.json', {'params': params})
        response = response.json()

        interfaces_id = []
        for row in response['imdata']:
            attributes = row['l1PhysIf']['attributes']
            interfaces_id.append(attributes['id'])
        return interfaces_id

    def load_ingress_to_interface(self, fecha1, fecha2, topology_id, node_id, interface):
        str_fecha1 = fecha1.strftime('%Y-%m-%dT%H:%M:%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%dT%H:%M:%S')
        params = {
            'rsp-subtree-class': 'eqptIngrTotalHist5min,eqptIngrErrPktsHist5min,eqptEgrTotalHist5min',
            #'rsp-subtree-filter': f'and(ge(eqptIngrTotalHist15min.repIntvEnd,"{str_fecha1}"), lt(eqptIngrTotalHist15min.repIntvEnd,"{str_fecha2}"))'
        }

        resp = self.get_stats_to_interface(params, topology_id, node_id, interface)
        interface_id = f"{topology_id}-{node_id}-{interface}"
        registros_to_insert = resp['eqptIngrTotalHist5min']['data']
        min_date = resp['eqptIngrTotalHist5min']['min_date']
        max_date = resp['eqptIngrTotalHist5min']['max_date']

        if min_date is not None and max_date is not None:
            self.repository.delete_where_collectiontime_between(interface_id, min_date, max_date)
        self.repository.insert_from_array(registros_to_insert)

        # Ingress Error
        registros_to_insert = resp['eqptIngrErrPktsHist5min']['data']
        min_date = resp['eqptIngrErrPktsHist5min']['min_date']
        max_date = resp['eqptIngrErrPktsHist5min']['max_date']
        if min_date is not None and max_date is not None:
            self.interface_error_repo.delete_where_collectiontime_between(interface_id, min_date, max_date)
        self.interface_error_repo.insert_from_array(registros_to_insert)

        # Egress
        registros_to_insert = resp['eqptEgrTotalHist5min']['data']
        min_date = resp['eqptEgrTotalHist5min']['min_date']
        max_date = resp['eqptEgrTotalHist5min']['max_date']
        if min_date is not None and max_date is not None:
            self.interface_egress_repo.delete_where_collectiontime_between(interface_id, min_date, max_date)
        self.interface_egress_repo.insert_from_array(registros_to_insert)
        #print(f"[{interface_id}]: {len(registros_to_insert)}")

    def load_ingress_error_to_interface(self, fecha1, fecha2, topology_id, node_id, interface):
        str_fecha1 = fecha1.strftime('%Y-%m-%dT%H:%M:%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%dT%H:%M:%S')
        params = {
            'rsp-subtree-class': 'eqptIngrErrPktsHist5min',
            #'rsp-subtree-filter': f'and(ge(eqptIngrErrPktsHist15min.repIntvEnd,"{str_fecha1}"), lt(eqptIngrErrPktsHist15min.repIntvEnd,"{str_fecha2}"))'
        }
        resp = self.get_stats_to_interface(params, topology_id, node_id, interface)
        interface_id = f"{topology_id}-{node_id}-{interface}"
        registros_to_insert = resp['data']
        min_date = resp['min_date']
        max_date = resp['max_date']

        if min_date is not None and max_date is not None:
            self.interface_error_repo.delete_where_collectiontime_between(interface_id, min_date, max_date)
        self.interface_error_repo.insert_from_array(registros_to_insert)
        #print(f"[{interface_id}]: {len(registros_to_insert)}")

    def load_egress_to_interface(self, fecha1, fecha2, topology_id, node_id, interface):
        str_fecha1 = fecha1.strftime('%Y-%m-%dT%H:%M:%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%dT%H:%M:%S')
        params = {
            'rsp-subtree-class': 'eqptEgrTotalHist5min',
            #'rsp-subtree-filter': f'and(ge(eqptEgrTotalHist15min.repIntvEnd,"{str_fecha1}"), lt(eqptEgrTotalHist15min.repIntvEnd,"{str_fecha2}"))'
        }
        resp = self.get_stats_to_interface(params, topology_id, node_id, interface)
        interface_id = f"{topology_id}-{node_id}-{interface}"
        registros_to_insert = resp['data']
        min_date = resp['min_date']
        max_date = resp['max_date']
        if min_date is not None and max_date is not None:
            self.interface_egress_repo.delete_where_collectiontime_between(interface_id, min_date, max_date)
        self.interface_egress_repo.insert_from_array(registros_to_insert)
        #print(f"[{interface_id}]: {len(registros_to_insert)}")


    def get_stats_to_interface(self, extra_params, topology_id, node_id, interface):
        params = {'rsp-subtree-include': 'stats'}
        params = dict(params, **extra_params)
        response = self.apic_service.get(f'node/mo/topology/pod-{topology_id}/node-{node_id}/sys/phys-[{interface}].json', {'params': params})
        response = response.json()
        
        subtree_class = params['rsp-subtree-class']
        subtree_class_list = subtree_class.split(',')
        min_date = None
        max_date = None
        stats = []
        if 'children' in response['imdata'][0]['l1PhysIf'].keys():
            stats = response['imdata'][0]['l1PhysIf']['children']

        response_by_class = {}
        for s_class in subtree_class_list:
            response_by_class[s_class] = {'data': [], 'fechas': []}

        interface_id = f"{topology_id}-{node_id}-{interface}"
        for row in stats:
            class_of_row = list(row)[0]
            to_add = row[class_of_row]['attributes']
            repIntvEnd = datetime.datetime.strptime(to_add['repIntvEnd'], '%Y-%m-%dT%H:%M:%S.%f%z')
            to_add['interface_id'] = interface_id
            to_add['repIntvEnd'] = repIntvEnd.strftime('%Y-%m-%d %H:%M:%S')
            to_add['repIntvStart'] = datetime.datetime.strptime(to_add['repIntvStart'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')
            to_add.pop('index')
            response_by_class[class_of_row]['data'].append(to_add)
            response_by_class[class_of_row]['fechas'].append(repIntvEnd.strftime("%Y%m%d%H%M%S"))

            """
            if min_date is None:
                min_date = repIntvEnd
            elif repIntvEnd < min_date:
                min_date = repIntvEnd
            
            if max_date is None:
                max_date = repIntvEnd
            elif repIntvEnd > max_date:
                max_date = repIntvEnd
            """
        for class_of_row in subtree_class_list:
            min_date = None
            max_date = None
            if len(response_by_class[class_of_row]['fechas']) != 0:
                min_date = min(response_by_class[class_of_row]['fechas'])
                min_date = datetime.datetime.strptime(min_date, "%Y%m%d%H%M%S")
                max_date = max(response_by_class[class_of_row]['fechas'])
                max_date = datetime.datetime.strptime(max_date, "%Y%m%d%H%M%S")
            response_by_class[class_of_row]['min_date'] = min_date
            response_by_class[class_of_row]['max_date'] = max_date
        return response_by_class