import datetime

class LoadAllInterfaces:
    def __init__(self, repository, apic_service):
        self.repository = repository
        self.apic_service = apic_service
    
    def execute(self):
        params = {
            'query-target': 'children',
            'target-subtree-class': 'fabricNode',
            'query-target-filter': 'and(not(wcard(fabricNode.dn,"__ui_")),and(ne(fabricNode.role,"controller")))'
        }
        response = self.apic_service.get('node/mo/topology/pod-1.json', {'params': params})

        response = response.json()

        nodes = list(map(lambda row: f"{row['fabricNode']['attributes']['id']}", response['imdata']))

        print(len(nodes))

        for node in nodes:
            self.load_interfaces_for_topology_and_node(1, node)
        #nodes = map(lambda row: row.keys(), response['imdata'])
        print(nodes)

    def load_interfaces_for_topology_and_node(self, topology_id, node_id):
        params = {
            'rsp-subtree': 'children',
            'rsp-subtree-class': 'ethpmPhysIf',
            #'subscription': 'yes',
            'order-by': 'l1PhysIf.monPolDn|asc'
        }
        response = self.apic_service.get(f'node/class/topology/pod-{topology_id}/node-{node_id}/l1PhysIf.json', {'params': params})
        response = response.json()

        registros_to_insert = []
        for row in response['imdata']:
            attributes = row['l1PhysIf']['attributes']
            children = {}
            for cld in row['l1PhysIf']['children']:
                children_to_loop = cld['ethpmPhysIf']['attributes']
                for attr in children_to_loop.keys():
                    children[f"ethpmPhysIf_{attr}"] = children_to_loop[attr]

            to_add = dict(attributes, **children)
            to_add['interface'] = to_add['id']
            to_add['id'] = f"{topology_id}-{node_id}-{to_add['id']}"
            to_add['node'] = node_id
            to_add['int_mode'] = to_add['mode']
            to_add['modTs'] = datetime.datetime.strptime(to_add['modTs'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')
            to_add['ethpmPhysIf_lastLinkStChg'] = datetime.datetime.strptime(to_add['ethpmPhysIf_lastLinkStChg'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')
            to_add.pop('mode')
            registros_to_insert.append(to_add)
        self.repository.delete_by_node(node_id)
        self.repository.insert_from_array(registros_to_insert)
        print(f"[{node_id}]: {len(registros_to_insert)}")
