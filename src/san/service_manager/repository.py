import cx_Oracle

class ServiceManagerRepository:
    def __init__(self, db):
        self.db = db
        self.table = ''
        self.temp_table = ''
        self.config = {
            'default': {'table': 'SAN_SERVICE_MANAGER'},
            'sam_5620': {'table': 'SAM5620_SERVICE_MANAGER'},
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

        template = "INSERT INTO "+self.temp_table+"(id, displayedName, description, serviceId, subscriberId, customerName, objectFullName) VALUES (:id, :displayedName, :description, :serviceId, :subscriberId, :customerName, :objectFullName)"
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
        self.temp_table = ''
        self.config = {
            'default': {'table': 'SAN_SERVICE_MANAGER_SITE'},
            'sam_5620': {'table': 'SAM5620_SERVICE_MANAGER_SITE'},
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
            ON (
                A.service_manager_id = B. service_manager_id AND
                A.OBJECTFULLNAME = B.OBJECTFULLNAME
            )
            WHEN MATCHED THEN UPDATE SET
                A.DISPLAYEDNAME = B.DISPLAYEDNAME,
                A.DESCRIPTION = B.DESCRIPTION,
                A.SERVICEID = B.SERVICEID,
                A.VCID = B.VCID,
                A.SUBSCRIBERID = B.SUBSCRIBERID,
                A.SUBSCRIBERNAME = B.SUBSCRIBERNAME,
                A.NUMBEROFACCESSINTERFACES = B.NUMBEROFACCESSINTERFACES,
                A.NAME = B.NAME,
                A.SVT_SPOKESDPBINDING = B.SVT_SPOKESDPBINDING,
                A.VLL_L2ACCESSINTERFACE = B.VLL_L2ACCESSINTERFACE,
                A.FECHA_ACTUALIZACION = TRUNC(SYSDATE, 'DD'),
                A.ESTADO_SEG = 1
            WHEN NOT MATCHED THEN INSERT (service_manager_id, displayedName, description, serviceId, vcId, subscriberId, subscriberName, numberOfAccessInterfaces, name, objectFullName, svt_SpokeSdpBinding, vll_L2AccessInterface, fecha_insercion, estado_seg)
                VALUES(b.service_manager_id, b.displayedName, b.description, b.serviceId, b.vcId, b.subscriberId, b.subscriberName, b.numberOfAccessInterfaces, b.name, b.objectFullName, b.svt_SpokeSdpBinding, b.vll_L2AccessInterface, TRUNC(SYSDATE, 'DD'), 1);
            COMMIT;
        END;"""
        self.db.query(query)

    def load_temp_table(self, registros_to_insert):
        query = f'DELETE FROM {self.temp_table}'
        self.db.query(query)

        template = f"INSERT INTO {self.temp_table}(service_manager_id, displayedName, description, serviceId, vcId, subscriberId, subscriberName, numberOfAccessInterfaces, name, objectFullName, svt_SpokeSdpBinding, vll_L2AccessInterface) VALUES (:service_manager_id, :displayedName, :description, :serviceId, :vcId, :subscriberId, :subscriberName, :numberOfAccessInterfaces, :name, :objectFullName, :svt_SpokeSdpBinding, :vll_L2AccessInterface)"
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
