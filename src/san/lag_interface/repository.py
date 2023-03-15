import cx_Oracle

class LagInterfaceRepository:
    def __init__(self, db):
        self.db = db
        self.table = ''
        self.config = {
            'default': {'table': 'SAN_LAG_INTERFACE'},
            'sam_5620': {'table': 'SAM5620_LAG_INTERFACE'},
        }
        self.use('default')

    def use(self, name):
        self.table = self.config[name]['table']
    
    def delete_all(self):
        query = f'DELETE FROM {self.table}'
        self.db.query(query)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(id, lagId, snmpPortId, description, siteId, siteName, shelfId, displayedName, operationalState, administrativeState, objectFullName) VALUES (:id, :lagId, :snmpPortId, :description, :siteId, :siteName, :shelfId, :displayedName, :operationalState, :administrativeState, :objectFullName)"
        bindings = {
            'id': cx_Oracle.STRING,
            'lagId': cx_Oracle.STRING,
            'snmpPortId': cx_Oracle.STRING,
            'description': cx_Oracle.STRING,
            'siteId': cx_Oracle.STRING,
            'siteName': cx_Oracle.STRING,
            'shelfId': cx_Oracle.STRING,
            'displayedName': cx_Oracle.STRING,
            'operationalState': cx_Oracle.STRING,
            'administrativeState': cx_Oracle.STRING,
            'objectFullName': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)


class LagInterfacePortRepository:
    def __init__(self, db):
        self.db = db
        self.table = ''
        self.config = {
            'default': {'table': 'SAN_LAG_INTERFACE_PORT'},
            'sam_5620': {'table': 'SAM5620_LAG_INTERFACE_PORT'},
        }
        self.use('default')

    def use(self, name):
        self.table = self.config[name]['table']
    
    def delete_all(self):
        query = f'DELETE FROM {self.table}'
        self.db.query(query)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(interface_id, nodeId, nodeName, lagId, portId, description, memberName, portPointer, shelfId) VALUES (:interface_id, :nodeId, :nodeName, :lagId, :portId, :description, :memberName, :portPointer, :shelfId)"
        bindings = {
            'interface_id': cx_Oracle.STRING,
            'nodeId': cx_Oracle.STRING,
            'nodeName': cx_Oracle.STRING,
            'lagId': cx_Oracle.STRING,
            'portId': cx_Oracle.STRING,
            'description': cx_Oracle.STRING,
            'memberName': cx_Oracle.STRING,
            'portPointer': cx_Oracle.STRING,
            'shelfId': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)