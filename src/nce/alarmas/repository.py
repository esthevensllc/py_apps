import re

class NCEConfigRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'NCE_CONFIG'
        self.fields = 'id, name, type, server_id, work_dir, file_pattern, file_date_format, limit_to_commit, tablename, queue_id, status, reload_by, exec_after_by, exec_after_st'
        self.sub_table = 'NCE_CONFIG_FIELD'

    def get(self):
        sql = f"SELECT {self.fields} from {self.table} where status=1"
        result = self.db.fetch(sql)
        data = self._map_result(result)
        return data

    def get_by_group_id(self, group_id):
        sql = f"SELECT {self.fields} from {self.table} where status=1 and group_id='{group_id}'"
        result = self.db.fetch(sql)
        data = self._map_result(result)
        return data

    def find(self, id):
        sql = f"SELECT {self.fields} from {self.table} where id='{id}'"
        result = self.db.fetch(sql)
        data = self._map_result(result)
        if len(data) > 0:
            return data[0]
        return None

    def _map_result(self, result):
        data = []
        for row in result:
            data.append({
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'server_id': row[3],
                'work_dir': row[4],
                'file_pattern': row[5],
                'file_date_format': row[6],
                'limit_to_commit': row[7],
                'tablename': row[8],
                'queue_id': row[9],
                'status': row[10],
                'reload_by': row[11],
                'exec_after_by': row[12],
                'exec_after_st': row[13]
            })
        return data
    
    def get_fields_by_id(self, config_id):
        query = f"""SELECT
        config_id, fieldname, nvl(src_fieldname, fieldname) as src_fieldname, lower(type) as type, map_with, to_reload, status, reload_argument
        FROM {self.sub_table} WHERE config_id = '{config_id}' and status=1"""
        result = self.db.fetch(query)
        data = []
        for row in result:
            data.append({
                'config_id': row[0],
                'fieldname': row[1],
                'src_fieldname': row[2],
                'type': row[3],
                'map_with': row[4],
                'to_reload': row[5],
                'status': row[6],
                'reload_argument': row[7]
            })
        return data
