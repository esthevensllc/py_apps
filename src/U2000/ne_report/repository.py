import cx_Oracle

class U2000NeReportRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'U2000_NE_REPORT'
    
    def delete_where_collectiontime_between(self, fecha1, fecha2):
        sql = "DELETE FROM "+self.table+" WHERE COLLECTIONTIME>=TO_DATE('{}', 'YYYYMMDDHH24MI') and COLLECTIONTIME<TO_DATE('{}', 'YYYYMMDDHH24MI')".format(fecha1.strftime('%Y%m%d%H%M'), fecha2.strftime('%Y%m%d%H%M'))
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        insert_into_template = """INSERT INTO """+self.table+"""(NE_NAME, NE_TYPE, NE_IP_ADDRESS, NE_MAC_ADDRESS, NE_ID, SOFTWARE_VERSION, PHYSICAL_LOCATION, CREATE_TIME, FIBER_CABLE_COUNT, RUNNING_STATUS, SUBNET, SUBNET_PATH, ALIAS, REMARKS, PATCH_VERSION_LIST, CUSTOMIZED_COLUMN, LSR_ID, MAINTENANCE_STATUS, GATEWAY_TYPE, GATEWAY, OPTICAL_NE, SUBRACK_TYPE, CONFERENCE_CALL, ORDERWIRE_PHONE, NE_SUBTYPE, COLLECTIONTIME) VALUES (:1, :2, :3, :4, :5, :6, :7, TO_DATE(:8, 'MM/DD/YYYY HH24:MI:SS'), :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25,  TO_DATE(:26, 'DD/MM/YYYY'))"""

        bindings = [cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.NUMBER, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.NUMBER, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING]
        config = {'template': insert_into_template, 'bindings': bindings, 'row_type': 'array'}
        self.db.save_from_array2(config, registros_to_insert)