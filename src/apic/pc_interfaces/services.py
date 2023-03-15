import cx_Oracle
import datetime
from src.apic.shared.services import BaseApicService

class LoadPCInterfaces(BaseApicService):
    def __init__(self, repository, apic_service):
        self.repository = repository
        self.apic_service = apic_service
        self.def_ethpmAggrIf_attr = {
            "accessVlan": None,
            "activeMbrs": None,
            "allowedVlans": None,
            "backplaneMac": None,
            "bundleBupId": None,
            "bundleIndex": None,
            "cfgAccessVlan": None,
            "cfgNativeVlan": None,
            "childAction": None,
            "currErrIndex": None,
            "diags": None,
            "encap": None,
            "errDisTimerRunning": None,
            "errVlanStatusHt": None,
            "errVlans": None,
            "hwBdId": None,
            "hwResourceId": None,
            "intfT": None,
            "iod": None,
            "lastErrors": None,
            "lastLinkStChg": None,
            "media": None,
            "modTs": None,
            "monPolDn": None,
            "nativeVlan": None,
            "numActivePorts": None,
            "numMbrUp": None,
            "numOfSI": None,
            "operBitset": None,
            "operDceMode": None,
            "operDuplex": None,
            "operEEERxWkTime": None,
            "operEEEState": None,
            "operEEETxWkTime": None,
            "operErrDisQual": None,
            "operFlowCtrl": None,
            "operMdix": None,
            "operMode": None,
            "operModeDetail": None,
            "operPhyEnSt": None,
            "operRouterMac": None,
            "operSpeed": None,
            "operSt": None,
            "operStQual": None,
            "operStQualCode": None,
            "operVlans": None,
            "osSum": None,
            "portCfgWaitFlags": None,
            "primaryVlan": None,
            "resetCtr": None,
            "rn": None,
            "siList": None,
            "status": None,
            "txT": None,
            "usage": None,
            "userCfgdFlags": None,
            "vdcId": None
        }

    def execute(self):
        print("Carga apic.cpu_interfaces")
        nodes_by_topology = {'1': []}
        registros_to_insert = []
        for top in list(nodes_by_topology):
            nodes_by_topology[top] = self._get_nodesid_by_topology(top)
            for node_id in nodes_by_topology[top]:
                cpu_interfaces = self.__get_cpu_interfaces_topology_and_node(top, node_id)
                registros_to_insert = registros_to_insert + cpu_interfaces
                print(f"[{node_id}]: {len(cpu_interfaces)}")
                self.repository.delete_by_topology_and_node(top, node_id)

        self.repository.insert_from_array(registros_to_insert)

    def __get_nodesid_by_topology(self, topology):
        params = {
            'query-target': 'children',
            'target-subtree-class': 'fabricNode',
            'query-target-filter': 'and(not(wcard(fabricNode.dn,"__ui_")),and(ne(fabricNode.role,"controller")))'
        }
        response = self.apic_service.get(f'node/mo/topology/pod-{topology}.json', {'params': params})
        response = response.json()
        nodes_id = list(map(lambda row: f"{row['fabricNode']['attributes']['id']}", response['imdata']))
        return nodes_id

    def __get_cpu_interfaces_topology_and_node(self, top_id, node_id):
        params = {
            'rsp-subtree': 'children',
            'rsp-subtree-class': 'ethpmAggrIf',
            'order-by': 'pcAggrIf.name|desc'
        }
        response = self.apic_service.get(f"node/class/topology/pod-{top_id}/node-{node_id}/pcAggrIf.json", {'params': params}).json()
        main_object = response['imdata']
        interfaces = []
        for row in response['imdata']:
            attr = row['pcAggrIf']['attributes']
            children = {}
            if len(row['pcAggrIf']['children']) == 0:
                children = self.def_ethpmAggrIf_attr.copy()
            else:
                children = row['pcAggrIf']['children'][0]['ethpmAggrIf']['attributes']
            
            for field in list(self.def_ethpmAggrIf_attr):
                attr[f'ethpmAggrIf_{field}'] = children[field]

            attr['int_mode'] = attr['mode']
            attr['topology'] = top_id
            attr['node'] = node_id
            attr['interface'] = attr['id']
            attr['id'] = f"{top_id}-{node_id}-{attr['id']}"
            attr['modTs'] = self._format_str_dt(attr['modTs'])
            attr['ethpmAggrIf_lastLinkStChg'] = self._format_str_dt(attr['ethpmAggrIf_lastLinkStChg'])
            attr.pop('mode')

            interfaces.append(attr)
        return interfaces

    def __get_lacpInst_by_topology_and_node(self, top_id, node_id):
        response = self.apic_service.get(f"node/class/topology/pod-{top_id}/node-{node_id}/lacpInst.json").json()
        main_object = response['imdata']
        lacpInst = None
        if len(response['imdata']) > 0:
            lacpInst = response['imdata'][0]['lacpInst']['attributes']
        return lacpInst


class LoadPCInterfacesTraffic(BaseApicService):
    def __init__(self, egress_repo, ingress_error_repo, ingress_repo, apic_service):
        self.egress_repo = egress_repo
        self.ingress_error_repo = ingress_error_repo
        self.ingress_repo = ingress_repo
        self.apic_service = apic_service

    def execute(self):
        print("Carga pc_interfaces_traffic")
        fecha2 = datetime.datetime.now().replace(minute=0, second=0)
        fecha1 = fecha2 - datetime.timedelta(hours=6)
        print(f"{fecha1} - {fecha2}")

        nodes_by_topology = {'1': []}
        registros_to_insert = []
        registros_to_delete = {'eqptIngrTotalHist15min': [],'eqptIngrErrPktsHist15min': [],'eqptEgrTotalHist15min': []}
        stats_by_class = {'eqptIngrTotalHist15min': [],'eqptIngrErrPktsHist15min': [],'eqptEgrTotalHist15min': []}
        for top in list(nodes_by_topology):
            nodes_by_topology[top] = self._get_nodesid_by_topology(top)
            #nodes_by_topology[top] = [nodes_by_topology[top][0]]
            for node_id in nodes_by_topology[top]:
                pc_interfaces = self.__get_pc_interfacesid_topology_and_node(top, node_id)
                for int_id in pc_interfaces:
                    stats = self.__get_stats_by_topology_node_interface(top, node_id, int_id, fecha1, fecha2)
                    for cl in list(stats_by_class):
                        stats_by_class[cl] += stats[cl]['data']
                        if stats[cl]['min'] is not None and stats[cl]['max'] is not None:
                            registros_to_delete[cl].append({
                            'interface_id': f"{top}-{node_id}-{int_id}",
                            'fec_ini': stats[cl]['min'],
                            'fec_fin': stats[cl]['max']
                        })
                print(f"[{node_id}]: {len(pc_interfaces)}")

        stats_by_class['eqptEgrTotalHist15min'] = self._del_duplicados(stats_by_class['eqptEgrTotalHist15min'], ['interface_id','repIntvEnd'])
        stats_by_class['eqptIngrTotalHist15min'] = self._del_duplicados(stats_by_class['eqptIngrTotalHist15min'], ['interface_id','repIntvEnd'])
        stats_by_class['eqptIngrErrPktsHist15min'] = self._del_duplicados(stats_by_class['eqptIngrErrPktsHist15min'], ['interface_id','repIntvEnd'])
        
        self.egress_repo.delete_from_array_where_collectiontime_between(registros_to_delete['eqptEgrTotalHist15min'])
        self.egress_repo.insert_from_array(stats_by_class['eqptEgrTotalHist15min'])

        self.ingress_repo.delete_from_array_where_collectiontime_between(registros_to_delete['eqptIngrTotalHist15min'])
        self.ingress_repo.insert_from_array(stats_by_class['eqptIngrTotalHist15min'])

        self.ingress_error_repo.delete_from_array_where_collectiontime_between(registros_to_delete['eqptIngrErrPktsHist15min'])
        self.ingress_error_repo.insert_from_array(stats_by_class['eqptIngrErrPktsHist15min'])

    def __get_pc_interfacesid_topology_and_node(self, top_id, node_id):
        params = {
            'rsp-subtree': 'children',
            'rsp-subtree-class': 'ethpmAggrIf',
            'order-by': 'pcAggrIf.name|desc'
        }
        response = self.apic_service.get(f"node/class/topology/pod-{top_id}/node-{node_id}/pcAggrIf.json", {'params': params}).json()
        main_object = response['imdata']
        interfaces = []
        for row in response['imdata']:
            if len(row['pcAggrIf']['children']) > 0:
                children = row['pcAggrIf']['children'][0]['ethpmAggrIf']['attributes']
                interfaces.append(row['pcAggrIf']['attributes']['id'])
        return interfaces

    def __get_stats_by_topology_node_interface(self, top_id, node_id, int_id, fecha1, fecha2):
        str_fecha1 = fecha1.strftime('%Y-%m-%dT%H:%M:%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%dT%H:%M:%S')
        params = {
            'rsp-subtree-include': 'stats',
            'rsp-subtree-class': 'eqptIngrTotalHist15min,eqptIngrErrPktsHist15min,eqptEgrTotalHist15min',
            'rsp-subtree-filter': f'and(ge(eqptIngrTotalHist15min.repIntvEnd,"{str_fecha1}"), lt(eqptIngrTotalHist15min.repIntvEnd,"{str_fecha2}"))',
            'rsp-subtree-filter': f'and(ge(eqptIngrErrPktsHist15min.repIntvEnd,"{str_fecha1}"), lt(eqptIngrErrPktsHist15min.repIntvEnd,"{str_fecha2}"))',
            'rsp-subtree-filter': f'and(ge(eqptEgrTotalHist15min.repIntvEnd,"{str_fecha1}"), lt(eqptEgrTotalHist15min.repIntvEnd,"{str_fecha2}"))'
        }
        response = self.apic_service.get(f"node/mo/topology/pod-{top_id}/node-{node_id}/sys/aggr-[{int_id}].json", {'params': params}).json()
        main_obj = response['imdata'][0]['pcAggrIf']
        stats = main_obj['children'] if 'children' in list(main_obj) else []
        stats_by_class = {}
        for st_class in params['rsp-subtree-class'].split(','):
            stats_by_class[st_class] = {'data': [], 'min': None, 'max': None, 'dates': []}
        for row in stats:
            stats_class = list(row)[0]
            attr = row[stats_class]['attributes']
            repIntvEnd = attr['repIntvEnd']
            attr['repIntvEnd'] = self._format_str_dt(attr['repIntvEnd'])
            attr['repIntvStart'] = self._format_str_dt(attr['repIntvStart'])
            attr['interface_id'] = f"{top_id}-{node_id}-{int_id}"
            attr.pop('index')
            stats_by_class[stats_class]['data'].append(row[stats_class]['attributes'])
            stats_by_class[stats_class]['dates'].append(self._format_str_dt(repIntvEnd, to_format='%Y%m%d%H%M%S'))
        
        for st_class in list(stats_by_class):
            if len(stats_by_class[st_class]['data']) > 0:
                min_strdate = min(stats_by_class[st_class]['dates'])
                max_strdate = max(stats_by_class[st_class]['dates'])
                stats_by_class[st_class]['min'] = datetime.datetime.strptime(min_strdate, '%Y%m%d%H%M%S')
                stats_by_class[st_class]['max'] = datetime.datetime.strptime(max_strdate, '%Y%m%d%H%M%S')

        return stats_by_class



