import cx_Oracle

class U2000BoardReportRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'U2000_BOARD_REPORT'
    
    def delete_where_collectiontime_between(self, fecha1, fecha2):
        sql = "DELETE FROM "+self.table+" WHERE COLLECTIONTIME>=TO_DATE('{}', 'YYYYMMDDHH24MI') and COLLECTIONTIME<TO_DATE('{}', 'YYYYMMDDHH24MI')".format(fecha1.strftime('%Y%m%d%H%M'), fecha2.strftime('%Y%m%d%H%M'))
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        insert_into_template = """INSERT INTO """+self.table+"""(NE, BOARD_NAME, BOARD_TYPE, NE_TYPE, SUBRACK_ID, SLOT_ID, HARDWARE_VERSION, SOFTWARE_VERSION, SN_BAR_CODE, "ALIAS", REMARKS, CUSTOMIZED_COLUMN, SUBRACK_TYPE, NE_ID, BIOS_VERSION, FPGA_VERSION, BOARD_STATUS, PN_BOM_CODE_ITEM, "MODEL", REV_ISSUE_NUMBER, "MANAGEMENT", "DESCRIPTION", MANUFACTURE_DATE, CREATE_TIME, COLLECTIONTIME) VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, TO_DATE(:23, 'YYYY-MM-DD'), TO_DATE(:24, 'YYYY-MM-DD'), TO_DATE(:25, 'DD/MM/YYYY'))"""

        bindings = [cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.NUMBER, cx_Oracle.NUMBER, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING]
        config = {'template': insert_into_template, 'bindings': bindings, 'row_type': 'array'}
        self.db.save_from_array2(config, registros_to_insert)
    
    