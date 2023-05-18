import cx_Oracle

class NetworkElementRepository:
    def __init__(self, db):
        self.db = db
        self.table = ''
        self.temp_table = ''
        self.config = {
            'default': {'table': 'SAN_NETWORK_ELEMENT'},
            'sam_5620': {'table': 'SAM5620_NETWORK_ELEMENT'},
        }
        self.use('default')

    def use(self, name):
        self.table = self.config[name]['table']
        self.temp_table = f"{self.table}_temp"

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
                A.IPADDRESS = B.IPADDRESS,
                A.CHASSISTYPE = B.CHASSISTYPE,
                A.SITEID = B.SITEID,
                A.SITENAME = B.SITENAME,
                A.DISPLAYEDNAME = B.DISPLAYEDNAME,
                A.NAME = B.NAME,
                A.LOCATION = B.LOCATION,
                A.VERSION = B.VERSION,
                A.DESCRIPTORVERSION = B.DESCRIPTORVERSION,
                A.FECHA_ACTUALIZACION = TRUNC(SYSDATE, 'DD'),
                A.ESTADO_SEG = 1
            WHEN NOT MATCHED THEN INSERT(id, ipAddress, chassisType, siteId, siteName,
            displayedName, name, location, version, descriptorVersion, objectFullName, fecha_insercion, estado_seg)
                VALUES(b.id, b.ipAddress, b.chassisType, b.siteId, b.siteName,
                b.displayedName, b.name, b.location, b.version, b.descriptorVersion, b.objectFullName, TRUNC(SYSDATE, 'DD'), 1);
            COMMIT;
        END;"""
        self.db.query(query)

    def load_temp_table(self, registros_to_insert):
        print(registros_to_insert[0])
        query = f'DELETE FROM {self.temp_table}'
        self.db.query(query)

        template = f"INSERT INTO {self.temp_table}(ipAddress, chassisType, siteId, siteName, displayedName, name, location, version, descriptorVersion, objectFullName) VALUES (:ipAddress, :chassisType, :siteId, :siteName, :displayedName, :name, :location, :version, :descriptorVersion, :objectFullName)"
        bindings = {
            # 'id': cx_Oracle.STRING,
            'ipAddress': cx_Oracle.STRING,
            'chassisType': cx_Oracle.STRING,
            'siteId': cx_Oracle.STRING,
            'siteName': cx_Oracle.STRING,
            'displayedName': cx_Oracle.STRING,
            'name': cx_Oracle.STRING,
            'location': cx_Oracle.STRING,
            'version': cx_Oracle.STRING,
            'descriptorVersion': cx_Oracle.STRING,
            'objectFullName': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 5000}
        self.db.save_from_array2(config, registros_to_insert)


class NetworkElementShelfRepository:
    def __init__(self, db):
        self.db = db
        self.table = ''
        self.temp_table = ''
        self.config = {
            'default': {'table': 'SAN_NETWORK_ELEMENT_SHELF'},
            'sam_5620': {'table': 'SAM5620_NETWORK_ELEMENT_SHELF'},
        }
        self.use('default')

    def use(self, name):
        self.table = self.config[name]['table']
        self.temp_table = f"{self.table}_temp"

    def merge_table(self):
        query = f"""BEGIN
            UPDATE {self.table} SET ESTADO_SEG = 0;
            COMMIT;

            MERGE INTO {self.table} A
            USING (
                SELECT * FROM {self.temp_table}
            ) B
            ON (
                A.network_element_id = B.network_element_id AND
                A.objectFullName = B.objectFullName
            )
            WHEN MATCHED THEN UPDATE SET
                A.SHELFTYPE = B.SHELFTYPE,
                A.SHELFNAME = B.SHELFNAME,
                A.SHELFID = B.SHELFID,
                A.SITEID = B.SITEID,
                A.SERIALNUMBER = B.SERIALNUMBER,
                A.MANUFACTURERBOARDNUMBER = B.MANUFACTURERBOARDNUMBER,
                A.EQUIPMENT_CARDSLOT = B.EQUIPMENT_CARDSLOT,
                A.FECHA_ACTUALIZACION = TRUNC(SYSDATE, 'DD'),
                A.ESTADO_SEG = 1
            WHEN NOT MATCHED THEN INSERT(network_element_id, shelfType, shelfName, shelfId, siteId,
            serialNumber, manufacturerBoardNumber, equipment_CardSlot, objectFullName, fecha_insercion, estado_seg)
                VALUES(b.network_element_id, b.shelfType, b.shelfName, b.shelfId, b.siteId,
                b.serialNumber, b.manufacturerBoardNumber, b.equipment_CardSlot, b.objectFullName, TRUNC(SYSDATE, 'DD'), 1);
            COMMIT;
        END;"""
        self.db.query(query)

    def load_temp_table(self, registros_to_insert):
        query = f'DELETE FROM {self.temp_table}'
        self.db.query(query)

        template = f"INSERT INTO {self.temp_table}(network_element_id, shelfType, shelfName, shelfId, siteId, serialNumber, manufacturerBoardNumber, equipment_CardSlot, objectFullName) VALUES(:network_element_id, :shelfType, :shelfName, :shelfId, :siteId, :serialNumber, :manufacturerBoardNumber, :equipment_CardSlot, :objectFullName)"
        bindings = {
            'network_element_id': cx_Oracle.STRING,
            'shelfType': cx_Oracle.STRING,
            'shelfName': cx_Oracle.STRING,
            'shelfId': cx_Oracle.STRING,
            'siteId': cx_Oracle.STRING,
            'serialNumber': cx_Oracle.STRING,
            'manufacturerBoardNumber': cx_Oracle.STRING,
            'equipment_CardSlot': cx_Oracle.CLOB,
            'objectFullName': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 5000}
        self.db.save_from_array2(config, registros_to_insert)
