import cx_Oracle

class U2000MEM_OCC_ProfileRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'U2000_mem_occ_profile_15min'
    
    def delete_where_collectiontime_between(self, fecha1, fecha2):
        sql = "DELETE FROM "+self.table+" WHERE COLLECTIONTIME>=TO_DATE('{}', 'YYYYMMDDHH24MI') and COLLECTIONTIME<TO_DATE('{}', 'YYYYMMDDHH24MI')".format(fecha1.strftime('%Y%m%d%H%M'), fecha2.strftime('%Y%m%d%H%M'))
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        insert_into_template = """INSERT INTO """+self.table+"""(DEVICEID, DEVICENAME, RESOURCENAME, COLLECTIONTIME, GRANULARITYPERIOD, MEMORY_OCCUPANCY) VALUES (:1, :2, :3, TO_DATE(:4, 'YYYY-MM-DD HH24:MI:SS'), :5, :6)"""

        bindings = [cx_Oracle.NUMBER, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.STRING, cx_Oracle.NUMBER, cx_Oracle.NUMBER]
        config = {'template': insert_into_template, 'bindings': bindings, 'row_type': 'array'}
        self.db.save_from_array2(config, registros_to_insert)
    
    