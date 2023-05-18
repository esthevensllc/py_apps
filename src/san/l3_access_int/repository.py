import cx_Oracle

class L3AccessInterfaceRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'SAN_L3_ACCESS_INT'
        self.temp_table = ''
        self.config = {
            'default': {'table': 'SAN_L3_ACCESS_INT'},
            'sam_5620': {'table': 'SAM5620_L3_ACCESS_INT'},
        }
        self.use('default')

    def use(self, name):
        self.table = self.config[name]['table']
        self.temp_table = f"{self.table}_TEMP"
    
    def merge_table(self):
        query = query = f"""BEGIN
            UPDATE {self.table} SET ESTADO_SEG = 0;
            COMMIT;

            MERGE INTO {self.table} A
            USING (
                SELECT * FROM {self.temp_table}
            ) B
            ON (
                A.OBJECTFULLNAME = B.OBJECTFULLNAME
            )
            WHEN MATCHED THEN UPDATE SET
                A.ID = B.ID,
                A.NODEID = B.NODEID,
                A.NODENAME = B.NODENAME,
                A.SERVICEID = B.SERVICEID,
                A.SERVICENAME = B.SERVICENAME,
                A.PORTID = B.PORTID,
                A.PORTNAME = B.PORTNAME,
                A.DISPLAYEDNAME = B.DISPLAYEDNAME,
                A.L3INTERFACEDESCRIPTION = B.L3INTERFACEDESCRIPTION,
                A.TERMINATEDPORTCLASSNAME = B.TERMINATEDPORTCLASSNAME,
                A.INNERENCAPVALUE = B.INNERENCAPVALUE,
                A.OUTERENCAPVALUE = B.OUTERENCAPVALUE,
                A.PRIMARYIPV4ADDRESS = B.PRIMARYIPV4ADDRESS,
                A.PRIMARYIPV4PREFIXLENGTH = B.PRIMARYIPV4PREFIXLENGTH,
                A.PORTPOINTER = B.PORTPOINTER,
                A.INGRESSPOLICYID = B.INGRESSPOLICYID,
                A.INGRESSPOLICYNAME = B.INGRESSPOLICYNAME,
                A.EGRESSPOLICYID = B.EGRESSPOLICYID,
                A.EGRESSPOLICYNAME = B.EGRESSPOLICYNAME,
                A.OPERATIONALSTATE = B.OPERATIONALSTATE,
                A.L3INTERFACEADMINISTRATIVESTATE = B.L3INTERFACEADMINISTRATIVESTATE,
                A.ADMINISTRATIVESTATE = B.ADMINISTRATIVESTATE,
                A.FECHA_ACTUALIZACION = TRUNC(SYSDATE, 'DD'),
                A.ESTADO_SEG = 1
            WHEN NOT MATCHED THEN INSERT(id, nodeId, nodeName, serviceId, serviceName, portId, portName, displayedName, l3InterfaceDescription, terminatedPortClassName, innerEncapValue, outerEncapValue, primaryIPv4Address, primaryIPv4PrefixLength, portPointer, ingressPolicyId, ingressPolicyName, egressPolicyId, egressPolicyName, operationalState, l3InterfaceAdministrativeState, administrativeState, objectFullName, fecha_insercion, estado_seg)
                VALUES(b.id, b.nodeId, b.nodeName, b.serviceId, b.serviceName, b.portId, b.portName, b.displayedName, b.l3InterfaceDescription, b.terminatedPortClassName, b.innerEncapValue, b.outerEncapValue, b.primaryIPv4Address, b.primaryIPv4PrefixLength, b.portPointer, b.ingressPolicyId, b.ingressPolicyName, b.egressPolicyId, b.egressPolicyName, b.operationalState, b.l3InterfaceAdministrativeState, b.administrativeState, b.objectFullName, TRUNC(SYSDATE, 'DD'), 1);
            COMMIT;
        END;"""
        self.db.query(query)

    def load_temp_table(self, registros_to_insert):
        query = f'DELETE FROM {self.temp_table}'
        self.db.query(query)

        template = f"INSERT INTO {self.temp_table}(id, nodeId, nodeName, serviceId, serviceName, portId, portName, displayedName, l3InterfaceDescription, terminatedPortClassName, innerEncapValue, outerEncapValue, primaryIPv4Address, primaryIPv4PrefixLength, portPointer, ingressPolicyId, ingressPolicyName, egressPolicyId, egressPolicyName, operationalState, l3InterfaceAdministrativeState, administrativeState, objectFullName) VALUES (:id, :nodeId, :nodeName, :serviceId, :serviceName, :portId, :portName, :displayedName, :l3InterfaceDescription, :terminatedPortClassName, :innerEncapValue, :outerEncapValue, :primaryIPv4Address, :primaryIPv4PrefixLength, :portPointer, :ingressPolicyId, :ingressPolicyName, :egressPolicyId, :egressPolicyName, :operationalState, :l3InterfaceAdministrativeState, :administrativeState, :objectFullName)"
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