import cx_Oracle
from src.shared.database.ClickHouseDB import ClickHouseDB

class ApicInterfaceRepository:
    def __init__(self, db):
        self.table = 'APIC_INTERFACE'
        self.db = db

    def delete_by_node(self, node):
        sql = f"DELETE FROM {self.table} WHERE NODE='{node}'"
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(id, interface, node, adminSt, autoNeg, brkoutMap, bw, childAction, delay, descr, dfeDelayMs, dn, dot1qEtherType, ethpmCfgFailedBmp, ethpmCfgFailedTs, ethpmCfgState, fcotChannelNumber, fecMode, inhBw, isReflectiveRelayCfgSupported, layer, lcOwn, linkDebounce, linkFlapErrorMax, linkFlapErrorSeconds, linkLog, mdix, medium, modTs, int_mode, monPolDn, mtu, name, pathSDescr, portT, prioFlowCtrl, reflectiveRelayEn, routerMac, snmpTrapSt, spanMode, speed, status, switchingSt, trunkLog, usage, ethpmPhysIf_accessVlan, ethpmPhysIf_allowedVlans, ethpmPhysIf_backplaneMac, ethpmPhysIf_bundleBupId, ethpmPhysIf_bundleIndex, ethpmPhysIf_cfgAccessVlan, ethpmPhysIf_cfgNativeVlan, ethpmPhysIf_childAction, ethpmPhysIf_currErrIndex, ethpmPhysIf_diags, ethpmPhysIf_encap, ethpmPhysIf_errDisTimerRunning, ethpmPhysIf_errVlanStatusHt, ethpmPhysIf_errVlans, ethpmPhysIf_hwBdId, ethpmPhysIf_hwResourceId, ethpmPhysIf_intfT, ethpmPhysIf_iod, ethpmPhysIf_lastErrors, ethpmPhysIf_lastLinkStChg, ethpmPhysIf_media, ethpmPhysIf_modTs, ethpmPhysIf_monPolDn, ethpmPhysIf_nativeVlan, ethpmPhysIf_numOfSI, ethpmPhysIf_operBitset, ethpmPhysIf_operDceMode, ethpmPhysIf_operDuplex, ethpmPhysIf_operEEERxWkTime, ethpmPhysIf_operEEEState, ethpmPhysIf_operEEETxWkTime, ethpmPhysIf_operErrDisQual, ethpmPhysIf_operFecMode, ethpmPhysIf_operFlowCtrl, ethpmPhysIf_operMdix, ethpmPhysIf_operMode, ethpmPhysIf_operModeDetail, ethpmPhysIf_operPhyEnSt, ethpmPhysIf_operRouterMac, ethpmPhysIf_operSpeed, ethpmPhysIf_operSt, ethpmPhysIf_operStQual, ethpmPhysIf_operStQualCode, ethpmPhysIf_operVlans, ethpmPhysIf_osSum, ethpmPhysIf_portCfgWaitFlags, ethpmPhysIf_primaryVlan, ethpmPhysIf_resetCtr, ethpmPhysIf_rn, ethpmPhysIf_siList, ethpmPhysIf_status, ethpmPhysIf_txT, ethpmPhysIf_usage, ethpmPhysIf_userCfgdFlags, ethpmPhysIf_vdcId) VALUES (:id, :interface, :node, :adminSt, :autoNeg, :brkoutMap, :bw, :childAction, :delay, :descr, :dfeDelayMs, :dn, :dot1qEtherType, :ethpmCfgFailedBmp, :ethpmCfgFailedTs, :ethpmCfgState, :fcotChannelNumber, :fecMode, :inhBw, :isReflectiveRelayCfgSupported, :layer, :lcOwn, :linkDebounce, :linkFlapErrorMax, :linkFlapErrorSeconds, :linkLog, :mdix, :medium, TO_DATE(:modTs, 'YYYY-MM-DD HH24:MI:SS'), :int_mode, :monPolDn, :mtu, :name, :pathSDescr, :portT, :prioFlowCtrl, :reflectiveRelayEn, :routerMac, :snmpTrapSt, :spanMode, :speed, :status, :switchingSt, :trunkLog, :usage, :ethpmPhysIf_accessVlan, :ethpmPhysIf_allowedVlans, :ethpmPhysIf_backplaneMac, :ethpmPhysIf_bundleBupId, :ethpmPhysIf_bundleIndex, :ethpmPhysIf_cfgAccessVlan, :ethpmPhysIf_cfgNativeVlan, :ethpmPhysIf_childAction, :ethpmPhysIf_currErrIndex, :ethpmPhysIf_diags, :ethpmPhysIf_encap, :ethpmPhysIf_errDisTimerRunning, :ethpmPhysIf_errVlanStatusHt, :ethpmPhysIf_errVlans, :ethpmPhysIf_hwBdId, :ethpmPhysIf_hwResourceId, :ethpmPhysIf_intfT, :ethpmPhysIf_iod, :ethpmPhysIf_lastErrors, TO_DATE(:ethpmPhysIf_lastLinkStChg, 'YYYY-MM-DD HH24:MI:SS'), :ethpmPhysIf_media, :ethpmPhysIf_modTs, :ethpmPhysIf_monPolDn, :ethpmPhysIf_nativeVlan, :ethpmPhysIf_numOfSI, :ethpmPhysIf_operBitset, :ethpmPhysIf_operDceMode, :ethpmPhysIf_operDuplex, :ethpmPhysIf_operEEERxWkTime, :ethpmPhysIf_operEEEState, :ethpmPhysIf_operEEETxWkTime, :ethpmPhysIf_operErrDisQual, :ethpmPhysIf_operFecMode, :ethpmPhysIf_operFlowCtrl, :ethpmPhysIf_operMdix, :ethpmPhysIf_operMode, :ethpmPhysIf_operModeDetail, :ethpmPhysIf_operPhyEnSt, :ethpmPhysIf_operRouterMac, :ethpmPhysIf_operSpeed, :ethpmPhysIf_operSt, :ethpmPhysIf_operStQual, :ethpmPhysIf_operStQualCode, :ethpmPhysIf_operVlans, :ethpmPhysIf_osSum, :ethpmPhysIf_portCfgWaitFlags, :ethpmPhysIf_primaryVlan, :ethpmPhysIf_resetCtr, :ethpmPhysIf_rn, :ethpmPhysIf_siList, :ethpmPhysIf_status, :ethpmPhysIf_txT, :ethpmPhysIf_usage, :ethpmPhysIf_userCfgdFlags, :ethpmPhysIf_vdcId)"
        bindings = {
            "id": cx_Oracle.STRING,
            "interface": cx_Oracle.STRING,
            "node": cx_Oracle.STRING,
            "adminSt": cx_Oracle.STRING,
            "autoNeg": cx_Oracle.STRING,
            "brkoutMap": cx_Oracle.STRING,
            "bw": cx_Oracle.STRING,
            "childAction": cx_Oracle.STRING,
            "delay": cx_Oracle.NUMBER,
            "descr": cx_Oracle.STRING,
            "dfeDelayMs": cx_Oracle.NUMBER,
            "dn": cx_Oracle.STRING,
            "dot1qEtherType": cx_Oracle.STRING,
            "ethpmCfgFailedBmp": cx_Oracle.STRING,
            "ethpmCfgFailedTs": cx_Oracle.STRING,
            "ethpmCfgState": cx_Oracle.STRING,
            "fcotChannelNumber": cx_Oracle.STRING,
            "fecMode": cx_Oracle.STRING,
            "inhBw": cx_Oracle.STRING,
            "isReflectiveRelayCfgSupported": cx_Oracle.STRING,
            "layer": cx_Oracle.STRING,
            "lcOwn": cx_Oracle.STRING,
            "linkDebounce": cx_Oracle.NUMBER,
            "linkFlapErrorMax": cx_Oracle.NUMBER,
            "linkFlapErrorSeconds": cx_Oracle.NUMBER,
            "linkLog": cx_Oracle.STRING,
            "mdix": cx_Oracle.STRING,
            "medium": cx_Oracle.STRING,
            "modTs": cx_Oracle.STRING,
            "int_mode": cx_Oracle.STRING,
            "monPolDn": cx_Oracle.STRING,
            "mtu": cx_Oracle.STRING,
            "name": cx_Oracle.STRING,
            "pathSDescr": cx_Oracle.STRING,
            "portT": cx_Oracle.STRING,
            "prioFlowCtrl": cx_Oracle.STRING,
            "reflectiveRelayEn": cx_Oracle.STRING,
            "routerMac": cx_Oracle.STRING,
            "snmpTrapSt": cx_Oracle.STRING,
            "spanMode": cx_Oracle.STRING,
            "speed": cx_Oracle.STRING,
            "status": cx_Oracle.STRING,
            "switchingSt": cx_Oracle.STRING,
            "trunkLog": cx_Oracle.STRING,
            "usage": cx_Oracle.STRING,
            "ethpmPhysIf_accessVlan": cx_Oracle.STRING,
            "ethpmPhysIf_allowedVlans": cx_Oracle.STRING,
            "ethpmPhysIf_backplaneMac": cx_Oracle.STRING,
            "ethpmPhysIf_bundleBupId": cx_Oracle.STRING,
            "ethpmPhysIf_bundleIndex": cx_Oracle.STRING,
            "ethpmPhysIf_cfgAccessVlan": cx_Oracle.STRING,
            "ethpmPhysIf_cfgNativeVlan": cx_Oracle.STRING,
            "ethpmPhysIf_childAction": cx_Oracle.STRING,
            "ethpmPhysIf_currErrIndex": cx_Oracle.NUMBER,
            "ethpmPhysIf_diags": cx_Oracle.STRING,
            "ethpmPhysIf_encap": cx_Oracle.STRING,
            "ethpmPhysIf_errDisTimerRunning": cx_Oracle.STRING,
            "ethpmPhysIf_errVlanStatusHt": cx_Oracle.NUMBER,
            "ethpmPhysIf_errVlans": cx_Oracle.STRING,
            "ethpmPhysIf_hwBdId": cx_Oracle.NUMBER,
            "ethpmPhysIf_hwResourceId": cx_Oracle.NUMBER,
            "ethpmPhysIf_intfT": cx_Oracle.STRING,
            "ethpmPhysIf_iod": cx_Oracle.NUMBER,
            "ethpmPhysIf_lastErrors": cx_Oracle.NUMBER,
            "ethpmPhysIf_lastLinkStChg": cx_Oracle.STRING,
            "ethpmPhysIf_media": cx_Oracle.NUMBER,
            "ethpmPhysIf_modTs": cx_Oracle.STRING,
            "ethpmPhysIf_monPolDn": cx_Oracle.STRING,
            "ethpmPhysIf_nativeVlan": cx_Oracle.STRING,
            "ethpmPhysIf_numOfSI":cx_Oracle.STRING,
            "ethpmPhysIf_operBitset": cx_Oracle.STRING,
            "ethpmPhysIf_operDceMode": cx_Oracle.STRING,
            "ethpmPhysIf_operDuplex": cx_Oracle.STRING,
            "ethpmPhysIf_operEEERxWkTime": cx_Oracle.STRING,
            "ethpmPhysIf_operEEEState": cx_Oracle.STRING,
            "ethpmPhysIf_operEEETxWkTime": cx_Oracle.STRING,
            "ethpmPhysIf_operErrDisQual": cx_Oracle.STRING,
            "ethpmPhysIf_operFecMode": cx_Oracle.STRING,
            "ethpmPhysIf_operFlowCtrl":cx_Oracle.NUMBER,
            "ethpmPhysIf_operMdix": cx_Oracle.STRING,
            "ethpmPhysIf_operMode": cx_Oracle.STRING,
            "ethpmPhysIf_operModeDetail": cx_Oracle.STRING,
            "ethpmPhysIf_operPhyEnSt": cx_Oracle.STRING,
            "ethpmPhysIf_operRouterMac": cx_Oracle.STRING,
            "ethpmPhysIf_operSpeed": cx_Oracle.STRING,
            "ethpmPhysIf_operSt": cx_Oracle.STRING,
            "ethpmPhysIf_operStQual": cx_Oracle.STRING,
            "ethpmPhysIf_operStQualCode": cx_Oracle.NUMBER,
            "ethpmPhysIf_operVlans": cx_Oracle.STRING,
            "ethpmPhysIf_osSum": cx_Oracle.STRING,
            "ethpmPhysIf_portCfgWaitFlags": cx_Oracle.NUMBER,
            "ethpmPhysIf_primaryVlan": cx_Oracle.STRING,
            "ethpmPhysIf_resetCtr": cx_Oracle.NUMBER,
            "ethpmPhysIf_rn": cx_Oracle.STRING,
            "ethpmPhysIf_siList": cx_Oracle.STRING,
            "ethpmPhysIf_status": cx_Oracle.STRING,
            "ethpmPhysIf_txT": cx_Oracle.STRING,
            "ethpmPhysIf_usage": cx_Oracle.STRING,
            "ethpmPhysIf_userCfgdFlags": cx_Oracle.NUMBER,
            "ethpmPhysIf_vdcId": cx_Oracle.NUMBER
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.save_from_array2(config, registros_to_insert)


class ApicOracleRepo:
    def __init__(self, db):
        self.table = ''
        self.db = db
        self.fields_to_reload = []
        self.fields = {}
        self.date_field = "repIntvEnd"

    def insert_from_list(self, data):
        temp_table = self._create_temp_table()
        self._insert_in_temp(temp_table, data)
        self._insert_from_temp(temp_table)
        self.db.query(f"DROP TABLE {temp_table}")

    def _create_temp_table(self):
        template_by_type = {
            cx_Oracle.STRING: "{field} varchar2(500)",
            # cx_Oracle.STRING: "{field} date",
            cx_Oracle.NUMBER: "{field} number",
        }
        def map_field(field):
            return template_by_type[self.fields[field]].format(field=field)
        str_fields = ",".join(list(map(map_field, self.fields.keys())))
        str_fields = str_fields.replace("repIntvEnd varchar2(500)", "repIntvEnd date")
        str_fields = str_fields.replace("repIntvStart varchar2(500)", "repIntvStart date")
        str_fields = str_fields.replace("created varchar2(500)", "created date")
        str_key_fields = ",".join(self.fields_to_reload)
        temp_table = f"{self.table}_temp"
        self.db.query(f"""BEGIN
            EXECUTE IMMEDIATE 'DROP TABLE {temp_table}';
        EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE != -942 THEN
                    RAISE;
                END IF;
        END;""")
        self.db.query(f"CREATE TABLE {temp_table}({str_fields})")
        return temp_table

    def _insert_in_temp(self, temp_table, registros_to_insert):
        str_fields = ",".join(list(self.fields.keys()))
        str_bind_fields = ",".join(list(map(lambda field: f":{field}", self.fields.keys())))
        template = f"INSERT INTO {temp_table}({str_fields}) VALUES ({str_bind_fields})"
        template = template.replace(":repIntvEnd", "TO_DATE(:repIntvEnd, 'YYYY-MM-DD HH24:MI:SS')")
        template = template.replace(":repIntvStart", "TO_DATE(:repIntvStart, 'YYYY-MM-DD HH24:MI:SS')")
        template = template.replace(":created", "TO_DATE(:created, 'YYYY-MM-DD HH24:MI:SS')")
        config = {'template': template, 'bindings': self.fields, 'row_type': 'object', 'limit_to_commit': 100000}
        registros_to_insert = self.db.map_data_by_bindings(registros_to_insert, self.fields)
        self.db.save_from_array2(config, registros_to_insert)

    def _insert_from_temp(self, temptable):
        str_fields = ",".join(list(self.fields.keys()))
        str_fields_to_reload = ",".join(self.fields_to_reload)
        query = f"""INSERT INTO {self.table}({str_fields}) SELECT {str_fields} FROM {temptable}
        WHERE ({str_fields_to_reload}) NOT IN (
            SELECT {str_fields_to_reload} FROM {self.table}
            WHERE {self.date_field} > (sysdate - interval '1' day)
        )"""
        self.db.query(query)


class ApicInterfaceIngressRepository(ApicOracleRepo):
    def __init__(self, db):
        super().__init__(db)
        self.table = 'APIC_INTERFACE_INGRESS_5_MIN'
        self.db = db
        self.fields_to_reload = ["interface_id", "repIntvEnd"]
        self.fields = {
            "node_id": cx_Oracle.STRING,
            "interface_id": cx_Oracle.STRING,
            "bytesAvg": cx_Oracle.NUMBER,
            "bytesCum": cx_Oracle.NUMBER,
            "bytesMax": cx_Oracle.NUMBER,
            "bytesMin": cx_Oracle.NUMBER,
            "bytesPer": cx_Oracle.NUMBER,
            "bytesRate": cx_Oracle.NUMBER,
            "bytesRateAvg": cx_Oracle.NUMBER,
            "bytesRateMax": cx_Oracle.NUMBER,
            "bytesRateMin": cx_Oracle.NUMBER,
            "bytesRateSpct": cx_Oracle.NUMBER,
            "bytesRateThr": cx_Oracle.NUMBER,
            "bytesRateTr": cx_Oracle.NUMBER,
            "bytesSpct": cx_Oracle.NUMBER,
            "bytesThr": cx_Oracle.NUMBER,
            "bytesTr": cx_Oracle.NUMBER,
            "childAction": cx_Oracle.STRING,
            "cnt": cx_Oracle.NUMBER,
            "lastCollOffset": cx_Oracle.NUMBER,
            "modTs": cx_Oracle.STRING,
            "pktsAvg": cx_Oracle.NUMBER,
            "pktsCum": cx_Oracle.NUMBER,
            "pktsMax": cx_Oracle.NUMBER,
            "pktsMin": cx_Oracle.NUMBER,
            "pktsPer": cx_Oracle.NUMBER,
            "pktsRate": cx_Oracle.NUMBER,
            "pktsRateAvg": cx_Oracle.NUMBER,
            "pktsRateMax": cx_Oracle.NUMBER,
            "pktsRateMin": cx_Oracle.NUMBER,
            "pktsRateSpct": cx_Oracle.NUMBER,
            "pktsRateThr": cx_Oracle.NUMBER,
            "pktsRateTr": cx_Oracle.NUMBER,
            "pktsSpct": cx_Oracle.NUMBER,
            "pktsThr": cx_Oracle.NUMBER,
            "pktsTr": cx_Oracle.NUMBER,
            "repIntvEnd": cx_Oracle.STRING,
            "repIntvStart": cx_Oracle.STRING,
            "rn": cx_Oracle.STRING,
            "status": cx_Oracle.STRING,
            "utilAvg": cx_Oracle.NUMBER,
            "utilMax": cx_Oracle.NUMBER,
            "utilMin": cx_Oracle.NUMBER,
            "utilSpct": cx_Oracle.NUMBER,
            "utilThr": cx_Oracle.NUMBER,
            "utilTr": cx_Oracle.NUMBER
        }


class ApicClickHouseRepo:
    def __init__(self, db):
        self.table = ''
        self.db = db
        self.fields_to_reload = []
        self.fields = {}
        self.date_field = "repIntvEnd"

    def insert_from_list(self, data):
        temp_table = self._create_temp_table()
        self._insert_in_temp(temp_table, data)
        self._insert_from_temp(temp_table)
        # self.db.query(f"DROP TABLE {temp_table}")

    def _create_temp_table(self):
        template_by_type_null = {
            ClickHouseDB.STRING: "{field} Nullable(String) DEFAULT NULL",
            ClickHouseDB.DATETIME: "{field} Nullable(DateTime) DEFAULT NULL",
            ClickHouseDB.DECIMAL: "{field} Nullable(Decimal(38, 8)) DEFAULT NULL",
        }
        template_by_type = {
            ClickHouseDB.STRING: "{field} String",
            ClickHouseDB.DATETIME: "{field} DateTime",
            ClickHouseDB.DECIMAL: "{field} Decimal(38, 8)",
        }
        def map_field(field):
            if field in self.fields_to_reload:
                return template_by_type[self.fields[field]].format(field=field)
            return template_by_type_null[self.fields[field]].format(field=field)
        str_fields = ",".join(list(map(map_field, self.fields.keys())))
        str_key_fields = ",".join(self.fields_to_reload)
        temp_table = f"{self.table}_temp"
        self.db.query(f"CREATE TEMPORARY TABLE {temp_table}({str_fields}) ENGINE = MergeTree PRIMARY KEY ({str_key_fields}) SETTINGS index_granularity = 8192")
        return temp_table

    def _insert_in_temp(self, temp_table, registros_to_insert):
        config = {'template': temp_table, 'bindings': self.fields, 'row_type': 'object', 'limit_to_commit': 100000}
        registros_to_insert = self.db.map_data_by_bindings(registros_to_insert, self.fields)
        self.db.insert(config, registros_to_insert)

    def _insert_from_temp(self, temptable):
        str_fields = ",".join(list(self.fields.keys()))
        str_fields_to_reload = ",".join(self.fields_to_reload)
        query = f"""INSERT INTO {self.table}({str_fields}) SELECT {str_fields} FROM {temptable}
        WHERE ({str_fields_to_reload}) NOT IN (
            SELECT {str_fields_to_reload} FROM {self.table}
            WHERE {self.date_field} > (now() - interval '1' day)
        )"""
        self.db.query(query)


class ApicClickHouseInterfaceIngressRepository(ApicClickHouseRepo):
    def __init__(self, db):
        super().__init__(db)
        self.table = 'apic_interface_ingress_5_min'
        self.db = db
        self.fields_to_reload = ["interface_id", "repIntvEnd"]
        self.fields = {
            "node_id": ClickHouseDB.STRING,
            "interface_id": ClickHouseDB.STRING,
            "bytesAvg": ClickHouseDB.DECIMAL,
            "bytesCum": ClickHouseDB.DECIMAL,
            "bytesMax": ClickHouseDB.DECIMAL,
            "bytesMin": ClickHouseDB.DECIMAL,
            "bytesPer": ClickHouseDB.DECIMAL,
            "bytesRate": ClickHouseDB.DECIMAL,
            "bytesRateAvg": ClickHouseDB.DECIMAL,
            "bytesRateMax": ClickHouseDB.DECIMAL,
            "bytesRateMin": ClickHouseDB.DECIMAL,
            "bytesRateSpct": ClickHouseDB.DECIMAL,
            "bytesRateThr": ClickHouseDB.DECIMAL,
            "bytesRateTr": ClickHouseDB.DECIMAL,
            "bytesSpct": ClickHouseDB.DECIMAL,
            "bytesThr": ClickHouseDB.DECIMAL,
            "bytesTr": ClickHouseDB.DECIMAL,
            "childAction": ClickHouseDB.STRING,
            "cnt": ClickHouseDB.DECIMAL,
            "lastCollOffset": ClickHouseDB.DECIMAL,
            "modTs": ClickHouseDB.STRING,
            "pktsAvg": ClickHouseDB.DECIMAL,
            "pktsCum": ClickHouseDB.DECIMAL,
            "pktsMax": ClickHouseDB.DECIMAL,
            "pktsMin": ClickHouseDB.DECIMAL,
            "pktsPer": ClickHouseDB.DECIMAL,
            "pktsRate": ClickHouseDB.DECIMAL,
            "pktsRateAvg": ClickHouseDB.DECIMAL,
            "pktsRateMax": ClickHouseDB.DECIMAL,
            "pktsRateMin": ClickHouseDB.DECIMAL,
            "pktsRateSpct": ClickHouseDB.DECIMAL,
            "pktsRateThr": ClickHouseDB.DECIMAL,
            "pktsRateTr": ClickHouseDB.DECIMAL,
            "pktsSpct": ClickHouseDB.DECIMAL,
            "pktsThr": ClickHouseDB.DECIMAL,
            "pktsTr": ClickHouseDB.DECIMAL,
            "repIntvEnd": ClickHouseDB.DATETIME,
            "repIntvStart": ClickHouseDB.DATETIME,
            "rn": ClickHouseDB.STRING,
            "status": ClickHouseDB.STRING,
            "utilAvg": ClickHouseDB.DECIMAL,
            "utilMax": ClickHouseDB.DECIMAL,
            "utilMin": ClickHouseDB.DECIMAL,
            "utilSpct": ClickHouseDB.DECIMAL,
            "utilThr": ClickHouseDB.DECIMAL,
            "utilTr": ClickHouseDB.DECIMAL
        }


class ApicInterfaceIngressErrorRepository(ApicOracleRepo):
    def __init__(self, db):
        super().__init__(db)
        self.table = 'APIC_INTERFACE_INGRESS_ERROR_5_MIN'
        self.db = db
        self.fields_to_reload = ["interface_id", "repIntvEnd"]
        self.fields = {
            "node_id": cx_Oracle.STRING,
            "interface_id": cx_Oracle.STRING,
            "anyErrorAvg": cx_Oracle.NUMBER,
            "anyErrorCum": cx_Oracle.NUMBER,
            "anyErrorMax": cx_Oracle.NUMBER,
            "anyErrorMin": cx_Oracle.NUMBER,
            "anyErrorPer": cx_Oracle.NUMBER,
            "anyErrorRate": cx_Oracle.NUMBER,
            "anyErrorSpct": cx_Oracle.NUMBER,
            "anyErrorThr": cx_Oracle.NUMBER,
            "anyErrorTr": cx_Oracle.NUMBER,
            "childAction": cx_Oracle.NUMBER,
            "cnt": cx_Oracle.NUMBER,
            "crcAvg": cx_Oracle.NUMBER,
            "crcCountAvg": cx_Oracle.NUMBER,
            "crcCountCum": cx_Oracle.NUMBER,
            "crcCountMax": cx_Oracle.NUMBER,
            "crcCountMin": cx_Oracle.NUMBER,
            "crcCountPer": cx_Oracle.NUMBER,
            "crcCountRate": cx_Oracle.NUMBER,
            "crcCountRateAvg": cx_Oracle.NUMBER,
            "crcCountRateMax": cx_Oracle.NUMBER,
            "crcCountRateMin": cx_Oracle.NUMBER,
            "crcCountRateSpct": cx_Oracle.NUMBER,
            "crcCountRateThr": cx_Oracle.NUMBER,
            "crcCountRateTr": cx_Oracle.NUMBER,
            "crcCountSpct": cx_Oracle.NUMBER,
            "crcCountThr": cx_Oracle.NUMBER,
            "crcCountTr": cx_Oracle.NUMBER,
            "crcMax": cx_Oracle.NUMBER,
            "crcMin": cx_Oracle.NUMBER,
            "crcSpct": cx_Oracle.NUMBER,
            "crcThr": cx_Oracle.NUMBER,
            "crcTr": cx_Oracle.NUMBER,
            "discardAvg": cx_Oracle.NUMBER,
            "discardCum": cx_Oracle.NUMBER,
            "discardMax": cx_Oracle.NUMBER,
            "discardMin": cx_Oracle.NUMBER,
            "discardPer": cx_Oracle.NUMBER,
            "discardRate": cx_Oracle.NUMBER,
            "discardSpct": cx_Oracle.NUMBER,
            "discardThr": cx_Oracle.NUMBER,
            "discardTr": cx_Oracle.NUMBER,
            "lastCollOffset": cx_Oracle.NUMBER,
            "modTs": cx_Oracle.STRING,
            "repIntvEnd": cx_Oracle.STRING,
            "repIntvStart": cx_Oracle.STRING,
            "rn": cx_Oracle.STRING,
            "status": cx_Oracle.STRING
        }


class ApicClickHouseInterfaceIngressErrorRepository(ApicClickHouseRepo):
    def __init__(self, db):
        super().__init__(db)
        self.table = 'apic_interface_ingress_error_5_min'
        self.db = db
        self.fields_to_reload = ["interface_id", "repIntvEnd"]
        self.fields = {
            "node_id": ClickHouseDB.STRING,
            "interface_id": ClickHouseDB.STRING,
            "anyErrorAvg": ClickHouseDB.DECIMAL,
            "anyErrorCum": ClickHouseDB.DECIMAL,
            "anyErrorMax": ClickHouseDB.DECIMAL,
            "anyErrorMin": ClickHouseDB.DECIMAL,
            "anyErrorPer": ClickHouseDB.DECIMAL,
            "anyErrorRate": ClickHouseDB.DECIMAL,
            "anyErrorSpct": ClickHouseDB.DECIMAL,
            "anyErrorThr": ClickHouseDB.DECIMAL,
            "anyErrorTr": ClickHouseDB.DECIMAL,
            "childAction": ClickHouseDB.DECIMAL,
            "cnt": ClickHouseDB.DECIMAL,
            "crcAvg": ClickHouseDB.DECIMAL,
            "crcCountAvg": ClickHouseDB.DECIMAL,
            "crcCountCum": ClickHouseDB.DECIMAL,
            "crcCountMax": ClickHouseDB.DECIMAL,
            "crcCountMin": ClickHouseDB.DECIMAL,
            "crcCountPer": ClickHouseDB.DECIMAL,
            "crcCountRate": ClickHouseDB.DECIMAL,
            "crcCountRateAvg": ClickHouseDB.DECIMAL,
            "crcCountRateMax": ClickHouseDB.DECIMAL,
            "crcCountRateMin": ClickHouseDB.DECIMAL,
            "crcCountRateSpct": ClickHouseDB.DECIMAL,
            "crcCountRateThr": ClickHouseDB.DECIMAL,
            "crcCountRateTr": ClickHouseDB.DECIMAL,
            "crcCountSpct": ClickHouseDB.DECIMAL,
            "crcCountThr": ClickHouseDB.DECIMAL,
            "crcCountTr": ClickHouseDB.DECIMAL,
            "crcMax": ClickHouseDB.DECIMAL,
            "crcMin": ClickHouseDB.DECIMAL,
            "crcSpct": ClickHouseDB.DECIMAL,
            "crcThr": ClickHouseDB.DECIMAL,
            "crcTr": ClickHouseDB.DECIMAL,
            "discardAvg": ClickHouseDB.DECIMAL,
            "discardCum": ClickHouseDB.DECIMAL,
            "discardMax": ClickHouseDB.DECIMAL,
            "discardMin": ClickHouseDB.DECIMAL,
            "discardPer": ClickHouseDB.DECIMAL,
            "discardRate": ClickHouseDB.DECIMAL,
            "discardSpct": ClickHouseDB.DECIMAL,
            "discardThr": ClickHouseDB.DECIMAL,
            "discardTr": ClickHouseDB.DECIMAL,
            "lastCollOffset": ClickHouseDB.DECIMAL,
            "modTs": ClickHouseDB.STRING,
            "repIntvEnd": ClickHouseDB.DATETIME,
            "repIntvStart": ClickHouseDB.DATETIME,
            "rn": ClickHouseDB.STRING,
            "status": ClickHouseDB.STRING
        }


class ApicInterfaceEgressRepository(ApicOracleRepo):
    def __init__(self, db):
        super().__init__(db)
        self.table = 'APIC_INTERFACE_EGRESS_5_MIN'
        self.db = db
        self.fields_to_reload = ["interface_id", "repIntvEnd"]
        self.fields = {
            "node_id": cx_Oracle.STRING,
            "interface_id": cx_Oracle.STRING,
            "bytesAvg": cx_Oracle.NUMBER,
            "bytesCum": cx_Oracle.NUMBER,
            "bytesMax": cx_Oracle.NUMBER,
            "bytesMin": cx_Oracle.NUMBER,
            "bytesPer": cx_Oracle.NUMBER,
            "bytesRate": cx_Oracle.NUMBER,
            "bytesRateAvg": cx_Oracle.NUMBER,
            "bytesRateMax": cx_Oracle.NUMBER,
            "bytesRateMin": cx_Oracle.NUMBER,
            "bytesRateSpct": cx_Oracle.NUMBER,
            "bytesRateThr": cx_Oracle.NUMBER,
            "bytesRateTr": cx_Oracle.NUMBER,
            "bytesSpct": cx_Oracle.NUMBER,
            "bytesThr": cx_Oracle.NUMBER,
            "bytesTr": cx_Oracle.NUMBER,
            "childAction": cx_Oracle.STRING,
            "cnt": cx_Oracle.NUMBER,
            "lastCollOffset": cx_Oracle.NUMBER,
            "modTs": cx_Oracle.STRING,
            "pktsAvg": cx_Oracle.NUMBER,
            "pktsCum": cx_Oracle.NUMBER,
            "pktsMax": cx_Oracle.NUMBER,
            "pktsMin": cx_Oracle.NUMBER,
            "pktsPer": cx_Oracle.NUMBER,
            "pktsRate": cx_Oracle.NUMBER,
            "pktsRateAvg": cx_Oracle.NUMBER,
            "pktsRateMax": cx_Oracle.NUMBER,
            "pktsRateMin": cx_Oracle.NUMBER,
            "pktsRateSpct": cx_Oracle.NUMBER,
            "pktsRateThr": cx_Oracle.NUMBER,
            "pktsRateTr": cx_Oracle.NUMBER,
            "pktsSpct": cx_Oracle.NUMBER,
            "pktsThr": cx_Oracle.NUMBER,
            "pktsTr": cx_Oracle.NUMBER,
            "repIntvEnd": cx_Oracle.STRING,
            "repIntvStart": cx_Oracle.STRING,
            "rn": cx_Oracle.STRING,
            "status": cx_Oracle.STRING,
            "utilAvg": cx_Oracle.NUMBER,
            "utilMax": cx_Oracle.NUMBER,
            "utilMin": cx_Oracle.NUMBER,
            "utilSpct": cx_Oracle.NUMBER,
            "utilThr": cx_Oracle.NUMBER,
            "utilTr": cx_Oracle.NUMBER
        }


class ApicClickHouseInterfaceEgressRepository(ApicClickHouseRepo):
    def __init__(self, db):
        super().__init__(db)
        self.table = 'apic_interface_egress_5_min'
        self.db = db
        self.fields_to_reload = ["interface_id", "repIntvEnd"]
        self.fields = {
            "node_id": ClickHouseDB.STRING,
            "interface_id": ClickHouseDB.STRING,
            "bytesAvg": ClickHouseDB.DECIMAL,
            "bytesCum": ClickHouseDB.DECIMAL,
            "bytesMax": ClickHouseDB.DECIMAL,
            "bytesMin": ClickHouseDB.DECIMAL,
            "bytesPer": ClickHouseDB.DECIMAL,
            "bytesRate": ClickHouseDB.DECIMAL,
            "bytesRateAvg": ClickHouseDB.DECIMAL,
            "bytesRateMax": ClickHouseDB.DECIMAL,
            "bytesRateMin": ClickHouseDB.DECIMAL,
            "bytesRateSpct": ClickHouseDB.DECIMAL,
            "bytesRateThr": ClickHouseDB.DECIMAL,
            "bytesRateTr": ClickHouseDB.DECIMAL,
            "bytesSpct": ClickHouseDB.DECIMAL,
            "bytesThr": ClickHouseDB.DECIMAL,
            "bytesTr": ClickHouseDB.DECIMAL,
            "childAction": ClickHouseDB.STRING,
            "cnt": ClickHouseDB.DECIMAL,
            "lastCollOffset": ClickHouseDB.DECIMAL,
            "modTs": ClickHouseDB.STRING,
            "pktsAvg": ClickHouseDB.DECIMAL,
            "pktsCum": ClickHouseDB.DECIMAL,
            "pktsMax": ClickHouseDB.DECIMAL,
            "pktsMin": ClickHouseDB.DECIMAL,
            "pktsPer": ClickHouseDB.DECIMAL,
            "pktsRate": ClickHouseDB.DECIMAL,
            "pktsRateAvg": ClickHouseDB.DECIMAL,
            "pktsRateMax": ClickHouseDB.DECIMAL,
            "pktsRateMin": ClickHouseDB.DECIMAL,
            "pktsRateSpct": ClickHouseDB.DECIMAL,
            "pktsRateThr": ClickHouseDB.DECIMAL,
            "pktsRateTr": ClickHouseDB.DECIMAL,
            "pktsSpct": ClickHouseDB.DECIMAL,
            "pktsThr": ClickHouseDB.DECIMAL,
            "pktsTr": ClickHouseDB.DECIMAL,
            "repIntvEnd": ClickHouseDB.DATETIME,
            "repIntvStart": ClickHouseDB.DATETIME,
            "rn": ClickHouseDB.STRING,
            "status": ClickHouseDB.STRING,
            "utilAvg": ClickHouseDB.DECIMAL,
            "utilMax": ClickHouseDB.DECIMAL,
            "utilMin": ClickHouseDB.DECIMAL,
            "utilSpct": ClickHouseDB.DECIMAL,
            "utilThr": ClickHouseDB.DECIMAL,
            "utilTr": ClickHouseDB.DECIMAL
        }


class ApicInterfaceEventRepository(ApicOracleRepo):
    def __init__(self, db):
        super().__init__(db)
        self.table = 'APIC_INTERFACE_EVENT'
        self.db = db
        self.fields_to_reload = ["interface_id", "created"]
        self.date_field = "created"
        self.fields = {
            'affected': cx_Oracle.STRING,
            'cause': cx_Oracle.STRING,
            'changeSet': cx_Oracle.STRING,
            'childAction': cx_Oracle.STRING,
            'code': cx_Oracle.STRING,
            'created': cx_Oracle.STRING,
            'descr': cx_Oracle.STRING,
            'dn': cx_Oracle.STRING,
            'id': cx_Oracle.NUMBER,
            'ind': cx_Oracle.STRING,
            'modTs': cx_Oracle.STRING,
            'severity': cx_Oracle.STRING,
            'status': cx_Oracle.STRING,
            'trig': cx_Oracle.STRING,
            'txId': cx_Oracle.NUMBER,
            'e_user': cx_Oracle.STRING,
            'interface_id': cx_Oracle.STRING
        }


class ApicInterfaceFaultRepository(ApicOracleRepo):
    def __init__(self, db):
        super().__init__(db)
        self.table = 'APIC_INTERFACE_FAULT'
        self.db = db
        self.fields_to_reload = ["interface_id", "created"]
        self.date_field = "created"
        self.fields = {
            'ack': cx_Oracle.STRING,
            'affected': cx_Oracle.STRING,
            'cause': cx_Oracle.STRING,
            'changeSet': cx_Oracle.STRING,
            'childAction': cx_Oracle.STRING,
            'code': cx_Oracle.STRING,
            'created': cx_Oracle.STRING,
            'delegated': cx_Oracle.STRING,
            'delegatedFrom': cx_Oracle.STRING,
            'descr': cx_Oracle.STRING,
            'dn': cx_Oracle.STRING,
            'domain': cx_Oracle.STRING,
            'highestSeverity': cx_Oracle.STRING,
            'id': cx_Oracle.NUMBER,
            'ind': cx_Oracle.STRING,
            'lc': cx_Oracle.STRING,
            'modTs': cx_Oracle.STRING,
            'occur': cx_Oracle.NUMBER,
            'origSeverity': cx_Oracle.STRING,
            'prevSeverity': cx_Oracle.STRING,
            'rule': cx_Oracle.STRING,
            'severity': cx_Oracle.STRING,
            'status': cx_Oracle.STRING,
            'subject': cx_Oracle.STRING,
            'type': cx_Oracle.STRING,
            'interface_id': cx_Oracle.STRING
        }


class ApicInterfaceHealthRepository(ApicOracleRepo):
    def __init__(self, db):
        super().__init__(db)
        self.table = 'APIC_INTERFACE_HEALTH'
        self.db = db
        self.fields_to_reload = ["interface_id", "created"]
        self.date_field = "created"
        self.fields = {
            "affected": cx_Oracle.STRING,
            "childAction": cx_Oracle.STRING,
            "chng": cx_Oracle.NUMBER,
            "created": cx_Oracle.STRING,
            "cur": cx_Oracle.NUMBER,
            "descr": cx_Oracle.STRING,
            "dn": cx_Oracle.STRING,
            "id": cx_Oracle.NUMBER,
            "ind": cx_Oracle.STRING,
            "maxSev": cx_Oracle.STRING,
            "modTs": cx_Oracle.STRING,
            "prev": cx_Oracle.NUMBER,
            "severity": cx_Oracle.STRING,
            "status": cx_Oracle.STRING,
            "twScore": cx_Oracle.NUMBER,
            "interface_id": cx_Oracle.STRING
        }


# clickhouse

class ApicClickHouseInterfaceEventRepository(ApicClickHouseRepo):
    def __init__(self, db):
        super().__init__(db)
        self.table = 'apic_interface_event'
        self.db = db
        self.fields_to_reload = ["interface_id", "created"]
        self.date_field = "created"
        self.fields = {
            'affected': ClickHouseDB.STRING,
            'cause': ClickHouseDB.STRING,
            'changeSet': ClickHouseDB.STRING,
            'childAction': ClickHouseDB.STRING,
            'code': ClickHouseDB.STRING,
            'created': ClickHouseDB.DATETIME,
            'descr': ClickHouseDB.STRING,
            'dn': ClickHouseDB.STRING,
            'id': ClickHouseDB.DECIMAL,
            'ind': ClickHouseDB.STRING,
            'modTs': ClickHouseDB.STRING,
            'severity': ClickHouseDB.STRING,
            'status': ClickHouseDB.STRING,
            'trig': ClickHouseDB.STRING,
            'txId': ClickHouseDB.DECIMAL,
            'e_user': ClickHouseDB.STRING,
            'interface_id': ClickHouseDB.STRING
        }


class ApicClickHouseInterfaceFaultRepository(ApicClickHouseRepo):
    def __init__(self, db):
        super().__init__(db)
        self.table = 'apic_interface_fault'
        self.db = db
        self.fields_to_reload = ["interface_id", "created"]
        self.date_field = "created"
        self.fields = {
            'ack': ClickHouseDB.STRING,
            'affected': ClickHouseDB.STRING,
            'cause': ClickHouseDB.STRING,
            'changeSet': ClickHouseDB.STRING,
            'childAction': ClickHouseDB.STRING,
            'code': ClickHouseDB.STRING,
            'created': ClickHouseDB.DATETIME,
            'delegated': ClickHouseDB.STRING,
            'delegatedFrom': ClickHouseDB.STRING,
            'descr': ClickHouseDB.STRING,
            'dn': ClickHouseDB.STRING,
            'domain': ClickHouseDB.STRING,
            'highestSeverity': ClickHouseDB.STRING,
            'id': ClickHouseDB.DECIMAL,
            'ind': ClickHouseDB.STRING,
            'lc': ClickHouseDB.STRING,
            'modTs': ClickHouseDB.STRING,
            'occur': ClickHouseDB.DECIMAL,
            'origSeverity': ClickHouseDB.STRING,
            'prevSeverity': ClickHouseDB.STRING,
            'rule': ClickHouseDB.STRING,
            'severity': ClickHouseDB.STRING,
            'status': ClickHouseDB.STRING,
            'subject': ClickHouseDB.STRING,
            'type': ClickHouseDB.STRING,
            'interface_id': ClickHouseDB.STRING
        }


class ApicClickHouseInterfaceHealthRepository(ApicClickHouseRepo):
    def __init__(self, db):
        super().__init__(db)
        self.table = 'apic_interface_health'
        self.db = db
        self.fields_to_reload = ["interface_id", "created"]
        self.date_field = "created"
        self.fields = {
            "affected": ClickHouseDB.STRING,
            "childAction": ClickHouseDB.STRING,
            "chng": ClickHouseDB.DECIMAL,
            "created": ClickHouseDB.DATETIME,
            "cur": ClickHouseDB.DECIMAL,
            "descr": ClickHouseDB.STRING,
            "dn": ClickHouseDB.STRING,
            "id": ClickHouseDB.DECIMAL,
            "ind": ClickHouseDB.STRING,
            "maxSev": ClickHouseDB.STRING,
            "modTs": ClickHouseDB.STRING,
            "prev": ClickHouseDB.DECIMAL,
            "severity": ClickHouseDB.STRING,
            "status": ClickHouseDB.STRING,
            "twScore": ClickHouseDB.DECIMAL,
            "interface_id": ClickHouseDB.STRING
        }
