import cx_Oracle

class InterfacesTrafficRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'pm_interfaces_traffic'
        self.table_by_group = {
            'Balanceadores': 'PM_INTERFACES_STATS_BAL',
            'ROUTERS CACs': 'PM_INTERFACES_STATS_RCACS',
            'SEDES': 'PM_INTERFACES_STATS_SEDES',
            'CALL CENTERS': 'PM_INTERFACES_STATS_CALLC'
        }

    def delete_where_collectiontime_between(self, group, fecha1, fecha2):
        str_fecha1 = fecha1.strftime('%Y%m%d%H%M')
        str_fecha2 = fecha2.strftime('%Y%m%d%H%M')
        table = self.table_by_group[group]
        sql = f"DELETE FROM {table} WHERE portmfs_timestamp >= TO_DATE('{str_fecha1}', 'YYYYMMDDHH24MI') and portmfs_timestamp <= TO_DATE('{str_fecha2}', 'YYYYMMDDHH24MI')"
        self.db.query(sql)

    def insert_from_array(self, group, registros_to_insert):
        table = self.table_by_group[group]
        template = "INSERT INTO "+table+"(device_id, device_name, portmfs_resolution, portmfs_timestamp, portmfs_im_UtilizationIn, portmfs_im_BitsPerSecondIn, portmfs_im_UtilizationOut, portmfs_im_BitsPerSecondOut) VALUES (:device_id,:device_name, :portmfs_resolution, TO_DATE(:portmfs_timestamp, 'YYYY-MM-DD HH24:MI:SS'), :portmfs_im_UtilizationIn, :portmfs_im_BitsPerSecondIn, :portmfs_im_UtilizationOut, :portmfs_im_BitsPerSecondOut)"
        bindings = {
            'device_id': cx_Oracle.NUMBER,
            'device_name': cx_Oracle.STRING,
            # 'group_name': cx_Oracle.STRING,
            'portmfs_resolution': cx_Oracle.NUMBER,
            'portmfs_timestamp': cx_Oracle.STRING,
            'portmfs_im_UtilizationIn': cx_Oracle.NUMBER,
            'portmfs_im_BitsPerSecondIn': cx_Oracle.NUMBER,
            'portmfs_im_UtilizationOut': cx_Oracle.NUMBER,
            'portmfs_im_BitsPerSecondOuT': cx_Oracle.NUMBER
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 10000}
        self.db.save_from_array2(config, registros_to_insert)