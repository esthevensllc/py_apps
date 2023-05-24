import re

class NCECargaConfigRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'tx_tabla'
        self.extra_name = ''

    def get(self):
        sql = f"SELECT codigo_medicion, nombre_tabla||'{self.extra_name}', granularidad, estado, flag_pronatel FROM {self.table} WHERE estado=1"
        resp = self.db.fetch(sql)
        to_return = []
        for row in resp:
            to_return.append({
                'codigo_medicion': row[0],
                'nombre_tabla': row[1],
                'granularidad': row[2],
                'estado': row[3],
                'flag_pronatel': row[4]
            })
        return to_return
    
    def find_by_codigo_med(self, codigo_medicion):
        sql = f"SELECT codigo_medicion, nombre_tabla||'{self.extra_name}', granularidad, estado, flag_pronatel FROM {self.table} WHERE codigo_medicion||'_'||granularidad = '{codigo_medicion}' and estado=1"
        resp = self.db.fetch(sql)
        to_return = None
        for row in resp:
            to_return = {
                'codigo_medicion': row[0],
                'nombre_tabla': row[1],
                'granularidad': row[2],
                'estado': row[3],
                'flag_pronatel': row[4]
            }
            break
        return to_return

    def get_fields_by_tabla(self, nombre_tabla):
        sql = f"SELECT columna_smart, columna_100g, tipo_dato, codigo_medicion FROM tx_validacampos WHERE lower(nombre_tabla||'{self.extra_name}') = '{nombre_tabla.lower()}' and estado=1"
        resp = self.db.fetch(sql)
        data = []
        varchar2 = re.compile('VARCHAR2.*')
        for row in resp:
            tipo_dato = row[2]
            if varchar2.match(tipo_dato):
                tipo_dato = 'VARCHAR2'
            data.append({
                'columna_smart': row[0],
                'columna_100g': row[1],
                'tipo_dato': tipo_dato,
                'codigo_medicion': row[3]
            })
        return data

class SharedRepository:
    def __init__(self, db):
        self.db = db

    def delete_where_collectiontime_between(self, table, date_field, fecha1, fecha2):
        fecha1_str = fecha1.strftime('%Y%m%d%H%M%S')
        fecha2_str = fecha2.strftime('%Y%m%d%H%M%S')
        partition = fecha1.strftime('%Y%m')
        sql = f"DELETE FROM {table} PARTITION(P_{partition}) WHERE {date_field}>=TO_DATE('{fecha1_str}', 'YYYYMMDDHH24MISS') and {date_field}<=TO_DATE('{fecha2_str}', 'YYYYMMDDHH24MISS')"
        self.db.query(sql)
    
    def insert_from_array(self, template, bindings, registros_to_insert):
        config = {'template': template, 'bindings': bindings.copy(), 'row_type': 'object', 'limit_to_commit': 50000}
        # self.db.save_from_array2(config, registros_to_insert)
        self.db.exec_batch(config, registros_to_insert)

    def createSuccessEvent(self, queue_id, fecha):
        self.db.callproc(f"PK_PADM_QUEUE.SP_NCE_FILE_SUCCESS('{queue_id}', '{fecha}')", {})