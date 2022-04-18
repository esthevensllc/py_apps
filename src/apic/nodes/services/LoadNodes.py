import datetime
import cx_Oracle

class LoadNodes:
    def __init__(self, repository, apic_service):
        self.repository = repository
        self.apic_service = apic_service

    def execute(self):
        nodes_by_topology = {'pod-1': ['201','202','123','124','125','126','127','128','181','182','183','184']}

        print("Inventario equipos")

        for topology in nodes_by_topology.keys():
            registros_to_insert = []
            for node_id in nodes_by_topology[topology]:
                response = self.apic_service.get(f'node/mo/topology/{topology}/node-{node_id}.json')
                response = response.json()

                attr = response['imdata'][0]['fabricNode']['attributes']
                attr['lastStateModTs'] = datetime.datetime.strptime(attr['lastStateModTs'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')
                attr['modTs'] = datetime.datetime.strptime(attr['modTs'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')
                attr['eq_uid'] = attr['uid']
                attr.pop('uid')
                registros_to_insert.append(attr)
            
            # print(registros_to_insert[0])
            self.repository.delete_by_ids(nodes_by_topology[topology])
            print("registros eliminados")
            self.repository.insert_from_array(registros_to_insert)
            print(f"Registros cargados: {len(registros_to_insert)}")