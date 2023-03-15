import json

class ReloadManagedObject:
    def __init__(self, repository, arbor_api):
        self.repository = repository
        self.arbor_api = arbor_api

    def execute(self):
        print('Recarga arbor_os.managed_object')
        #managed_obj_resp = self.managed_object_api.get({'params': {'perPage': 2000}})
        managed_obj_resp = self.arbor_api.get('api/sp/traffic_query_facet_values/managed_objects/?perPage=2000')
        managed_obj_resp = managed_obj_resp.json()

        registros_to_insert = []
        for row in managed_obj_resp['data']:
            row_to_add = {
                'id': row['id'],
                'description': row['attributes']['description'] if 'description' in row['attributes'].keys() else None,
                'family': row['attributes']['family'],
                'name': row['attributes']['name'],
                'tags': json.dumps(row['attributes']['tags'] if 'tags' in row['attributes'].keys() else None)
            }
            registros_to_insert.append(row_to_add)
        
        self.repository.delete_all()
        self.repository.insert_from_array(registros_to_insert)
        print('Registros insertados: {}'.format(len(registros_to_insert)))