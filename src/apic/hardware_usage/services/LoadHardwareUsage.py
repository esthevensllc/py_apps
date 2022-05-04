import datetime

class LoadHardwareUsage:
    def __init__(self, repository, mem_repo, temp_repo, apic_service):
        self.repository = repository
        self.mem_repo = mem_repo
        self.temp_repo = temp_repo
        self.apic_service = apic_service

    def execute(self):
        # fecha2 = datetime.datetime.strptime('2022-04-04 10:00:00', '%Y-%m-%d %H:%M:%S')
        # fecha1 = datetime.datetime.strptime('2022-04-04 09:00:00', '%Y-%m-%d %H:%M:%S')
        fecha2 = datetime.datetime.now().replace(minute=0, second=0)
        fecha1 = fecha2 - datetime.timedelta(hours=1)
        
        print("Carga hardaware_usage")
        params = {
            'query-target': 'children',
            'target-subtree-class': 'fabricNode',
            'query-target-filter': 'and(not(wcard(fabricNode.dn,"__ui_")),and(ne(fabricNode.role,"controller")))'
        }
        response = self.apic_service.get('node/mo/topology/pod-1.json', {'params': params})
        response = response.json()
        nodes_id = list(map(lambda row: f"node-{row['fabricNode']['attributes']['id']}", response['imdata']))

        nodes_by_topology = {'pod-1': nodes_id}
        str_fecha1 = fecha1.strftime('%Y-%m-%dT%H:%M:%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%dT%H:%M:%S')
        print(f'UTC: {str_fecha1} - {str_fecha2}')

        for index in nodes_by_topology.keys():
            for node in nodes_by_topology[index]:
                print("CPU")
                self.load_for_topology_and_node(index, node, fecha1, fecha2)
                print("Memory usage")
                self.load_mem_for_topology_and_node(index, node, fecha1, fecha2)
                print("Temperature")
                for sensor_id in [1,2,3,4,5]:
                    self.load_temperature_for_topology_and_node(index, node, sensor_id, fecha1, fecha2)

    def load_for_topology_and_node(self, topology, node, fecha1, fecha2):
        str_fecha1 = fecha1.strftime('%Y-%m-%dT%H:%M:%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%dT%H:%M:%S')
        params = {'rsp-subtree-filter': f'and(ge(procSysCPUHist15min.repIntvEnd,"{str_fecha1}"), lt(procSysCPUHist15min.repIntvEnd,"{str_fecha2}"))'}
        response = self.apic_service.get(f'node/mo/topology/{topology}/{node}/sys/procsys.json?rsp-subtree-include=stats&rsp-subtree-class=procSysCPUHist15min', {'params': params})
        response = response.json()
        # print(response)
        temp_list = []
        if 'children' in response['imdata'][0]['procSystem'].keys():
            temp_list = response['imdata'][0]['procSystem']['children']
        registros_to_insert = []
        min_date = None
        max_date = None
        for row in temp_list:
            attr = row['procSysCPUHist15min']['attributes']
            attr.pop('index')
            repIntvEnd = datetime.datetime.strptime(attr['repIntvEnd'], '%Y-%m-%dT%H:%M:%S.%f%z')
            attr['repIntvEnd'] = repIntvEnd.strftime('%Y-%m-%d %H:%M:%S')
            attr['repIntvStart'] = datetime.datetime.strptime(attr['repIntvStart'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')
            attr['topology'] = topology
            attr['node'] = node
            registros_to_insert.append(attr)

            if min_date is None:
                min_date = repIntvEnd
            elif repIntvEnd < min_date:
                min_date = repIntvEnd
            
            if max_date is None:
                max_date = repIntvEnd
            elif repIntvEnd > max_date:
                max_date = repIntvEnd
        print(registros_to_insert[0])
        if min_date is not None and max_date is not None:
            print("[{}] min: {} - max: {}".format(node, min_date, max_date))
            self.repository.delete_where_collectiontime_between(node, min_date, max_date)
        self.repository.insert_from_array(registros_to_insert)
        print(f"Registros: {len(registros_to_insert)}")

    def load_mem_for_topology_and_node(self, topology, node, fecha1, fecha2):
        str_fecha1 = fecha1.strftime('%Y-%m-%dT%H:%M:%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%dT%H:%M:%S')
        params = {'rsp-subtree-filter': f'and(ge(procSysMemHist15min.repIntvEnd,"{str_fecha1}"), lt(procSysMemHist15min.repIntvEnd,"{str_fecha2}"))'}
        response = self.apic_service.get(f'node/mo/topology/{topology}/{node}/sys/procsys.json?rsp-subtree-include=stats&rsp-subtree-class=procSysMemHist15min', {'params': params})
        response = response.json()

        temp_list = []
        if 'children' in response['imdata'][0]['procSystem'].keys():
            temp_list = response['imdata'][0]['procSystem']['children']
        registros_to_insert = []
        min_date = None
        max_date = None
        for row in temp_list:
            attr = row['procSysMemHist15min']['attributes']
            attr.pop('index')
            repIntvEnd = datetime.datetime.strptime(attr['repIntvEnd'], '%Y-%m-%dT%H:%M:%S.%f%z')
            attr['repIntvEnd'] = repIntvEnd.strftime('%Y-%m-%d %H:%M:%S')
            attr['repIntvStart'] = datetime.datetime.strptime(attr['repIntvStart'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')
            attr['topology'] = topology
            attr['node'] = node
            registros_to_insert.append(attr)

            if min_date is None:
                min_date = repIntvEnd
            elif repIntvEnd < min_date:
                min_date = repIntvEnd
            
            if max_date is None:
                max_date = repIntvEnd
            elif repIntvEnd > max_date:
                max_date = repIntvEnd
        
        if min_date is not None and max_date is not None:
            print("[{}] min: {} - max: {}".format(node, min_date, max_date))
            self.mem_repo.delete_where_collectiontime_between(node, min_date, max_date)
        self.mem_repo.insert_from_array(registros_to_insert)
        print(f"Registros: {len(registros_to_insert)}")

    def load_temperature_for_topology_and_node(self, topology, node, sensor_id, fecha1, fecha2):
        str_fecha1 = fecha1.strftime('%Y-%m-%dT%H:%M:%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%dT%H:%M:%S')
        params = {'rsp-subtree-filter': f'and(ge(eqptTempHist15min.repIntvEnd,"{str_fecha1}"), lt(eqptTempHist15min.repIntvEnd,"{str_fecha2}"))'}
        response = self.apic_service.get(f'node/mo/topology/{topology}/{node}/sys/ch/supslot-1/sup/sensor-{sensor_id}.json?rsp-subtree-include=stats&rsp-subtree-class=eqptTempHist15min', {'params': params})
        response = response.json()

        temp_list = []
        if 'children' in response['imdata'][0]['eqptSensor'].keys():
            temp_list = response['imdata'][0]['eqptSensor']['children']
        registros_to_insert = []
        min_date = None
        max_date = None
        for row in temp_list:
            attr = row['eqptTempHist15min']['attributes']
            attr.pop('index')
            repIntvEnd = datetime.datetime.strptime(attr['repIntvEnd'], '%Y-%m-%dT%H:%M:%S.%f%z')
            attr['repIntvEnd'] = repIntvEnd.strftime('%Y-%m-%d %H:%M:%S')
            attr['repIntvStart'] = datetime.datetime.strptime(attr['repIntvStart'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')
            attr['topology'] = topology
            attr['node'] = node
            attr['sensor'] = sensor_id
            registros_to_insert.append(attr)

            if min_date is None:
                min_date = repIntvEnd
            elif repIntvEnd < min_date:
                min_date = repIntvEnd
            
            if max_date is None:
                max_date = repIntvEnd
            elif repIntvEnd > max_date:
                max_date = repIntvEnd
        
        if min_date is not None and max_date is not None:
            print("[{}] min: {} - max: {}".format(node, min_date, max_date))
            self.temp_repo.delete_where_collectiontime_between(node, sensor_id, min_date, max_date)
        self.temp_repo.insert_from_array(registros_to_insert)
        print(f"Registros: {len(registros_to_insert)}")
        
        # table_attr = registros_to_insert[0]
        # sql_create = ''
        # sql_bind = ''
        # for index in table_attr.keys():
        #     value = table_attr[index]
        #     try:
        #         value = float(table_attr[index])
        #     except:
        #         pass
        #     type_str = 'cx_Oracle.NUMBER' if type(value) == type(1.2) else 'cx_Oracle.STRING'
        #     sql_create += f'\'{index}\': {type_str}, '
        #     sql_bind += f':{index}, '

        # print(sql_create)
        # print('')
        # print(sql_bind)

            
