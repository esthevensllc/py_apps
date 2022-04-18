import cx_Oracle

class NodeRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'apic_equipo'

    def delete_by_ids(self, nodes_id):
        mapped_ids = list(map(lambda node_id: {'node_id': node_id}, nodes_id))
        template = f'delete from {self.table} where id = :node_id'
        print(template)
        bindings = {'node_id': cx_Oracle.STRING}
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100}
        self.db.save_from_array2(config, mapped_ids)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table} (id, name, nameAlias, adSt, address, annotation, apicType, childAction, delayedHeartbeat, dn, extMngdBy, fabricSt, lastStateModTs, lcOwn, modTs, model, monPolDn, nodeType, role, serial, status, eq_uid, vendor, version) VALUES (:id, :name, :nameAlias, :adSt, :address, :annotation, :apicType, :childAction, :delayedHeartbeat, :dn, :extMngdBy, :fabricSt, TO_DATE(:lastStateModTs, 'YYYY-MM-DD HH24:MI:SS'), :lcOwn, TO_DATE(:modTs, 'YYYY-MM-DD HH24:MI:SS'), :model, :monPolDn, :nodeType, :role, :serial, :status, :eq_uid, :vendor, :version)"
        bindings = {
            'id': cx_Oracle.STRING,
            'name': cx_Oracle.STRING,
            'nameAlias': cx_Oracle.STRING,
            'adSt': cx_Oracle.STRING,
            'address': cx_Oracle.STRING,
            'annotation': cx_Oracle.STRING,
            'apicType': cx_Oracle.STRING,
            'childAction': cx_Oracle.STRING,
            'delayedHeartbeat': cx_Oracle.STRING,
            'dn': cx_Oracle.STRING,
            'extMngdBy': cx_Oracle.STRING,
            'fabricSt': cx_Oracle.STRING,
            'lastStateModTs': cx_Oracle.STRING,
            'lcOwn': cx_Oracle.STRING,
            'modTs': cx_Oracle.STRING,
            'model': cx_Oracle.STRING,
            'monPolDn': cx_Oracle.STRING,
            'nodeType': cx_Oracle.STRING,
            'role': cx_Oracle.STRING,
            'serial': cx_Oracle.STRING,
            'status': cx_Oracle.STRING,
            'eq_uid': cx_Oracle.STRING,
            'vendor': cx_Oracle.STRING,
            'version': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 10000}
        self.db.save_from_array2(config, registros_to_insert)