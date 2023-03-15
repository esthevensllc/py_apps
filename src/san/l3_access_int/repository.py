import cx_Oracle

class L3AccessInterfaceRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'SAN_L3_ACCESS_INT'
        self.config = {
            'default': {'table': 'SAN_L3_ACCESS_INT'},
            'sam_5620': {'table': 'SAM5620_L3_ACCESS_INT'},
        }
        self.use('default')

    def use(self, name):
        self.table = self.config[name]['table']
    
    def delete_all(self):
        query = f'DELETE FROM {self.table}'
        self.db.query(query)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(id, nodeId, nodeName, serviceId, serviceName, portId, portName, displayedName, l3InterfaceDescription, terminatedPortClassName, innerEncapValue, outerEncapValue, primaryIPv4Address, primaryIPv4PrefixLength, portPointer, ingressPolicyId, ingressPolicyName, egressPolicyId, egressPolicyName, operationalState, l3InterfaceAdministrativeState, administrativeState, objectFullName) VALUES (:id, :nodeId, :nodeName, :serviceId, :serviceName, :portId, :portName, :displayedName, :l3InterfaceDescription, :terminatedPortClassName, :innerEncapValue, :outerEncapValue, :primaryIPv4Address, :primaryIPv4PrefixLength, :portPointer, :ingressPolicyId, :ingressPolicyName, :egressPolicyId, :egressPolicyName, :operationalState, :l3InterfaceAdministrativeState, :administrativeState, :objectFullName)"
        bindings = {
            'id': cx_Oracle.STRING,
            'nodeId': cx_Oracle.STRING,
            'nodeName': cx_Oracle.STRING,
            'serviceId': cx_Oracle.STRING,
            'serviceName': cx_Oracle.STRING,
            'portId': cx_Oracle.STRING,
            'portName': cx_Oracle.STRING,
            'displayedName': cx_Oracle.STRING,
            'l3InterfaceDescription': cx_Oracle.STRING,
            'terminatedPortClassName': cx_Oracle.STRING,
            'innerEncapValue': cx_Oracle.STRING,
            'outerEncapValue': cx_Oracle.STRING,
            'primaryIPv4Address': cx_Oracle.STRING,
            'primaryIPv4PrefixLength': cx_Oracle.STRING,
            'portPointer': cx_Oracle.STRING,
            'ingressPolicyId': cx_Oracle.STRING,
            'ingressPolicyName': cx_Oracle.STRING,
            'egressPolicyId': cx_Oracle.STRING,
            'egressPolicyName': cx_Oracle.STRING,
            'operationalState': cx_Oracle.STRING,
            'l3InterfaceAdministrativeState': cx_Oracle.STRING,
            'administrativeState': cx_Oracle.STRING,
            #'egressPolicyName': cx_Oracle.STRING,
            'objectFullName': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)