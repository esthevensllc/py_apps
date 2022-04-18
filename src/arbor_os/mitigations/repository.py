import cx_Oracle

class MitigationRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'arbor_mitigation'

    def delete_all(self):
        self.db.query(f'truncate table {self.table}')

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(ID, DESCRIPTION, IP_VERSION, NAME, ONGOING, IS_AUTOMITIGATION, START_TIME, STOP_TIME, SUBTYPE, MI_USER, ALERT_ID, SUBOBJECT) VALUES (:id, :description, :ip_version, :name, :ongoing, :is_automitigation, to_date(:start_time,'yyyy-mm-dd hh24:mi:ss'), to_date(:stop_time, 'yyyy-mm-dd hh24:mi:ss'), :subtype, :mi_user, :alert_id, :subobject)"

        bindings = {
            'id': cx_Oracle.STRING,
            'description': cx_Oracle.STRING,
            'ip_version': cx_Oracle.NUMBER,
            'name': cx_Oracle.STRING,
            'ongoing': cx_Oracle.NUMBER,
            'is_automitigation': cx_Oracle.NUMBER,
            'start_time': cx_Oracle.STRING,
            'stop_time': cx_Oracle.STRING,
            'subtype': cx_Oracle.STRING,
            'mi_user': cx_Oracle.STRING,
            'alert_id': cx_Oracle.STRING,
            'subobject': cx_Oracle.CLOB
        }

        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)