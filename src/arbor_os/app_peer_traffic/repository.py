import cx_Oracle

class ApplicationPeerTrafficRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'arbor_app_peer_traffic'

    def delete_where_collectiontime_between(self, fecha1, fecha2):
        sql = "DELETE FROM "+self.table+" WHERE COLLECTIONTIME>=TO_DATE('{}', 'YYYYMMDDHH24MI') and COLLECTIONTIME<TO_DATE('{}', 'YYYYMMDDHH24MI')".format(fecha1.strftime('%Y%m%d%H%M'), fecha2.strftime('%Y%m%d%H%M'))
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        # template = "INSERT INTO "+self.table+"(collectiontime, granularidad, application, peer, in_pct95, in_avg, in_max, in_sum, in_current, out_pct95, out_avg, out_max, out_sum, out_current) VALUES (TO_DATE(:collectiontime, 'YYYY-MM-DD HH24:MI:SS'), :granularidad, :application, :peer, :in_pct95, :in_avg, :in_max, :in_sum, :in_current, :out_pct95, :out_avg, :out_max, :out_sum, :out_current)"
        template = "INSERT INTO "+self.table+"(collectiontime, granularidad, application, peer, in_current, out_current) VALUES (TO_DATE(:collectiontime, 'YYYY-MM-DD HH24:MI:SS'), :granularidad, :application, :peer, :in_current, :out_current)"
        bindings = {'collectiontime': cx_Oracle.STRING, 'granularidad': cx_Oracle.NUMBER, 'in_current': cx_Oracle.NUMBER, 'out_current': cx_Oracle.NUMBER}
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 10000}
        self.db.save_from_array2(config, registros_to_insert)