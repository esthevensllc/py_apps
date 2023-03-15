import cx_Oracle

class VPRNRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'SAN_VPRN'
        self.config = {
            'default': {'table': 'SAN_VPRN'},
            'sam_5620': {'table': 'SAM5620_VPRN'},
        }
        self.use('default')

    def use(self, name):
        self.table = self.config[name]['table']

    def delete_all(self):
        query = f'DELETE FROM {self.table}'
        self.db.query(query)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(id, displayedName, description, serviceId, subscriberId, customerName, objectFullName) VALUES (:id, :displayedName, :description, :serviceId, :subscriberId, :customerName, :objectFullName)"
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


class VprnSiteRepository:
    def __init__(self, db):
        self.db = db
        self.table = ''
        self.config = {
            'default': {'table': 'SAN_VPRN_SITE'},
            'sam_5620': {'table': 'SAM5620_VPRN_SITE'},
        }
        self.use('default')

    def use(self, name):
        self.table = self.config[name]['table']

    def delete_all(self):
        query = f'DELETE FROM {self.table}'
        self.db.query(query)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(vprn_id, displayedName, description, serviceId, serviceName, vcId, siteId, subscriberId, subscriberName, svcComponentId, routingInstanceId, objectFullName, l3fwd_ServiceSite, vprn_L3AccessInterface, vprn_RoutingInstanceSite) VALUES (:vprn_id, :displayedName, :description, :serviceId, :serviceName, :vcId, :siteId, :subscriberId, :subscriberName, :svcComponentId, :routingInstanceId, :objectFullName, :l3fwd_ServiceSite, :vprn_L3AccessInterface, :vprn_RoutingInstanceSite)"
        bindings = {
            'vprn_id': cx_Oracle.STRING,
            'displayedName': cx_Oracle.STRING,
            'description': cx_Oracle.STRING,
            'serviceId': cx_Oracle.STRING,
            'serviceName': cx_Oracle.STRING,
            'vcId': cx_Oracle.STRING,
            'siteId': cx_Oracle.STRING,
            'subscriberId': cx_Oracle.STRING,
            'subscriberName': cx_Oracle.STRING,
            'svcComponentId': cx_Oracle.STRING,
            'routingInstanceId': cx_Oracle.STRING,
            'objectFullName': cx_Oracle.STRING,
            'l3fwd_ServiceSite': cx_Oracle.CLOB,
            'vprn_L3AccessInterface': cx_Oracle.CLOB,
            'vprn_RoutingInstanceSite': cx_Oracle.CLOB
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 5000}
        self.db.save_from_array2(config, registros_to_insert)