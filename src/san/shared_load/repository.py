class SanConfigRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'SAN_CONFIG'
        self.sub_table = 'SAN_CONFIG_FIELD'

    def get(self):
        query = f"SELECT id, name, type, query, limit_to_commit, root_data, tablename, queue_id FROM {self.table} where status=1"
        result = self.db.fetch(query)
        data = []
        for row in result:
            data.append({'id': row[0], 'name': row[1], 'type': row[2], 'query': row[3], 'limit_to_commit': row[4], 'root_data': row[5], 'tablename': row[6], 'queue_id': row[7]})
        return data

    def find(self, id):
        query = f"SELECT id, name, type, query, limit_to_commit, root_data, tablename, queue_id FROM {self.table} WHERE ID = '{id}'"
        result = self.db.fetch(query)
        for row in result:
            return {'id': row[0], 'name': row[1], 'type': row[2], 'query': row[3], 'limit_to_commit': row[4], 'root_data': row[5], 'tablename': row[6], 'queue_id': row[7]}
        return None

    def get_fields_by_id(self, config_id):
        query = f"SELECT config_id, fieldname, nvl(fieldname, api_fieldname) as api_fieldname, lower(type) as type, map_with, to_reload, status FROM {self.sub_table} WHERE config_id = '{config_id}' and status=1"
        result = self.db.fetch(query)
        data = []
        for row in result:
            data.append({
                'config_id': row[0],
                'fieldname': row[1],
                'api_fieldname': row[2],
                'type': row[3],
                'map_with': row[4],
                'to_reload': row[5],
                'status': row[6]
            })
        return data


class ClickHouseSanConfigRepository(SanConfigRepository):
    def __init__(self, db):
        self.db = db
        self.table = 'SAN_CONFIG'
        self.sub_table = 'SAN_CONFIG_FIELD'

    def get(self):
        query = f"SELECT id, name, type, query, limit_to_commit, root_data, tablename, 'ch_'||queue_id FROM {self.table} where status=1"
        result = self.db.fetch(query)
        data = []
        for row in result:
            data.append({'id': row[0], 'name': row[1], 'type': row[2], 'query': row[3], 'limit_to_commit': row[4], 'root_data': row[5], 'tablename': row[6], 'queue_id': row[7]})
        return data

    def find(self, id):
        query = f"SELECT id, name, type, query, limit_to_commit, root_data, tablename, 'ch_'||queue_id FROM {self.table} WHERE ID = '{id}'"
        result = self.db.fetch(query)
        for row in result:
            return {'id': row[0], 'name': row[1], 'type': row[2], 'query': row[3], 'limit_to_commit': row[4], 'root_data': row[5], 'tablename': row[6], 'queue_id': row[7]}
        return None
