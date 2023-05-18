import cx_Oracle

class SANPhysicalLMRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'SAN_PHYSICAL_LM'
        self.temp_table = ''
        self.config = {
            'default': {'table': 'SAN_PHYSICAL_LM'},
            'sam_5620': {'table': 'SAM5620_PHYSICAL_LM'},
        }
        self.use("default")
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
                A.DISPLAYEDNAME = B.DISPLAYEDNAME,
                A.DESCRIPTION = B.DESCRIPTION,
                A.ENDPOINTAPORTID = B.ENDPOINTAPORTID,
                A.ENDPOINTBPORTID = B.ENDPOINTBPORTID,
                A.ENDPOINTAPOINTER = B.ENDPOINTAPOINTER,
                A.ENDPOINTBPOINTER = B.ENDPOINTBPOINTER,
                A.ENDPOINTASITEID = B.ENDPOINTASITEID,
                A.ENDPOINTBSITEID = B.ENDPOINTBSITEID,
                A.ENDPOINTATYPE = B.ENDPOINTATYPE,
                A.ENDPOINTBTYPE = B.ENDPOINTBTYPE,
                A.USESMANAGEDENDPOINTA = B.USESMANAGEDENDPOINTA,
                A.USESMANAGEDENDPOINTB = B.USESMANAGEDENDPOINTB,
                A.FECHA_ACTUALIZACION = TRUNC(SYSDATE, 'DD'),
                A.ESTADO_SEG = 1
            WHEN NOT MATCHED THEN INSERT (displayedName, description, endPointAPortId, endPointBPortId, usesManagedEndpointA, endpointAPointer, endpointBPointer, endPointASiteId, endPointBSiteId, endPointAType, endPointBType, usesManagedEndpointB, objectFullName, fecha_insercion, estado_seg)
                VALUES(b.displayedName, b.description, b.endPointAPortId, b.endPointBPortId, b.usesManagedEndpointA, b.endpointAPointer, b.endpointBPointer, b.endPointASiteId, b.endPointBSiteId, b.endPointAType, b.endPointBType, b.usesManagedEndpointB, b.objectFullName, TRUNC(SYSDATE, 'DD'), 1);
            COMMIT;
        END;"""
        self.db.query(query)

    def load_temp_table(self, registros_to_insert):
        query = f'DELETE FROM {self.temp_table}'
        self.db.query(query)

        template = "INSERT INTO "+self.temp_table+"(displayedName, description, endPointAPortId, endPointBPortId, usesManagedEndpointA, endpointAPointer, endpointBPointer, endPointASiteId, endPointBSiteId, endPointAType, endPointBType, usesManagedEndpointB, objectFullName) VALUES (:displayedName, :description, :endPointAPortId, :endPointBPortId, :usesManagedEndpointA, :endpointAPointer, :endpointBPointer, :endPointASiteId, :endPointBSiteId, :endPointAType, :endPointBType, :usesManagedEndpointB, :objectFullName)"
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