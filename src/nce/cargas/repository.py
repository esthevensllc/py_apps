import re
import datetime as dt
import cx_Oracle
import random

class NCECargaConfigRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'tx_tabla'
        self.extra_name = ''

    def get(self):
        sql = f"SELECT codigo_medicion, nombre_tabla||'{self.extra_name}', granularidad, estado, flag_pronatel, del_duplicados FROM {self.table} WHERE estado=1"
        resp = self.db.fetch(sql)
        to_return = []
        for row in resp:
            to_return.append({
                'codigo_medicion': row[0],
                'nombre_tabla': row[1],
                'granularidad': row[2],
                'estado': row[3],
                'flag_pronatel': row[4],
                'del_duplicados': row[5],
            })
        return to_return
    
    def find_by_codigo_med(self, codigo_medicion):
        sql = f"SELECT codigo_medicion, nombre_tabla||'{self.extra_name}', granularidad, estado, flag_pronatel, del_duplicados FROM {self.table} WHERE codigo_medicion||'_'||granularidad = '{codigo_medicion}' and estado=1"
        resp = self.db.fetch(sql)
        to_return = None
        for row in resp:
            to_return = {
                'codigo_medicion': row[0],
                'nombre_tabla': row[1],
                'granularidad': row[2],
                'estado': row[3],
                'flag_pronatel': row[4],
                'del_duplicados': row[5]
            }
            break
        return to_return

    def get_fields_by_tabla(self, nombre_tabla):
        sql = f"SELECT LOWER(columna_smart) columna_smart, columna_100g, tipo_dato, codigo_medicion FROM tx_validacampos_2 WHERE lower(nombre_tabla||'{self.extra_name}') = '{nombre_tabla.lower()}' and estado=1"
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

    def count_where_collectiontime_between(self, table, granularidad, date_field, fecha1, fecha2):
        fecha1_str = fecha1.strftime('%Y-%m-%d %H:%M:%S')
        fecha2_str = fecha2.strftime('%Y-%m-%d %H:%M:%S')
        partition = fecha1.strftime('%Y%m')
        query = f"""SELECT COUNT(*) as counter FROM {table.lower()} PARTITION(P_{partition})
        WHERE {date_field.lower()}>=TO_DATE(:fecha1, 'YYYY-MM-DD HH24:MI:SS')
        and {date_field.lower()}<=TO_DATE(:fecha2, 'YYYY-MM-DD HH24:MI:SS') and granularityperiod = :granularidad"""
        result = self.db.fetch(query, {"fecha1": fecha1_str, "fecha2": fecha2_str, "granularidad": int(granularidad)})
        return result[0][0]

    def delete_where_collectiontime_between(self, table, granularidad, date_field, fecha1, fecha2):
        fecha1_str = fecha1.strftime('%Y%m%d%H%M%S')
        fecha2_str = fecha2.strftime('%Y%m%d%H%M%S')
        partition = fecha1.strftime('%Y%m')
        sql = f"DELETE FROM {table} PARTITION(P_{partition}) WHERE {date_field}>=TO_DATE('{fecha1_str}', 'YYYYMMDDHH24MISS') and {date_field}<=TO_DATE('{fecha2_str}', 'YYYYMMDDHH24MISS') and granularityperiod = {granularidad}"
        self.db.query(sql)
    
    def insert_from_array(self, template, bindings, registros_to_insert):
        config = {'template': template, 'bindings': bindings.copy(), 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)
        # self.db.exec_batch(config, registros_to_insert)

    def createSuccessEvent(self, queue_id, fecha):
        self.db.callproc(f"PK_PADM_QUEUE.SP_NCE_FILE_SUCCESS('{queue_id}', '{fecha}')", {})

    def get_insert_template_and_bindings(self, table, cvffields_by_fieldconfig):
        str_fields = []
        str_binds = []
        bindings = {}
        datatypes_by_db = {
            "oracle": {"FLOAT": cx_Oracle.NUMBER, "INT": cx_Oracle.NUMBER, "STRING": cx_Oracle.STRING, "DATE": cx_Oracle.STRING},
            "clickhouse": {"FLOAT": "decimal", "INT": "int", "STRING": "string", "DATE": "datetime"}
        }
        db_types = datatypes_by_db["oracle"]
        for csvfield in list(cvffields_by_fieldconfig):
            field = cvffields_by_fieldconfig[csvfield]
            if field is not None:
                str_fields.append(field['columna_smart'])
                cx_oracle_type = None
                if field['tipo_dato'] == 'FLOAT' or field['tipo_dato'] == 'INT':
                    str_binds.append(f":{field['columna_smart']}")
                    cx_oracle_type = db_types["FLOAT"]
                elif field['tipo_dato'] == 'STRING':
                    str_binds.append(f":{field['columna_smart']}")
                    cx_oracle_type = db_types["STRING"]
                elif field['tipo_dato'] == 'DATE':
                    str_binds.append(f"TO_DATE(:{field['columna_smart']}, 'YYYY-MM-DD HH24:MI:SS')")
                    cx_oracle_type = db_types["DATE"]
                bindings[field['columna_smart']] = cx_oracle_type
        template = f"INSERT INTO {table}({', '.join(str_fields)}) VALUES ({', '.join(str_binds)})"
        return template, bindings


class ClickHouseNCECargaConfigRepository(NCECargaConfigRepository):
    def __init__(self, db):
        super().__init__(db)
        self.table = 'tx_tabla_ch'

class ClickHouseSharedRepository:
    def __init__(self, db, oracle):
        self.db = db
        self.oracle = oracle

    def count_where_collectiontime_between(self, table, granularidad, date_field, fecha1, fecha2):
        fecha1_str = fecha1.strftime('%Y-%m-%d %H:%M:%S')
        fecha2_str = fecha2.strftime('%Y-%m-%d %H:%M:%S')
        query = f"SELECT COUNT(*) as counter FROM {table.lower()} WHERE {date_field.lower()}>=toDateTime({{fecha1:String}}) and {date_field.lower()}<=toDateTime({{fecha2:String}}) and granularityperiod = {granularidad}"
        result = self.db.fetch(query, {"fecha1": fecha1_str, "fecha2": fecha2_str})
        return result[0][0]

    def delete_where_collectiontime_between(self, table, granularidad, date_field, fecha1, fecha2):
        str_partition = "P_"+fecha1.strftime('%Y%m%d%H')

        fecha_fin_part = (fecha1 + dt.timedelta(hours=1)).strftime('%Y-%m-%d %H')+":00:00"

        temp_table = f"{table.lower()}_temp_{random.randrange(100000, 999999, 4)}"
        self.db.query(f"DROP TABLE IF EXISTS {temp_table}")
        sql = f"""
        CREATE TEMPORARY TABLE {temp_table}
        ENGINE = MergeTree
        PRIMARY KEY (collectiontime, granularityperiod)
        ORDER BY (collectiontime, granularityperiod)
        as
        select * from {table.lower()}
        where {date_field.lower()} >= toDateTime('{fecha1.strftime('%Y-%m-%d %H')}:00:00')
        and {date_field.lower()} < toDateTime('{fecha_fin_part}')
        and not (
            {date_field.lower()} >= toDateTime('{fecha1.strftime('%Y-%m-%d %H:%M:%S')}')
            and {date_field.lower()} < toDateTime('{fecha2.strftime('%Y-%m-%d %H:%M:%S')}')
            and granularityperiod = {granularidad}
        )
        """
        self.db.query(sql)
        sql = f"ALTER TABLE {table.lower()} DROP PARTITION '{str_partition}'"
        self.db.query(sql)
        sql = f"INSERT INTO {table.lower()} SELECT * FROM {temp_table}"
        self.db.query(sql)
        self.db.query(f"DROP TABLE IF EXISTS {temp_table}")

    def insert_from_array(self, template, bindings, registros_to_insert):
        config = {'template': template.lower(), 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        registros_to_insert = self.db.map_data_by_bindings(registros_to_insert, bindings)
        self.db.insert(config, registros_to_insert)

    def createSuccessEvent(self, queue_id, fecha):
        self.oracle.callproc(f"PK_PADM_QUEUE.SP_NCE_FILE_SUCCESS('{queue_id}', '{fecha}')", {})

    def get_insert_template_and_bindings(self, table, cvffields_by_fieldconfig):
        str_fields = []
        str_binds = []
        bindings = {}
        datatypes_by_db = {
            "oracle": {"FLOAT": cx_Oracle.NUMBER, "INT": cx_Oracle.NUMBER, "STRING": cx_Oracle.STRING, "DATE": cx_Oracle.STRING},
            "clickhouse": {"FLOAT": "decimal", "INT": "int", "STRING": "string", "DATE": "datetime"}
        }
        db_types = datatypes_by_db["clickhouse"]
        for csvfield in list(cvffields_by_fieldconfig):
            field = cvffields_by_fieldconfig[csvfield]
            if field is not None:
                str_fields.append(field['columna_smart'])
                cx_oracle_type = None
                if field['tipo_dato'] == 'FLOAT':
                    str_binds.append(f":{field['columna_smart']}")
                    cx_oracle_type = db_types["FLOAT"]
                if field['tipo_dato'] == 'INT':
                    str_binds.append(f":{field['columna_smart']}")
                    cx_oracle_type = db_types["INT"]
                elif field['tipo_dato'] == 'STRING':
                    str_binds.append(f":{field['columna_smart']}")
                    cx_oracle_type = db_types["STRING"]
                elif field['tipo_dato'] == 'DATE':
                    str_binds.append(f"TO_DATE(:{field['columna_smart']}, 'YYYY-MM-DD HH24:MI:SS')")
                    cx_oracle_type = db_types["DATE"]
                bindings[field['columna_smart']] = cx_oracle_type
        return table, bindings
