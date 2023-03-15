import cx_Oracle

class MedHuawei2ConfigRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'MED_HUAWEI2_CONFIG'
        self.sub_table = 'MED_HUAWEI2_CONFIG_FIELD'

    def _map_result(self, result):
        data = []
        for row in result:
            data.append({'id': row[0], 'name': row[1], 'type': row[2], 'query': row[3], 'limit_to_commit': row[4], 'root_data': row[5], 'tablename': row[6], 'queue_id': row[7]})
        return data

    def get(self):
        query = f"SELECT id, name, type, query, limit_to_commit, root_data, tablename, queue_id FROM {self.table} WHERE status=1 order by n_order"
        result = self.db.fetch(query)
        data = self._map_result(result)
        return data

    def get_by_group(self, group):
        str_groups = "','".join(group)
        query = f"""SELECT id, name, type, query, limit_to_commit, root_data, tablename, queue_id FROM {self.table}
        WHERE status=1 and m_group in ('{str_groups}') order by n_order"""
        result = self.db.fetch(query)
        data = self._map_result(result)
        return data

    def find(self, id):
        query = f"SELECT id, name, type, query, limit_to_commit, root_data, tablename, queue_id FROM {self.table} WHERE ID = '{id}'"
        result = self.db.fetch(query)
        data = self._map_result(result)
        if len(data) > 0:
            return data[0]
        return None

    def get_fields_by_id(self, config_id):
        query = f"SELECT config_id, fieldname, nvl(src_fieldname, fieldname) as src_fieldname, lower(type) as type, map_with, to_reload, status FROM {self.sub_table} WHERE config_id = '{config_id}' and status=1"
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
                'status': row[6]
            })
        return data

class SharedRepository:
    def __init__(self, db):
        self.db = db

    def delete_where_collectiontime_between(self, table, date_field, fecha1, fecha2):
        fecha1_str = fecha1.strftime('%Y%m%d%H%M%S')
        fecha2_str = fecha2.strftime('%Y%m%d%H%M%S')
        sql = f"DELETE FROM {table} WHERE {date_field}>=TO_DATE('{fecha1_str}', 'YYYYMMDDHH24MISS') and {date_field}<TO_DATE('{fecha2_str}', 'YYYYMMDDHH24MISS')"
        self.db.query(sql)
    
    def insert_from_array(self, template, bindings, registros_to_insert):
        registros_to_insert = self.db.map_data_by_bindings(registros_to_insert, bindings, {}, True)
        #print(registros_to_insert[1031])
        config = {'template': template, 'bindings': bindings.copy(), 'row_type': 'object', 'limit_to_commit': 10000}
        self.db.save_from_array2(config, registros_to_insert)