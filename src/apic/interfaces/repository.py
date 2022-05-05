import cx_Oracle

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


class ApicInterfaceIngressRepository:
    def __init__(self, db):
        self.table = 'APIC_INTERFACE_INGRESS_5_MIN'
        self.db = db

    def delete_where_collectiontime_between(self, interface_id, fecha1, fecha2):
        fecha1_str = fecha1.strftime('%Y%m%d%H%M%S')
        fecha2_str = fecha2.strftime('%Y%m%d%H%M%S')
        sql = f"DELETE FROM {self.table} WHERE interface_id='{interface_id}' AND repIntvEnd>=TO_DATE('{fecha1_str}', 'YYYYMMDDHH24MISS') and repIntvEnd<=TO_DATE('{fecha2_str}', 'YYYYMMDDHH24MISS')"
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(interface_id, bytesAvg, bytesCum, bytesMax, bytesMin, bytesPer, bytesRate, bytesRateAvg, bytesRateMax, bytesRateMin, bytesRateSpct, bytesRateThr, bytesRateTr, bytesSpct, bytesThr, bytesTr, childAction, cnt, lastCollOffset, modTs, pktsAvg, pktsCum, pktsMax, pktsMin, pktsPer, pktsRate, pktsRateAvg, pktsRateMax, pktsRateMin, pktsRateSpct, pktsRateThr, pktsRateTr, pktsSpct, pktsThr, pktsTr, repIntvEnd, repIntvStart, rn, status, utilAvg, utilMax, utilMin, utilSpct, utilThr, utilTr) VALUES(:interface_id, :bytesAvg, :bytesCum, :bytesMax, :bytesMin, :bytesPer, :bytesRate, :bytesRateAvg, :bytesRateMax, :bytesRateMin, :bytesRateSpct, :bytesRateThr, :bytesRateTr, :bytesSpct, :bytesThr, :bytesTr, :childAction, :cnt, :lastCollOffset, :modTs, :pktsAvg, :pktsCum, :pktsMax, :pktsMin, :pktsPer, :pktsRate, :pktsRateAvg, :pktsRateMax, :pktsRateMin, :pktsRateSpct, :pktsRateThr, :pktsRateTr, :pktsSpct, :pktsThr, :pktsTr, TO_DATE(:repIntvEnd, 'YYYY-MM-DD HH24:MI:SS'), TO_DATE(:repIntvStart, 'YYYY-MM-DD HH24:MI:SS'), :rn, :status, :utilAvg, :utilMax, :utilMin, :utilSpct, :utilThr, :utilTr)"
        bindings = {
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
        for i in range(len(registros_to_insert)):
            row = registros_to_insert[i]
            for field in bindings.keys():
                if bindings[field] == cx_Oracle.NUMBER:
                    if registros_to_insert[i][field] == '':
                        registros_to_insert[i][field] = None
                    else:
                        registros_to_insert[i][field] = float(registros_to_insert[i][field])

        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.save_from_array2(config, registros_to_insert)


class ApicInterfaceIngressErrorRepository:
    def __init__(self, db):
        self.table = 'APIC_INTERFACE_INGRESS_ERROR_5_MIN'
        self.db = db

    def delete_where_collectiontime_between(self, interface_id, fecha1, fecha2):
        fecha1_str = fecha1.strftime('%Y%m%d%H%M%S')
        fecha2_str = fecha2.strftime('%Y%m%d%H%M%S')
        sql = f"DELETE FROM {self.table} WHERE interface_id='{interface_id}' AND repIntvEnd>=TO_DATE('{fecha1_str}', 'YYYYMMDDHH24MISS') and repIntvEnd<=TO_DATE('{fecha2_str}', 'YYYYMMDDHH24MISS')"
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(interface_id, anyErrorAvg, anyErrorCum, anyErrorMax, anyErrorMin, anyErrorPer, anyErrorRate, anyErrorSpct, anyErrorThr, anyErrorTr, childAction, cnt, crcAvg, crcCountAvg, crcCountCum, crcCountMax, crcCountMin, crcCountPer, crcCountRate, crcCountRateAvg, crcCountRateMax, crcCountRateMin, crcCountRateSpct, crcCountRateThr, crcCountRateTr, crcCountSpct, crcCountThr, crcCountTr, crcMax, crcMin, crcSpct, crcThr, crcTr, discardAvg, discardCum, discardMax, discardMin, discardPer, discardRate, discardSpct, discardThr, discardTr, lastCollOffset, modTs, repIntvEnd, repIntvStart, rn, status) VALUES (:interface_id, :anyErrorAvg, :anyErrorCum, :anyErrorMax, :anyErrorMin, :anyErrorPer, :anyErrorRate, :anyErrorSpct, :anyErrorThr, :anyErrorTr, :childAction, :cnt, :crcAvg, :crcCountAvg, :crcCountCum, :crcCountMax, :crcCountMin, :crcCountPer, :crcCountRate, :crcCountRateAvg, :crcCountRateMax, :crcCountRateMin, :crcCountRateSpct, :crcCountRateThr, :crcCountRateTr, :crcCountSpct, :crcCountThr, :crcCountTr, :crcMax, :crcMin, :crcSpct, :crcThr, :crcTr, :discardAvg, :discardCum, :discardMax, :discardMin, :discardPer, :discardRate, :discardSpct, :discardThr, :discardTr, :lastCollOffset, :modTs, TO_DATE(:repIntvEnd, 'YYYY-MM-DD HH24:MI:SS'), TO_DATE(:repIntvStart, 'YYYY-MM-DD HH24:MI:SS'), :rn, :status)"

        bindings = {
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

        for i in range(len(registros_to_insert)):
            row = registros_to_insert[i]
            for field in bindings.keys():
                if bindings[field] == cx_Oracle.NUMBER:
                    if registros_to_insert[i][field] == '':
                        registros_to_insert[i][field] = None
                    else:
                        registros_to_insert[i][field] = float(registros_to_insert[i][field])

        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.save_from_array2(config, registros_to_insert)


class ApicInterfaceEgressRepository:
    def __init__(self, db):
        self.table = 'APIC_INTERFACE_EGRESS_5_MIN'
        self.db = db

    def delete_where_collectiontime_between(self, interface_id, fecha1, fecha2):
        fecha1_str = fecha1.strftime('%Y%m%d%H%M%S')
        fecha2_str = fecha2.strftime('%Y%m%d%H%M%S')
        sql = f"DELETE FROM {self.table} WHERE interface_id='{interface_id}' AND repIntvEnd>=TO_DATE('{fecha1_str}', 'YYYYMMDDHH24MISS') and repIntvEnd<=TO_DATE('{fecha2_str}', 'YYYYMMDDHH24MISS')"
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(interface_id, bytesAvg, bytesCum, bytesMax, bytesMin, bytesPer, bytesRate, bytesRateAvg, bytesRateMax, bytesRateMin, bytesRateSpct, bytesRateThr, bytesRateTr, bytesSpct, bytesThr, bytesTr, childAction, cnt, lastCollOffset, modTs, pktsAvg, pktsCum, pktsMax, pktsMin, pktsPer, pktsRate, pktsRateAvg, pktsRateMax, pktsRateMin, pktsRateSpct, pktsRateThr, pktsRateTr, pktsSpct, pktsThr, pktsTr, repIntvEnd, repIntvStart, rn, status, utilAvg, utilMax, utilMin, utilSpct, utilThr, utilTr) VALUES (:interface_id, :bytesAvg, :bytesCum, :bytesMax, :bytesMin, :bytesPer, :bytesRate, :bytesRateAvg, :bytesRateMax, :bytesRateMin, :bytesRateSpct, :bytesRateThr, :bytesRateTr, :bytesSpct, :bytesThr, :bytesTr, :childAction, :cnt, :lastCollOffset, :modTs, :pktsAvg, :pktsCum, :pktsMax, :pktsMin, :pktsPer, :pktsRate, :pktsRateAvg, :pktsRateMax, :pktsRateMin, :pktsRateSpct, :pktsRateThr, :pktsRateTr, :pktsSpct, :pktsThr, :pktsTr, TO_DATE(:repIntvEnd, 'YYYY-MM-DD HH24:MI:SS'), TO_DATE(:repIntvStart, 'YYYY-MM-DD HH24:MI:SS'), :rn, :status, :utilAvg, :utilMax, :utilMin, :utilSpct, :utilThr, :utilTr)"

        bindings = {
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

        for i in range(len(registros_to_insert)):
            row = registros_to_insert[i]
            for field in bindings.keys():
                if bindings[field] == cx_Oracle.NUMBER:
                    if registros_to_insert[i][field] == '':
                        registros_to_insert[i][field] = None
                    else:
                        registros_to_insert[i][field] = float(registros_to_insert[i][field])

        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.save_from_array2(config, registros_to_insert)