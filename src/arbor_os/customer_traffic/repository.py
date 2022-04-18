import cx_Oracle

class CustomerTrafficRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'arbor_customer_traffic'

    def delete_where_collectiontime_between(self, fecha1, fecha2):
        sql = "DELETE FROM "+self.table+" WHERE COLLECTIONTIME>=TO_DATE('{}', 'YYYYMMDDHH24MI') and COLLECTIONTIME<TO_DATE('{}', 'YYYYMMDDHH24MI')".format(fecha1.strftime('%Y%m%d%H%M'), fecha2.strftime('%Y%m%d%H%M'))
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        template = "INSERT INTO "+self.table+"(collectiontime, granularidad, customer, in_bps, out_bps) VALUES (TO_DATE(:collectiontime, 'YYYY-MM-DD HH24:MI:SS'), :granularidad, :customer, :in_bps, :out_bps)"
        bindings = {'collectiontime': cx_Oracle.STRING, 'granularidad': cx_Oracle.NUMBER, 'customer': cx_Oracle.STRING, 'in_bps': cx_Oracle.NUMBER, 'out_bps': cx_Oracle.NUMBER}
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.save_from_array2(config, registros_to_insert)