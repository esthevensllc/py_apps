import cx_Oracle

class ManagedObjectRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'arbor_managed_object'

    def delete_all(self):
        sql = "TRUNCATE TABLE "+self.table
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        template = "INSERT INTO "+self.table+"(ID, DESCRIPTION, FAMILY, NAME, TAGS) VALUES (:id, :description, :family, :name, :tags)"
        bindings = {'id': cx_Oracle.STRING, 'description': cx_Oracle.STRING, 'family': cx_Oracle.STRING, 'name': cx_Oracle.STRING, 'tags': cx_Oracle.STRING}
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 1000}
        self.db.save_from_array2(config, registros_to_insert)