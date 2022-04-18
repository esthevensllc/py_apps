import cx_Oracle

class U2000SubrackReportRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'U2000_SUBRACK_REPORT'
    
    def delete_where_collectiontime_between(self, fecha1, fecha2):
        sql = "DELETE FROM "+self.table+" WHERE COLLECTIONTIME>=TO_DATE('{}', 'YYYYMMDDHH24MI') and COLLECTIONTIME<TO_DATE('{}', 'YYYYMMDDHH24MI')".format(fecha1.strftime('%Y%m%d%H%M'), fecha2.strftime('%Y%m%d%H%M'))
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        insert_into_template = """INSERT INTO """+self.table+"""(NE, SUBRACK_NAME, SUBRACK_TYPE, SUBRACK_ID, SOFTWARE_VERSION, NE_ID, ALIAS, SUBRACK_STATUS, SN_BAR_CODE, TELECOMMUNICATIONS_ROOM, RACK, SUBRACK_NO, PN_BOM_CODE_ITEM, DESCRIPTION, MANUFACTURE_DATE, SUBNET, SUBNET_PATH, EQUIPMENT_NO, REMARKS, CUSTOMIZED_COLUMN, COLLECTIONTIME) VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, TO_DATE(:15, 'YYYY-MM-DD'), :16, :17, :18, :19, :20, TO_DATE(:21, 'DD/MM/YYYY'))"""

        bindings = [cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.NUMBER, cx_Oracle.STRING, cx_Oracle.NUMBER, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING]
        config = {'template': insert_into_template, 'bindings': bindings, 'row_type': 'array'}
        self.db.save_from_array2(config, registros_to_insert)
    
    