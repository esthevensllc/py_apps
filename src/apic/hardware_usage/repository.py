import cx_Oracle
from src.shared.database.ClickHouseDB import ClickHouseDB

class ApicCPURepository:
    def __init__(self, db):
        self.table = 'apic_cpu'
        self.db = db
    
    def delete_where_collectiontime_between(self, node, fecha1, fecha2):
        sql = "DELETE FROM "+self.table+" WHERE NODE='{}' AND REPINTVEND>=TO_DATE('{}', 'YYYYMMDDHH24MISS') and REPINTVEND<=TO_DATE('{}', 'YYYYMMDDHH24MISS')".format(node, fecha1.strftime('%Y%m%d%H%M%S'), fecha2.strftime('%Y%m%d%H%M%S'))
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}_temp(topology, node, childAction, cnt, idleAverage1mAvg, idleAverage1mMax, idleAverage1mMin, idleAverage1mSpct, idleAverage1mThr, idleAverage1mTr, idleAvg, idleMax, idleMin, idleSpct, idleThr, idleTr, kernelAverage1mAvg, kernelAverage1mMax, kernelAverage1mMin, kernelAverage1mSpct, kernelAverage1mThr, kernelAverage1mTr, kernelAvg, kernelMax, kernelMin, kernelSpct, kernelThr, kernelTr, lastCollOffset, modTs, repIntvEnd, repIntvStart, rn, status, userAverage1mAvg, userAverage1mMax, userAverage1mMin, userAverage1mSpct, userAverage1mThr, userAverage1mTr, userAvg, userMax, userMin, userSpct, userThr, userTr) VALUES (:topology, :node, :childAction, :cnt, :idleAverage1mAvg, :idleAverage1mMax, :idleAverage1mMin, :idleAverage1mSpct, :idleAverage1mThr, :idleAverage1mTr, :idleAvg, :idleMax, :idleMin, :idleSpct, :idleThr, :idleTr, :kernelAverage1mAvg, :kernelAverage1mMax, :kernelAverage1mMin, :kernelAverage1mSpct, :kernelAverage1mThr, :kernelAverage1mTr, :kernelAvg, :kernelMax, :kernelMin, :kernelSpct, :kernelThr, :kernelTr, :lastCollOffset, :modTs, TO_DATE(:repIntvEnd, 'YYYY-MM-DD HH24:MI:SS'), TO_DATE(:repIntvStart, 'YYYY-MM-DD HH24:MI:SS'), :rn, :status, :userAverage1mAvg, :userAverage1mMax, :userAverage1mMin, :userAverage1mSpct, :userAverage1mThr, :userAverage1mTr, :userAvg, :userMax, :userMin, :userSpct, :userThr, :userTr)"
        bindings = {'topology': cx_Oracle.STRING, 'node': cx_Oracle.STRING, 'childAction': cx_Oracle.STRING, 'cnt': cx_Oracle.NUMBER, 'idleAverage1mAvg': cx_Oracle.NUMBER, 'idleAverage1mMax': cx_Oracle.NUMBER, 'idleAverage1mMin': cx_Oracle.NUMBER, 'idleAverage1mSpct': cx_Oracle.NUMBER, 'idleAverage1mThr': cx_Oracle.STRING, 'idleAverage1mTr': cx_Oracle.NUMBER, 'idleAvg': cx_Oracle.NUMBER, 'idleMax': cx_Oracle.NUMBER, 'idleMin': cx_Oracle.NUMBER, 'idleSpct': cx_Oracle.NUMBER, 'idleThr': cx_Oracle.STRING, 'idleTr': cx_Oracle.NUMBER, 'kernelAverage1mAvg': cx_Oracle.NUMBER, 'kernelAverage1mMax': cx_Oracle.NUMBER, 'kernelAverage1mMin': cx_Oracle.NUMBER, 'kernelAverage1mSpct': cx_Oracle.NUMBER, 'kernelAverage1mThr': cx_Oracle.STRING, 'kernelAverage1mTr': cx_Oracle.NUMBER, 'kernelAvg': cx_Oracle.NUMBER, 'kernelMax': cx_Oracle.NUMBER, 'kernelMin': cx_Oracle.NUMBER, 'kernelSpct': cx_Oracle.NUMBER, 'kernelThr': cx_Oracle.STRING, 'kernelTr': cx_Oracle.NUMBER, 'lastCollOffset': cx_Oracle.NUMBER, 'modTs': cx_Oracle.STRING, 'repIntvEnd': cx_Oracle.STRING, 'repIntvStart': cx_Oracle.STRING, 'rn': cx_Oracle.STRING, 'status': cx_Oracle.STRING, 'userAverage1mAvg': cx_Oracle.NUMBER, 'userAverage1mMax': cx_Oracle.NUMBER, 'userAverage1mMin': cx_Oracle.NUMBER, 'userAverage1mSpct': cx_Oracle.NUMBER, 'userAverage1mThr': cx_Oracle.STRING, 'userAverage1mTr': cx_Oracle.NUMBER, 'userAvg': cx_Oracle.NUMBER, 'userMax': cx_Oracle.NUMBER, 'userMin': cx_Oracle.NUMBER, 'userSpct': cx_Oracle.NUMBER, 'userThr': cx_Oracle.STRING, 'userTr': cx_Oracle.NUMBER}
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.query(f"TRUNCATE TABLE {self.table}_temp")
        registros_to_insert = self.db.map_data_by_bindings(registros_to_insert, bindings)
        self.db.save_from_array2(config, registros_to_insert)
        self._insert_from_temp(list(bindings.keys()))

    def _insert_from_temp(self, fields):
        str_fields = ",".join(fields)
        query = f"""INSERT INTO {self.table}({str_fields}) SELECT {str_fields} FROM {self.table}_temp
        WHERE (node, repIntvEnd) NOT IN (
            SELECT node, repIntvEnd FROM {self.table}
            WHERE repIntvEnd >= (sysdate - interval '7' hour)
        )"""
        self.db.query(query)


class ApicMemoryRepository:
    def __init__(self, db):
        self.table = 'APIC_MEMORY'
        self.db = db
    
    def delete_where_collectiontime_between(self, node, fecha1, fecha2):
        sql = "DELETE FROM "+self.table+" WHERE NODE='{}' AND REPINTVEND>=TO_DATE('{}', 'YYYYMMDDHH24MISS') and REPINTVEND<=TO_DATE('{}', 'YYYYMMDDHH24MISS')".format(node, fecha1.strftime('%Y%m%d%H%M%S'), fecha2.strftime('%Y%m%d%H%M%S'))
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}_temp(topology, node, childAction, cnt, freeAvg, freeMax, freeMin, freeSpct, freeThr, freeTr, lastCollOffset, modTs, repIntvEnd, repIntvStart, rn, status, totalAvg, totalMax, totalMin, totalSpct, totalThr, totalTr, usedAvg, usedMax, usedMin, usedSpct, usedThr, usedTr) VALUES (:topology, :node, :childAction, :cnt, :freeAvg, :freeMax, :freeMin, :freeSpct, :freeThr, :freeTr, :lastCollOffset, :modTs, TO_DATE(:repIntvEnd, 'YYYY-MM-DD HH24:MI:SS'), TO_DATE(:repIntvStart, 'YYYY-MM-DD HH24:MI:SS'), :rn, :status, :totalAvg, :totalMax, :totalMin, :totalSpct, :totalThr, :totalTr, :usedAvg, :usedMax, :usedMin, :usedSpct, :usedThr, :usedTr)"
        bindings = {
            'topology': cx_Oracle.STRING,
            'node': cx_Oracle.STRING,
            'childAction': cx_Oracle.STRING,
            'cnt': cx_Oracle.NUMBER,
            'freeAvg': cx_Oracle.NUMBER,
            'freeMax': cx_Oracle.NUMBER,
            'freeMin': cx_Oracle.NUMBER,
            'freeSpct': cx_Oracle.NUMBER,
            'freeThr': cx_Oracle.NUMBER,
            'freeTr': cx_Oracle.NUMBER,
            'lastCollOffset': cx_Oracle.NUMBER,
            'modTs': cx_Oracle.STRING,
            'repIntvEnd': cx_Oracle.STRING,
            'repIntvStart': cx_Oracle.STRING,
            'rn': cx_Oracle.STRING,
            'status': cx_Oracle.STRING,
            'totalAvg': cx_Oracle.NUMBER,
            'totalMax': cx_Oracle.NUMBER,
            'totalMin': cx_Oracle.NUMBER,
            'totalSpct': cx_Oracle.NUMBER,
            'totalThr': cx_Oracle.NUMBER,
            'totalTr': cx_Oracle.NUMBER,
            'usedAvg': cx_Oracle.NUMBER,
            'usedMax': cx_Oracle.NUMBER,
            'usedMin': cx_Oracle.NUMBER,
            'usedSpct': cx_Oracle.NUMBER,
            'usedThr': cx_Oracle.NUMBER,
            'usedTr': cx_Oracle.NUMBER
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.query(f"TRUNCATE TABLE {self.table}_temp")
        registros_to_insert = self.db.map_data_by_bindings(registros_to_insert, bindings)
        self.db.save_from_array2(config, registros_to_insert)
        self._insert_from_temp(list(bindings.keys()))

    def _insert_from_temp(self, fields):
        str_fields = ",".join(fields)
        query = f"""INSERT INTO {self.table}({str_fields}) SELECT {str_fields} FROM {self.table}_temp
        WHERE (node, repIntvEnd) NOT IN (
            SELECT node, repIntvEnd FROM {self.table}
            WHERE repIntvEnd >= (sysdate - interval '7' hour)
        )"""
        self.db.query(query)


class ApicTemperatureRepository:
    def __init__(self, db):
        self.table = 'APIC_TEMPERATURE'
        self.db = db
    
    def delete_where_collectiontime_between(self, node, sensor_id, fecha1, fecha2):
        sql = "DELETE FROM "+self.table+" WHERE NODE='{}' AND REPINTVEND>=TO_DATE('{}', 'YYYYMMDDHH24MISS') and REPINTVEND<=TO_DATE('{}', 'YYYYMMDDHH24MISS') AND SENSOR='{}'".format(node, fecha1.strftime('%Y%m%d%H%M%S'), fecha2.strftime('%Y%m%d%H%M%S'), sensor_id)
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}_temp(topology, node, sensor, childAction, cnt, currentAvg, currentMax, currentMin, currentSpct, currentThr, currentTr, lastCollOffset, modTs, normalizedAvg, normalizedMax, normalizedMin, normalizedSpct, normalizedThr, normalizedTr, repIntvEnd, repIntvStart, rn, status) VALUES (:topology, :node, :sensor, :childAction, :cnt, :currentAvg, :currentMax, :currentMin, :currentSpct, :currentThr, :currentTr, :lastCollOffset, :modTs, :normalizedAvg, :normalizedMax, :normalizedMin, :normalizedSpct, :normalizedThr, :normalizedTr, TO_DATE(:repIntvEnd, 'YYYY-MM-DD HH24:MI:SS'), TO_DATE(:repIntvStart, 'YYYY-MM-DD HH24:MI:SS'), :rn, :status)"
        bindings = {
            "topology": cx_Oracle.STRING,
            "node": cx_Oracle.STRING,
            "sensor": cx_Oracle.STRING,
            "childAction": cx_Oracle.STRING,
            "cnt": cx_Oracle.NUMBER,
            "currentAvg": cx_Oracle.NUMBER,
            "currentMax": cx_Oracle.NUMBER,
            "currentMin": cx_Oracle.NUMBER,
            "currentSpct": cx_Oracle.NUMBER,
            "currentThr": cx_Oracle.STRING,
            "currentTr": cx_Oracle.NUMBER,
            "lastCollOffset": cx_Oracle.NUMBER,
            "modTs": cx_Oracle.STRING,
            "normalizedAvg": cx_Oracle.NUMBER,
            "normalizedMax": cx_Oracle.NUMBER,
            "normalizedMin": cx_Oracle.NUMBER,
            "normalizedSpct": cx_Oracle.NUMBER,
            "normalizedThr": cx_Oracle.STRING,
            "normalizedTr": cx_Oracle.NUMBER,
            "repIntvEnd": cx_Oracle.STRING,
            "repIntvStart": cx_Oracle.STRING,
            "rn": cx_Oracle.STRING,
            "status": cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.query(f"TRUNCATE TABLE {self.table}_temp")
        registros_to_insert = self.db.map_data_by_bindings(registros_to_insert, bindings)
        self.db.save_from_array2(config, registros_to_insert)
        self._insert_from_temp(list(bindings.keys()))

    def _insert_from_temp(self, fields):
        str_fields = ",".join(fields)
        query = f"""INSERT INTO {self.table}({str_fields}) SELECT {str_fields} FROM {self.table}_temp
        WHERE (node, repIntvEnd) NOT IN (
            SELECT node, repIntvEnd FROM {self.table}
            WHERE repIntvEnd >= (sysdate - interval '7' hour)
        )"""
        self.db.query(query)


class ClickHouseApicCPURepository:
    def __init__(self, db):
        self.table = 'apic_cpu'
        self.db = db
    
    def delete_where_collectiontime_between(self, node, fecha1, fecha2):
        str_fecha1 = fecha1.strftime('%Y-%m-%d %H:%M:%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%d %H:%M:%S')
        sql = f"ALTER TABLE {self.table} DELETE WHERE node='{node}' and repIntvEnd >= toDateTime('{str_fecha1}') and repIntvEnd <= toDateTime('{str_fecha2}')"
        query_validation = f"SELECT COUNT(*) FROM {self.table} WHERE node='{node}' and repIntvEnd >= toDateTime('{str_fecha1}') and repIntvEnd <= toDateTime('{str_fecha2}')"
        count_validation = self.db.fetch(query_validation)
        count_validation = count_validation[0][0]
        if count_validation > 0:
            self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        bindings = {
            'topology': ClickHouseDB.STRING,
            'node': ClickHouseDB.STRING,
            'childAction': ClickHouseDB.STRING,
            'cnt': ClickHouseDB.DECIMAL,
            'idleAverage1mAvg': ClickHouseDB.DECIMAL,
            'idleAverage1mMax': ClickHouseDB.DECIMAL,
            'idleAverage1mMin': ClickHouseDB.DECIMAL,
            'idleAverage1mSpct': ClickHouseDB.DECIMAL,
            'idleAverage1mThr': ClickHouseDB.STRING,
            'idleAverage1mTr': ClickHouseDB.DECIMAL,
            'idleAvg': ClickHouseDB.DECIMAL,
            'idleMax': ClickHouseDB.DECIMAL,
            'idleMin': ClickHouseDB.DECIMAL,
            'idleSpct': ClickHouseDB.DECIMAL,
            'idleThr': ClickHouseDB.STRING,
            'idleTr': ClickHouseDB.DECIMAL,
            'kernelAverage1mAvg': ClickHouseDB.DECIMAL,
            'kernelAverage1mMax': ClickHouseDB.DECIMAL,
            'kernelAverage1mMin': ClickHouseDB.DECIMAL,
            'kernelAverage1mSpct': ClickHouseDB.DECIMAL,
            'kernelAverage1mThr': ClickHouseDB.STRING,
            'kernelAverage1mTr': ClickHouseDB.DECIMAL,
            'kernelAvg': ClickHouseDB.DECIMAL,
            'kernelMax': ClickHouseDB.DECIMAL,
            'kernelMin': ClickHouseDB.DECIMAL,
            'kernelSpct': ClickHouseDB.DECIMAL,
            'kernelThr': ClickHouseDB.STRING,
            'kernelTr': ClickHouseDB.DECIMAL,
            'lastCollOffset': ClickHouseDB.DECIMAL,
            'modTs': ClickHouseDB.STRING,
            'repIntvEnd': ClickHouseDB.DATETIME,
            'repIntvStart': ClickHouseDB.DATETIME,
            'rn': ClickHouseDB.STRING,
            'status': ClickHouseDB.STRING,
            'userAverage1mAvg': ClickHouseDB.DECIMAL,
            'userAverage1mMax': ClickHouseDB.DECIMAL,
            'userAverage1mMin': ClickHouseDB.DECIMAL,
            'userAverage1mSpct': ClickHouseDB.DECIMAL,
            'userAverage1mThr': ClickHouseDB.STRING,
            'userAverage1mTr': ClickHouseDB.DECIMAL,
            'userAvg': ClickHouseDB.DECIMAL,
            'userMax': ClickHouseDB.DECIMAL,
            'userMin': ClickHouseDB.DECIMAL,
            'userSpct': ClickHouseDB.DECIMAL,
            'userThr': ClickHouseDB.STRING,
            'userTr': ClickHouseDB.DECIMAL
        }
        config = {'template': self.table+"_temp", 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        registros_to_insert = self.db.map_data_by_bindings(registros_to_insert, bindings)
        self.db.query(f"TRUNCATE TABLE {self.table}_temp")
        self.db.insert(config, registros_to_insert)
        self._insert_from_temp(list(bindings.keys()))

    def _insert_from_temp(self, fields):
        str_fields = ",".join(fields)
        query = f"""INSERT INTO {self.table}({str_fields}) SELECT {str_fields} FROM {self.table}_temp
        WHERE (node, repIntvEnd) NOT IN (
            SELECT node, repIntvEnd FROM {self.table}
            WHERE repIntvEnd >= (now() - interval '7' hour)
        )"""
        self.db.query(query)


class ClickHouseApicMemoryRepository:
    def __init__(self, db):
        self.table = 'apic_memory'
        self.db = db
    
    def delete_where_collectiontime_between(self, node, fecha1, fecha2):
        str_fecha1 = fecha1.strftime('%Y-%m-%d %H:%M:%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%d %H:%M:%S')
        sql = f"ALTER TABLE {self.table} DELETE WHERE node='{node}' and repIntvEnd >= toDateTime('{str_fecha1}') and repIntvEnd <= toDateTime('{str_fecha2}')"
        query_validation = f"SELECT COUNT(*) FROM {self.table} WHERE node='{node}' and repIntvEnd >= toDateTime('{str_fecha1}') and repIntvEnd <= toDateTime('{str_fecha2}')"
        count_validation = self.db.fetch(query_validation)
        count_validation = count_validation[0][0]
        if count_validation > 0:
            self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        bindings = {
            'topology': ClickHouseDB.STRING,
            'node': ClickHouseDB.STRING,
            'childAction': ClickHouseDB.STRING,
            'cnt': ClickHouseDB.DECIMAL,
            'freeAvg': ClickHouseDB.DECIMAL,
            'freeMax': ClickHouseDB.DECIMAL,
            'freeMin': ClickHouseDB.DECIMAL,
            'freeSpct': ClickHouseDB.DECIMAL,
            'freeThr': ClickHouseDB.DECIMAL,
            'freeTr': ClickHouseDB.DECIMAL,
            'lastCollOffset': ClickHouseDB.DECIMAL,
            'modTs': ClickHouseDB.STRING,
            'repIntvEnd': ClickHouseDB.DATETIME,
            'repIntvStart': ClickHouseDB.DATETIME,
            'rn': ClickHouseDB.STRING,
            'status': ClickHouseDB.STRING,
            'totalAvg': ClickHouseDB.DECIMAL,
            'totalMax': ClickHouseDB.DECIMAL,
            'totalMin': ClickHouseDB.DECIMAL,
            'totalSpct': ClickHouseDB.DECIMAL,
            'totalThr': ClickHouseDB.DECIMAL,
            'totalTr': ClickHouseDB.DECIMAL,
            'usedAvg': ClickHouseDB.DECIMAL,
            'usedMax': ClickHouseDB.DECIMAL,
            'usedMin': ClickHouseDB.DECIMAL,
            'usedSpct': ClickHouseDB.DECIMAL,
            'usedThr': ClickHouseDB.DECIMAL,
            'usedTr': ClickHouseDB.DECIMAL
        }
        config = {'template': self.table+"_temp", 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        registros_to_insert = self.db.map_data_by_bindings(registros_to_insert, bindings)
        self.db.query(f"TRUNCATE TABLE {self.table}_temp")
        self.db.insert(config, registros_to_insert)
        self._insert_from_temp(list(bindings.keys()))

    def _insert_from_temp(self, fields):
        str_fields = ",".join(fields)
        query = f"""INSERT INTO {self.table}({str_fields}) SELECT {str_fields} FROM {self.table}_temp
        WHERE (node, repIntvEnd) NOT IN (
            SELECT node, repIntvEnd FROM {self.table}
            WHERE repIntvEnd >= (now() - interval '7' hour)
        )"""
        self.db.query(query)


class ClickHouseApicTemperatureRepository:
    def __init__(self, db):
        self.table = 'apic_temperature'
        self.db = db
    
    def delete_where_collectiontime_between(self, node, sensor_id, fecha1, fecha2):
        str_fecha1 = fecha1.strftime('%Y-%m-%d %H:%M:%S')
        str_fecha2 = fecha2.strftime('%Y-%m-%d %H:%M:%S')
        sql = f"ALTER TABLE {self.table} DELETE WHERE node='{node}' and repIntvEnd >= toDateTime('{str_fecha1}') and repIntvEnd <= toDateTime('{str_fecha2}')"
        query_validation = f"SELECT COUNT(*) FROM {self.table} WHERE node='{node}' and repIntvEnd >= toDateTime('{str_fecha1}') and repIntvEnd <= toDateTime('{str_fecha2}')"
        count_validation = self.db.fetch(query_validation)
        count_validation = count_validation[0][0]
        if count_validation > 0:
            self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        bindings = {
            "topology": ClickHouseDB.STRING,
            "node": ClickHouseDB.STRING,
            "sensor": ClickHouseDB.STRING,
            "childAction": ClickHouseDB.STRING,
            "cnt": ClickHouseDB.DECIMAL,
            "currentAvg": ClickHouseDB.DECIMAL,
            "currentMax": ClickHouseDB.DECIMAL,
            "currentMin": ClickHouseDB.DECIMAL,
            "currentSpct": ClickHouseDB.DECIMAL,
            "currentThr": ClickHouseDB.STRING,
            "currentTr": ClickHouseDB.DECIMAL,
            "lastCollOffset": ClickHouseDB.DECIMAL,
            "modTs": ClickHouseDB.STRING,
            "normalizedAvg": ClickHouseDB.DECIMAL,
            "normalizedMax": ClickHouseDB.DECIMAL,
            "normalizedMin": ClickHouseDB.DECIMAL,
            "normalizedSpct": ClickHouseDB.DECIMAL,
            "normalizedThr": ClickHouseDB.STRING,
            "normalizedTr": ClickHouseDB.DECIMAL,
            "repIntvEnd": ClickHouseDB.DATETIME,
            "repIntvStart": ClickHouseDB.DATETIME,
            "rn": ClickHouseDB.STRING,
            "status": ClickHouseDB.STRING
        }
        config = {'template': self.table+"_temp", 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        registros_to_insert = self.db.map_data_by_bindings(registros_to_insert, bindings)
        self.db.query(f"TRUNCATE TABLE {self.table}_temp")
        self.db.insert(config, registros_to_insert)
        self._insert_from_temp(list(bindings.keys()))

    def _insert_from_temp(self, fields):
        str_fields = ",".join(fields)
        query = f"""INSERT INTO {self.table}({str_fields}) SELECT {str_fields} FROM {self.table}_temp
        WHERE (node, repIntvEnd) NOT IN (
            SELECT node, repIntvEnd FROM {self.table}
            WHERE repIntvEnd >= (now() - interval '7' hour)
        )"""
        self.db.query(query)
