import cx_Oracle
class AlarmasU2000_Repository:
    def __init__(self, db):
        self.db = db
        self.table = 'U2000_ALARMAS_5MIN'

    def delete_where_collectiontime(self, fecha):
        sql = "DELETE FROM "+self.table+" WHERE COLLECTIONTIME=TO_DATE({}, 'YYYYMMDDHH24MI')".format(fecha.strftime('%Y%m%d%H%M'))
        self.db.query(sql)
    
    def delete_where_collectiontime_between(self, fecha1, fecha2):
        sql = "DELETE FROM "+self.table+" WHERE COLLECTIONTIME>=TO_DATE('{}', 'YYYYMMDDHH24MI') and COLLECTIONTIME<TO_DATE('{}', 'YYYYMMDDHH24MI')".format(fecha1.strftime('%Y%m%d%H%M'), fecha2.strftime('%Y%m%d%H%M'))
        self.db.query(sql)

    def insert_from_list(self, registros_to_insert):
        insert_into_template = """INSERT INTO """+self.table+"""(LOG_SERIAL_NUMBER, OBJECT_IDENTITY_NAME, OBJECT_IDENTITY, PRODUCT_NAME, NE_TYPE, NE_OBJECT_IDENTITY, ALARM_SOURCE, EQUIPMENT_ALARMSERIALNUMBER, ALARMNAME, TYPE, SEVERITY, STATUS, OCCURRENCETIME, ACKNOWLEDGEMENTTIME, CLEARANCETIME, UN_ACKNOWLEDGEMENTOPERATOR, CLEARANCE_OPERATOR, LOCATIONINFORMATION, LINKFDN, LINKNAME, LINKTYPE, ALARM_IDENTIFIER, ALARM_ID, OBJECT_INSTANCE_TYPE, AUTO_CLEAR, ALARM_CLEAR_TYPE, BUSINESS_AFFECTED, ADDTIONAL_TEXT, ARRIVEDUTCTIME, LIST_ID, RELATED_LOGID, AGENT_ID, ROOT_ID, SHOW_FLAG, COLLECTIONTIME)
        VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12,
        TO_DATE(:13, 'YYYY/MM/DD HH24:MI:SS'), :14,
        TO_DATE(:15, 'YYYY/MM/DD HH24:MI:SS'), :16, :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27, :28,
        TO_DATE(:29, 'YYYY/MM/DD HH24:MI:SS'), :30, :31, :32, :33, :34, TO_DATE(:35, 'YYYYMMDDHH24MI'))"""

        bindings = [cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.NUMBER, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.NUMBER, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.NUMBER, cx_Oracle.NUMBER, cx_Oracle.NUMBER, cx_Oracle.NUMBER, cx_Oracle.NUMBER, cx_Oracle.STRING]
        config = {'template': insert_into_template, 'bindings': bindings, 'row_type': 'array'}
        self.db.save_from_array2(config, registros_to_insert)