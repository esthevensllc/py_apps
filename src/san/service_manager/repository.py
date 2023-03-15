import cx_Oracle

class ServiceManagerRepository:
    def __init__(self, db):
        self.db = db
        self.table = ''
        self.config = {
            'default': {'table': 'SAN_SERVICE_MANAGER'},
            'sam_5620': {'table': 'SAM5620_SERVICE_MANAGER'},
        }
        self.use('default')

    def use(self, name):
        self.table = self.config[name]['table']
    
    def delete_all(self):
        query = f'DELETE FROM {self.table}'
        self.db.query(query)

    def insert_from_array(self, registros_to_insert):
        template = "INSERT INTO "+self.table+"(id, displayedName, description, serviceId, subscriberId, customerName, objectFullName) VALUES (:id, :displayedName, :description, :serviceId, :subscriberId, :customerName, :objectFullName)"
        bindings = {
            'id': cx_Oracle.STRING,
            'displayedName': cx_Oracle.STRING,
            'description': cx_Oracle.STRING,
            'serviceId': cx_Oracle.STRING,
            'subscriberId': cx_Oracle.STRING,
            'customerName': cx_Oracle.STRING,
            'objectFullName': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)

    
class ServiceManagerSiteRepository:
    def __init__(self, db):
        self.db = db
        self.table = ''
        self.config = {
            'default': {'table': 'SAN_SERVICE_MANAGER_SITE'},
            'sam_5620': {'table': 'SAM5620_SERVICE_MANAGER_SITE'},
        }
        self.use('default')
    
    def use(self, name):
        self.table = self.config[name]['table']
    
    def delete_all(self):
        query = f'DELETE FROM {self.table}'
        self.db.query(query)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(service_manager_id, displayedName, description, serviceId, vcId, subscriberId, subscriberName, numberOfAccessInterfaces, name, objectFullName, svt_SpokeSdpBinding, vll_L2AccessInterface) VALUES (:service_manager_id, :displayedName, :description, :serviceId, :vcId, :subscriberId, :subscriberName, :numberOfAccessInterfaces, :name, :objectFullName, :svt_SpokeSdpBinding, :vll_L2AccessInterface)"
        bindings = {
            'service_manager_id': cx_Oracle.STRING,
            'displayedName': cx_Oracle.STRING,
            'description': cx_Oracle.STRING,
            'serviceId': cx_Oracle.STRING,
            'vcId': cx_Oracle.STRING,
            'subscriberId': cx_Oracle.STRING,
            'subscriberName': cx_Oracle.STRING,
            'numberOfAccessInterfaces': cx_Oracle.STRING,
            'name': cx_Oracle.STRING,
            'objectFullName': cx_Oracle.STRING,
            'svt_SpokeSdpBinding': cx_Oracle.STRING,
            'vll_L2AccessInterface': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)
