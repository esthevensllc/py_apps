import cx_Oracle

class NetworkInterfaceRepository:
    def __init__(self, db):
        self.db = db
        self.table = ''
        self.config = {
            'default': {'table': 'SAN_NETWORK_INTERFACE'},
            'sam_5620': {'table': 'SAM5620_NETWORK_INTERFACE'},
        }
        self.use('default')

    def use(self, name):
        self.table = self.config[name]['table']
    
    def delete_all(self):
        query = f'DELETE FROM {self.table}'
        self.db.query(query)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(id, nodeId, nodeName, portId, portName, terminatedObjectId, displayedName, description, interfaceClass, primaryIPv4Address, primaryIPv4PrefixLength, terminatedPortInnerEncapValue, terminatedPortOuterEncapValue, objectFullName, operationalState, administrativeState) VALUES(:id, :nodeId, :nodeName, :portId, :portName, :terminatedObjectId, :displayedName, :description, :interfaceClass, :primaryIPv4Address, :primaryIPv4PrefixLength, :terminatedPortInnerEncapValue, :terminatedPortOuterEncapValue, :objectFullName, :operationalState, :administrativeState)"
        bindings = {
            'id': cx_Oracle.STRING,
            'nodeId': cx_Oracle.STRING,
            'nodeName': cx_Oracle.STRING,
            'portId': cx_Oracle.STRING,
            'portName': cx_Oracle.STRING,
            'terminatedObjectId': cx_Oracle.STRING,
            'displayedName': cx_Oracle.STRING,
            'description': cx_Oracle.STRING,
            'interfaceClass': cx_Oracle.STRING,
            'primaryIPv4Address': cx_Oracle.STRING,
            'primaryIPv4PrefixLength': cx_Oracle.STRING,
            'terminatedPortInnerEncapValue': cx_Oracle.STRING,
            'terminatedPortOuterEncapValue': cx_Oracle.STRING,
            'objectFullName': cx_Oracle.STRING,
            'operationalState': cx_Oracle.STRING,
            'administrativeState': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)