import cx_Oracle

class VPRNRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'SAN_VPRN'
        self.temp_table = ''
        self.config = {
            'default': {'table': 'SAN_VPRN'},
            'sam_5620': {'table': 'SAM5620_VPRN'},
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
                A.DISPLAYEDNAME = B.DISPLAYEDNAME,
                A.DESCRIPTION = B.DESCRIPTION,
                A.SERVICEID = B.SERVICEID,
                A.SUBSCRIBERID = B.SUBSCRIBERID,
                A.CUSTOMERNAME = B.CUSTOMERNAME,
                A.FECHA_ACTUALIZACION = TRUNC(SYSDATE, 'DD'),
                A.ESTADO_SEG = 1
            WHEN NOT MATCHED THEN INSERT (id, displayedName, description, serviceId, subscriberId, customerName, objectFullName, fecha_insercion, estado_seg)
                VALUES(b.id, b.displayedName, b.description, b.serviceId, b.subscriberId, b.customerName, b.objectFullName, TRUNC(SYSDATE, 'DD'), 1);
            COMMIT;
        END;"""
        self.db.query(query)

    def load_temp_table(self, registros_to_insert):
        query = f'DELETE FROM {self.temp_table}'
        self.db.query(query)

        template = f"INSERT INTO {self.temp_table}(id, displayedName, description, serviceId, subscriberId, customerName, objectFullName) VALUES (:id, :displayedName, :description, :serviceId, :subscriberId, :customerName, :objectFullName)"
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
        self.temp_table = ''
        self.config = {
            'default': {'table': 'SAN_VPRN_SITE'},
            'sam_5620': {'table': 'SAM5620_VPRN_SITE'},
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
            ON (A.vprn_id = B.vprn_id AND A.OBJECTFULLNAME = B.OBJECTFULLNAME)
            WHEN MATCHED THEN UPDATE SET
                A.DISPLAYEDNAME = B.DISPLAYEDNAME,
                A.DESCRIPTION = B.DESCRIPTION,
                A.SERVICEID = B.SERVICEID,
                A.SERVICENAME = B.SERVICENAME,
                A.VCID = B.VCID,
                A.SITEID = B.SITEID,
                A.SUBSCRIBERID = B.SUBSCRIBERID,
                A.SUBSCRIBERNAME = B.SUBSCRIBERNAME,
                A.SVCCOMPONENTID = B.SVCCOMPONENTID,
                A.ROUTINGINSTANCEID = B.ROUTINGINSTANCEID,
                A.L3FWD_SERVICESITE = B.L3FWD_SERVICESITE,
                A.VPRN_L3ACCESSINTERFACE = B.VPRN_L3ACCESSINTERFACE,
                A.VPRN_ROUTINGINSTANCESITE = B.VPRN_ROUTINGINSTANCESITE,
                A.FECHA_ACTUALIZACION = TRUNC(SYSDATE, 'DD'),
                A.ESTADO_SEG = 1
            WHEN NOT MATCHED THEN INSERT (vprn_id, displayedName, description, serviceId, serviceName, vcId, siteId, subscriberId, subscriberName, svcComponentId, routingInstanceId, objectFullName, l3fwd_ServiceSite, vprn_L3AccessInterface, vprn_RoutingInstanceSite, fecha_insercion, estado_seg)
                VALUES(b.vprn_id, b.displayedName, b.description, b.serviceId, b.serviceName, b.vcId, b.siteId, b.subscriberId, b.subscriberName, b.svcComponentId, b.routingInstanceId, b.objectFullName, b.l3fwd_ServiceSite, b.vprn_L3AccessInterface, b.vprn_RoutingInstanceSite, TRUNC(SYSDATE, 'DD'), 1);
            COMMIT;
        END;"""
        self.db.query(query)

    def load_temp_table(self, registros_to_insert):
        query = f'DELETE FROM {self.temp_table}'
        self.db.query(query)

        template = f"INSERT INTO {self.temp_table}(vprn_id, displayedName, description, serviceId, serviceName, vcId, siteId, subscriberId, subscriberName, svcComponentId, routingInstanceId, objectFullName, l3fwd_ServiceSite, vprn_L3AccessInterface, vprn_RoutingInstanceSite) VALUES (:vprn_id, :displayedName, :description, :serviceId, :serviceName, :vcId, :siteId, :subscriberId, :subscriberName, :svcComponentId, :routingInstanceId, :objectFullName, :l3fwd_ServiceSite, :vprn_L3AccessInterface, :vprn_RoutingInstanceSite)"
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