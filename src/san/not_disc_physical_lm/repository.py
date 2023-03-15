import cx_Oracle

class NotDiscPhysicalLMRepository:
    def __init__(self, db):
        self.db = db
        self.table = ''
        self.config = {
            'default': {'table': 'SAN_NOT_DISC_PHYSICAL_LM'},
            'sam_5620': {'table': 'SAM5620_NOT_DISC_PHYSICAL_LM'},
        }
        self.use('default')

    def use(self, name):
        self.table = self.config[name]['table']

    def delete_all(self):
        query = f'DELETE FROM {self.table}'
        self.db.query(query)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(id, displayedName, description, endpointAPointer, endpointBPointer, objectFullName) VALUES (:id, :displayedName, :description, :endpointAPointer, :endpointBPointer, :objectFullName)"
        bindings = {
            'id': cx_Oracle.STRING,
            'displayedName': cx_Oracle.STRING,
            'description': cx_Oracle.STRING,
            'endpointAPointer': cx_Oracle.STRING,
            'endpointBPointer': cx_Oracle.STRING,
            'objectFullName': cx_Oracle.STRING,
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        registros_to_insert = self.db.map_data_by_bindings(registros_to_insert, bindings, fill_data=True)
        self.db.save_from_array2(config, registros_to_insert)