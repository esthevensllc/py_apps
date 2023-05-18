import cx_Oracle

class NotDiscPhysicalLMRepository:
    def __init__(self, db):
        self.db = db
        self.table = ''
        self.temp_table = ''
        self.config = {
            'default': {'table': 'SAN_NOT_DISC_PHYSICAL_LM'},
            'sam_5620': {'table': 'SAM5620_NOT_DISC_PHYSICAL_LM'},
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
                A.ENDPOINTAPOINTER = B.ENDPOINTAPOINTER,
                A.ENDPOINTBPOINTER = B.ENDPOINTBPOINTER,
                A.FECHA_ACTUALIZACION = TRUNC(SYSDATE, 'DD'),
                A.ESTADO_SEG = 1
            WHEN NOT MATCHED THEN INSERT (id, displayedName, description, endpointAPointer, endpointBPointer, objectFullName, fecha_insercion, estado_seg)
                VALUES(b.id, b.displayedName, b.description, b.endpointAPointer, b.endpointBPointer, b.objectFullName, TRUNC(SYSDATE, 'DD'), 1);
            COMMIT;
        END;"""
        self.db.query(query)

    def load_temp_table(self, registros_to_insert):
        query = f'DELETE FROM {self.temp_table}'
        self.db.query(query)

        template = f"INSERT INTO {self.temp_table}(id, displayedName, description, endpointAPointer, endpointBPointer, objectFullName) VALUES (:id, :displayedName, :description, :endpointAPointer, :endpointBPointer, :objectFullName)"
        bindings = {
            'id': cx_Oracle.STRING,
            'displayedName': cx_Oracle.STRING,
            'description': cx_Oracle.STRING,
            'endpointAPointer': cx_Oracle.STRING,
            'endpointBPointer': cx_Oracle.STRING,
            'objectFullName': cx_Oracle.STRING,
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        registros_to_insert = self.db.map_data_by_bindings(registros_to_insert, bindings, fill_data=True)
        self.db.save_from_array2(config, registros_to_insert)