import cx_Oracle

class LagInterfaceRepository:
    def __init__(self, db):
        self.db = db
        self.table = ''
        self.temp_table = ''
        self.config = {
            'default': {'table': 'SAN_LAG_INTERFACE'},
            'sam_5620': {'table': 'SAM5620_LAG_INTERFACE'},
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
                A.LAGID = B.LAGID,
                A.SNMPPORTID = B.SNMPPORTID,
                A.DESCRIPTION = B.DESCRIPTION,
                A.SITEID = B.SITEID,
                A.SITENAME = B.SITENAME,
                A.SHELFID = B.SHELFID,
                A.DISPLAYEDNAME = B.DISPLAYEDNAME,
                A.OPERATIONALSTATE = B.OPERATIONALSTATE,
                A.ADMINISTRATIVESTATE = B.ADMINISTRATIVESTATE,
                A.FECHA_ACTUALIZACION = TRUNC(SYSDATE, 'DD'),
                A.ESTADO_SEG = 1
            WHEN NOT MATCHED THEN INSERT (lagId, snmpPortId, description, siteId, siteName, shelfId, displayedName, operationalState, administrativeState, objectFullName, fecha_insercion, estado_seg)
                VALUES(b.lagId, b.snmpPortId, b.description, b.siteId, b.siteName, b.shelfId, b.displayedName, b.operationalState, b.administrativeState, b.objectFullName, TRUNC(SYSDATE, 'DD'), 1);
            COMMIT;
        END;"""
        self.db.query(query)

    def load_temp_table(self, registros_to_insert):
        query = f'DELETE FROM {self.temp_table}'
        self.db.query(query)

        template = f"INSERT INTO {self.temp_table}(lagId, snmpPortId, description, siteId, siteName, shelfId, displayedName, operationalState, administrativeState, objectFullName) VALUES (:lagId, :snmpPortId, :description, :siteId, :siteName, :shelfId, :displayedName, :operationalState, :administrativeState, :objectFullName)"
        bindings = {
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
        self.temp_table = ''
        self.config = {
            'default': {'table': 'SAN_LAG_INTERFACE_PORT'},
            'sam_5620': {'table': 'SAM5620_LAG_INTERFACE_PORT'},
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
            ON (A.interface_id = B.interface_id AND A.objectFullName = B.objectFullName)
            WHEN MATCHED THEN UPDATE SET
                A.NODEID = B.NODEID,
                A.NODENAME = B.NODENAME,
                A.LAGID = B.LAGID,
                A.PORTID = B.PORTID,
                A.DESCRIPTION = B.DESCRIPTION,
                A.MEMBERNAME = B.MEMBERNAME,
                A.PORTPOINTER = B.PORTPOINTER,
                A.SHELFID = B.SHELFID,
                A.FECHA_ACTUALIZACION = TRUNC(SYSDATE, 'DD'),
                A.ESTADO_SEG = 1
            WHEN NOT MATCHED THEN INSERT (interface_id, nodeId, nodeName, lagId, portId, description, memberName, portPointer, shelfId, objectFullName, fecha_insercion, estado_seg)
                VALUES(b.interface_id, b.nodeId, b.nodeName, b.lagId, b.portId, b.description, b.memberName, b.portPointer, b.shelfId, b.objectFullName, TRUNC(SYSDATE, 'DD'), 1);
            COMMIT;
        END;"""
        self.db.query(query)

    def load_temp_table(self, registros_to_insert):
        query = f'DELETE FROM {self.temp_table}'
        self.db.query(query)

        template = f"INSERT INTO {self.temp_table}(interface_id, nodeId, nodeName, lagId, portId, description, memberName, portPointer, shelfId, objectFullName) VALUES (:interface_id, :nodeId, :nodeName, :lagId, :portId, :description, :memberName, :portPointer, :shelfId, :objectFullName)"
        bindings = {
            'interface_id': cx_Oracle.STRING,
            'nodeId': cx_Oracle.STRING,
            'nodeName': cx_Oracle.STRING,
            'lagId': cx_Oracle.STRING,
            'portId': cx_Oracle.STRING,
            'description': cx_Oracle.STRING,
            'memberName': cx_Oracle.STRING,
            'portPointer': cx_Oracle.STRING,
            'shelfId': cx_Oracle.STRING,
            'objectFullName': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)