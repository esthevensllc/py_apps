import cx_Oracle

class PlanoRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'FIJA_PLANOS_SGA'
        self.table_bup = 'FIJA_PLANOS_SGA_BUP'

    def delete_all(self):
        self.db.query(f"TRUNCATE TABLE {self.table}")

    def insert_from_array(self, registros):
        template = f"INSERT INTO {self.table}(id, nombre, geometry, fecha_insercion) VALUES (:id, :nombre, :geometry, SYSDATE)"
        bindings = {'id': cx_Oracle.STRING, 'nombre': cx_Oracle.STRING, 'geometry': cx_Oracle.CLOB}
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 10000}
        self.db.save_from_array2(config, registros)

    def insert_from_backup(self):
        self.db.query(f"INSERT INTO {self.table}(id, nombre, geometry, fecha_insercion) SELECT id, nombre, geometry, fecha_insercion FROM {self.table_bup}")

    def delete_all_backup(self):
        self.db.query(f"TRUNCATE TABLE {self.table_bup}")

    def insert_backup(self):
        self.db.query(f"INSERT INTO {self.table_bup}(id, nombre, geometry, fecha_insercion) SELECT id, nombre, geometry, sysdate FROM {self.table}")

    def exec_procedure(self, procedure, params = {}):
        self.db.callproc(procedure, params)