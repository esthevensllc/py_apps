import cx_Oracle

class NetworkElementRepository:
    def __init__(self, db):
        self.db = db
        self.table = ''
        self.config = {
            'default': {'table': 'SAN_NETWORK_ELEMENT'},
            'sam_5620': {'table': 'SAM5620_NETWORK_ELEMENT'},
        }
        self.use('default')

    def use(self, name):
        self.table = self.config[name]['table']

    def delete_all(self):
        query = f'DELETE FROM {self.table}'
        self.db.query(query)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(id, ipAddress, chassisType, siteId, siteName, displayedName, name, location, version, descriptorVersion) VALUES (:id, :ipAddress, :chassisType, :siteId, :siteName, :displayedName, :name, :location, :version, :descriptorVersion)"
        bindings = {
            'id': cx_Oracle.STRING,
            'ipAddress': cx_Oracle.STRING,
            'chassisType': cx_Oracle.STRING,
            'siteId': cx_Oracle.STRING,
            'siteName': cx_Oracle.STRING,
            'displayedName': cx_Oracle.STRING,
            'name': cx_Oracle.STRING,
            'location': cx_Oracle.STRING,
            'version': cx_Oracle.STRING,
            'descriptorVersion': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)


class NetworkElementShelfRepository:
    def __init__(self, db):
        self.db = db
        self.table = ''
        self.config = {
            'default': {'table': 'SAN_NETWORK_ELEMENT_SHELF'},
            'sam_5620': {'table': 'SAM5620_NETWORK_ELEMENT_SHELF'},
        }
        self.use('default')

    def use(self, name):
        self.table = self.config[name]['table']

    def delete_all(self):
        query = f'DELETE FROM {self.table}'
        self.db.query(query)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(network_element_id, shelfType, shelfName, shelfId, siteId, serialNumber, manufacturerBoardNumber, equipment_CardSlot) VALUES(:network_element_id, :shelfType, :shelfName, :shelfId, :siteId, :serialNumber, :manufacturerBoardNumber, :equipment_CardSlot)"
        bindings = {
            'network_element_id': cx_Oracle.STRING,
            'shelfType': cx_Oracle.STRING,
            'shelfName': cx_Oracle.STRING,
            'shelfId': cx_Oracle.STRING,
            'siteId': cx_Oracle.STRING,
            'serialNumber': cx_Oracle.STRING,
            'manufacturerBoardNumber': cx_Oracle.STRING,
            'equipment_CardSlot': cx_Oracle.CLOB
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)
