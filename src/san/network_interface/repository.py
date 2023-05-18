import cx_Oracle

class NetworkInterfaceRepository:
    def __init__(self, db):
        self.db = db
        self.table = ''
        self.temp_table = ''
        self.config = {
            'default': {'table': 'SAN_NETWORK_INTERFACE'},
            'sam_5620': {'table': 'SAM5620_NETWORK_INTERFACE'},
        }
        self.use('default')

    def use(self, name):
        self.table = self.config[name]['table']
        self.temp_table = f"{self.table}_TEMP"
    
    def merge_table(self):
        query = f"""BEGIN
            UPDATE {self.table} SET ESTADO_SEG = 0;
            COMMIT;

            MERGE INTO {self.table} A
            USING (
                SELECT * FROM {self.temp_table}
            ) B
            ON (A.OBJECTFULLNAME = B.OBJECTFULLNAME)
            WHEN MATCHED THEN UPDATE SET
                A.ID = B.ID,
                A.NODEID = B.NODEID,
                A.NODENAME = B.NODENAME,
                A.PORTID = B.PORTID,
                A.PORTNAME = B.PORTNAME,
                A.TERMINATEDOBJECTID = B.TERMINATEDOBJECTID,
                A.DISPLAYEDNAME = B.DISPLAYEDNAME,
                A.DESCRIPTION = B.DESCRIPTION,
                A.INTERFACECLASS = B.INTERFACECLASS,
                A.PRIMARYIPV4ADDRESS = B.PRIMARYIPV4ADDRESS,
                A.PRIMARYIPV4PREFIXLENGTH = B.PRIMARYIPV4PREFIXLENGTH,
                A.TERMINATEDPORTINNERENCAPVALUE = B.TERMINATEDPORTINNERENCAPVALUE,
                A.TERMINATEDPORTOUTERENCAPVALUE = B.TERMINATEDPORTOUTERENCAPVALUE,
                A.OPERATIONALSTATE = B.OPERATIONALSTATE,
                A.ADMINISTRATIVESTATE = B.ADMINISTRATIVESTATE,
                A.FECHA_ACTUALIZACION = TRUNC(SYSDATE, 'DD'),
                A.ESTADO_SEG = 1
            WHEN NOT MATCHED THEN INSERT(id, nodeId, nodeName, portId, portName, terminatedObjectId, displayedName, description, interfaceClass, primaryIPv4Address, primaryIPv4PrefixLength, terminatedPortInnerEncapValue, terminatedPortOuterEncapValue, objectFullName, operationalState, administrativeState, fecha_insercion, estado_seg)
                VALUES(b.id, b.nodeId, b.nodeName, b.portId, b.portName, b.terminatedObjectId, b.displayedName, b.description, b.interfaceClass, b.primaryIPv4Address, b.primaryIPv4PrefixLength, b.terminatedPortInnerEncapValue, b.terminatedPortOuterEncapValue, b.objectFullName, b.operationalState, b.administrativeState, TRUNC(SYSDATE, 'DD'), 1);
            COMMIT;
        END;"""
        self.db.query(query)

    def load_temp_table(self, registros_to_insert):
        query = f'DELETE FROM {self.temp_table}'
        self.db.query(query)

        template = f"INSERT INTO {self.temp_table}(id, nodeId, nodeName, portId, portName, terminatedObjectId, displayedName, description, interfaceClass, primaryIPv4Address, primaryIPv4PrefixLength, terminatedPortInnerEncapValue, terminatedPortOuterEncapValue, objectFullName, operationalState, administrativeState) VALUES(:id, :nodeId, :nodeName, :portId, :portName, :terminatedObjectId, :displayedName, :description, :interfaceClass, :primaryIPv4Address, :primaryIPv4PrefixLength, :terminatedPortInnerEncapValue, :terminatedPortOuterEncapValue, :objectFullName, :operationalState, :administrativeState)"
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