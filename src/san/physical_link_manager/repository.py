import cx_Oracle

class SANPhysicalLMRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'SAN_PHYSICAL_LM'
        self.config = {
            'default': {'table': 'SAN_PHYSICAL_LM'},
            'sam_5620': {'table': 'SAM5620_PHYSICAL_LM'},
        }
    def use(self, name):
        self.table = self.config[name]['table']
    
    def delete_all(self):
        query = f'DELETE FROM {self.table}'
        self.db.query(query)

    def insert_from_array(self, registros_to_insert):
        template = "INSERT INTO "+self.table+"(displayedName, description, endPointAPortId, endPointBPortId, usesManagedEndpointA, endpointAPointer, endpointBPointer, endPointASiteId, endPointBSiteId, endPointAType, endPointBType, usesManagedEndpointB, objectFullName) VALUES (:displayedName, :description, :endPointAPortId, :endPointBPortId, :usesManagedEndpointA, :endpointAPointer, :endpointBPointer, :endPointASiteId, :endPointBSiteId, :endPointAType, :endPointBType, :usesManagedEndpointB, :objectFullName)"
        bindings = {
            'displayedName': cx_Oracle.STRING,
            'description': cx_Oracle.STRING,
            'endPointAPortId': cx_Oracle.STRING,
            'endPointBPortId': cx_Oracle.STRING,
            'usesManagedEndpointA': cx_Oracle.STRING,
            'endpointAPointer': cx_Oracle.STRING,
            'endpointBPointer': cx_Oracle.STRING,
            'endPointASiteId': cx_Oracle.STRING,
            'endPointBSiteId': cx_Oracle.STRING,
            'endPointAType': cx_Oracle.STRING,
            'endPointBType': cx_Oracle.STRING,
            'usesManagedEndpointB': cx_Oracle.STRING,
            'objectFullName': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)