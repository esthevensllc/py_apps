from src.apic.shared.services import BaseApicService

class LoadVPCInterfaces(BaseApicService):
    def __init__(self, repository, interface_repo, apic_service):
        self.repository = repository
        self.interface_repo = interface_repo
        self.apic_service = apic_service

    def execute(self):
        print("apic.vpc_interfaces")
        nodes_by_topology = {'1': []}
        to_template = None
        registros_to_insert = []
        interfaces = []
        for top in list(nodes_by_topology):
            nodes_by_topology[top] = self._get_nodesid_by_topology(top)
            for node_id in nodes_by_topology[top]:
                vpc_domains = self.__get_vpc_domains_by_topology_and_node(top, node_id)
                for row in vpc_domains:
                    interfaces_of_dom = self.__get_vpc_interfaces_by_topology_and_node(top, node_id, row['domain'])
                    interfaces = interfaces + interfaces_of_dom
                    self.interface_repo.delete_by_topology_node_domain(top, node_id, row['domain'])
                registros_to_insert = registros_to_insert + vpc_domains
                self.repository.delete_by_topology_and_node(top, node_id)

        self.repository.insert_from_array(registros_to_insert)
        self.interface_repo.insert_from_array(interfaces)

        print(f"domains: {len(registros_to_insert)}")
        print(f"interfaces: {len(interfaces)}")
        
        """
        template, bindings, table_temp = self._make_template_load('APIC_VPC_INTERFACE', interfaces[0], [])
        print(template)
        print('')
        print(bindings)
        print('')
        print(table_temp)
        """

    def __get_vpc_domains_by_topology_and_node(self, top_id, node_id):
        response = self.apic_service.get(f"node/class/topology/pod-{top_id}/node-{node_id}/vpcDom.json").json()        
        vpcDom_list = []
        for row in response['imdata']:
            row_to_add = row['vpcDom']['attributes']
            row_to_add['modTs'] = self._format_str_dt(row_to_add['modTs'])
            row_to_add['splitBrainTimerStartTime'] = self._format_str_dt(row_to_add['splitBrainTimerStartTime'])
            row_to_add['tryRoleEstabTimerStartTime'] = self._format_str_dt(row_to_add['tryRoleEstabTimerStartTime'])
            row_to_add['topology'] = top_id
            row_to_add['node'] = node_id
            row_to_add['domain'] = row_to_add['id']
            row_to_add['id'] = f"{top_id}-{node_id}-{row_to_add['id']}"
            vpcDom_list.append(row_to_add)
        return vpcDom_list

    def __get_vpc_interfaces_by_topology_and_node(self, top_id, node_id, dom_id):
        params = {
            'query-target': 'children',
            'target-subtree-class': 'vpcIf',
            'query-target-filter': 'not(wcard(vpcIf.dn,"__ui_"))'
        }
        response = self.apic_service.get(f"node/mo/topology/pod-{top_id}/node-{node_id}/sys/vpc/inst/dom-{dom_id}.json", {'params': params}).json()
        vpcIf_list = []
        for row in response['imdata']:
            row_to_add = row['vpcIf']['attributes']
            row_to_add['modTs'] = self._format_str_dt(row_to_add['modTs'])
            row_to_add['topology'] = top_id
            row_to_add['node'] = node_id
            row_to_add['domain'] = dom_id
            row_to_add['interface'] = row_to_add['id']
            row_to_add['id'] = f"{top_id}-{node_id}-{dom_id}-{row_to_add['id']}"
            vpcIf_list.append(row_to_add)
        return vpcIf_list
