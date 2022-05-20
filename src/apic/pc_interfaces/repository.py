import cx_Oracle

class ApicPCInterfaceRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'APIC_PC_INTERFACE'

    def delete_by_topology_and_node(self, topology, node):
        sql = f"DELETE FROM {self.table} WHERE topology='{topology}' and NODE='{node}'"
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table} (topology, node, interface, activePorts, adminSt, autoNeg, bw, childAction, createTime, ctrl, delay, descr, dn, dot1qEtherType, ethpmCfgFailedBmp, ethpmCfgFailedTs, ethpmCfgState, fcotChannelNumber, fop, hashDist, id, inhBw, iod, isPlatformSupported, isReflectiveRelayCfgSupported, lastBundleMbr, lastBundleTime, lastSt, lastStCause, lastTime, lastUnbundleMbr, lastUnbundleTime, layer, lcOwn, lif, linkDebounce, linkLog, loadDeferStartTime, ltl, maxActive, maxLinks, mdix, medium, minLinks, modTs, int_mode, monPolDn, mtu, name, operChannelMode, osSum, pathSDescr, pcId, pcMode, pcmCfgFailedBmp, pcmCfgFailedTs, pcmCfgState, portT, prioFlowCtrl, reflectiveRelayEn, routerMac, rowSt, snmpTrapSt, spanMode, speed, status, suspMinlinks, switchingSt, trunkLog, usage, ethpmAggrIf_accessVlan, ethpmAggrIf_activeMbrs, ethpmAggrIf_allowedVlans, ethpmAggrIf_backplaneMac, ethpmAggrIf_bundleBupId, ethpmAggrIf_bundleIndex, ethpmAggrIf_cfgAccessVlan, ethpmAggrIf_cfgNativeVlan, ethpmAggrIf_childAction, ethpmAggrIf_currErrIndex, ethpmAggrIf_diags, ethpmAggrIf_encap, ethpmAggrIf_errDisTimerRunning, ethpmAggrIf_errVlanStatusHt, ethpmAggrIf_errVlans, ethpmAggrIf_hwBdId, ethpmAggrIf_hwResourceId, ethpmAggrIf_intfT, ethpmAggrIf_iod, ethpmAggrIf_lastErrors, ethpmAggrIf_lastLinkStChg, ethpmAggrIf_media, ethpmAggrIf_modTs, ethpmAggrIf_monPolDn, ethpmAggrIf_nativeVlan, ethpmAggrIf_numActivePorts, ethpmAggrIf_numMbrUp, ethpmAggrIf_numOfSI, ethpmAggrIf_operBitset, ethpmAggrIf_operDceMode, ethpmAggrIf_operDuplex, ethpmAggrIf_operEEERxWkTime, ethpmAggrIf_operEEEState, ethpmAggrIf_operEEETxWkTime, ethpmAggrIf_operErrDisQual, ethpmAggrIf_operFlowCtrl, ethpmAggrIf_operMdix, ethpmAggrIf_operMode, ethpmAggrIf_operModeDetail, ethpmAggrIf_operPhyEnSt, ethpmAggrIf_operRouterMac, ethpmAggrIf_operSpeed, ethpmAggrIf_operSt, ethpmAggrIf_operStQual, ethpmAggrIf_operStQualCode, ethpmAggrIf_operVlans, ethpmAggrIf_osSum, ethpmAggrIf_portCfgWaitFlags, ethpmAggrIf_primaryVlan, ethpmAggrIf_resetCtr, ethpmAggrIf_rn, ethpmAggrIf_siList, ethpmAggrIf_status, ethpmAggrIf_txT, ethpmAggrIf_usage, ethpmAggrIf_userCfgdFlags, ethpmAggrIf_vdcId) VALUES (:topology, :node, :interface, :activePorts, :adminSt, :autoNeg, :bw, :childAction, :createTime, :ctrl, :delay, :descr, :dn, :dot1qEtherType, :ethpmCfgFailedBmp, :ethpmCfgFailedTs, :ethpmCfgState, :fcotChannelNumber, :fop, :hashDist, :id, :inhBw, :iod, :isPlatformSupported, :isReflectiveRelayCfgSupported, :lastBundleMbr, :lastBundleTime, :lastSt, :lastStCause, :lastTime, :lastUnbundleMbr, :lastUnbundleTime, :layer, :lcOwn, :lif, :linkDebounce, :linkLog, :loadDeferStartTime, :ltl, :maxActive, :maxLinks, :mdix, :medium, :minLinks, TO_DATE(:modTs, 'YYYY-MM-DD HH24:MI:SS'), :int_mode, :monPolDn, :mtu, :name, :operChannelMode, :osSum, :pathSDescr, :pcId, :pcMode, :pcmCfgFailedBmp, :pcmCfgFailedTs, :pcmCfgState, :portT, :prioFlowCtrl, :reflectiveRelayEn, :routerMac, :rowSt, :snmpTrapSt, :spanMode, :speed, :status, :suspMinlinks, :switchingSt, :trunkLog, :usage, :ethpmAggrIf_accessVlan, :ethpmAggrIf_activeMbrs, :ethpmAggrIf_allowedVlans, :ethpmAggrIf_backplaneMac, :ethpmAggrIf_bundleBupId, :ethpmAggrIf_bundleIndex, :ethpmAggrIf_cfgAccessVlan, :ethpmAggrIf_cfgNativeVlan, :ethpmAggrIf_childAction, :ethpmAggrIf_currErrIndex, :ethpmAggrIf_diags, :ethpmAggrIf_encap, :ethpmAggrIf_errDisTimerRunning, :ethpmAggrIf_errVlanStatusHt, :ethpmAggrIf_errVlans, :ethpmAggrIf_hwBdId, :ethpmAggrIf_hwResourceId, :ethpmAggrIf_intfT, :ethpmAggrIf_iod, :ethpmAggrIf_lastErrors, TO_DATE(:ethpmAggrIf_lastLinkStChg, 'YYYY-MM-DD HH24:MI:SS'), :ethpmAggrIf_media, :ethpmAggrIf_modTs, :ethpmAggrIf_monPolDn, :ethpmAggrIf_nativeVlan, :ethpmAggrIf_numActivePorts, :ethpmAggrIf_numMbrUp, :ethpmAggrIf_numOfSI, :ethpmAggrIf_operBitset, :ethpmAggrIf_operDceMode, :ethpmAggrIf_operDuplex, :ethpmAggrIf_operEEERxWkTime, :ethpmAggrIf_operEEEState, :ethpmAggrIf_operEEETxWkTime, :ethpmAggrIf_operErrDisQual, :ethpmAggrIf_operFlowCtrl, :ethpmAggrIf_operMdix, :ethpmAggrIf_operMode, :ethpmAggrIf_operModeDetail, :ethpmAggrIf_operPhyEnSt, :ethpmAggrIf_operRouterMac, :ethpmAggrIf_operSpeed, :ethpmAggrIf_operSt, :ethpmAggrIf_operStQual, :ethpmAggrIf_operStQualCode, :ethpmAggrIf_operVlans, :ethpmAggrIf_osSum, :ethpmAggrIf_portCfgWaitFlags, :ethpmAggrIf_primaryVlan, :ethpmAggrIf_resetCtr, :ethpmAggrIf_rn, :ethpmAggrIf_siList, :ethpmAggrIf_status, :ethpmAggrIf_txT, :ethpmAggrIf_usage, :ethpmAggrIf_userCfgdFlags, :ethpmAggrIf_vdcId)"

        bindings = {
            'topology': cx_Oracle.STRING,
            'node': cx_Oracle.STRING,
            'interface': cx_Oracle.STRING,
            'activePorts': cx_Oracle.NUMBER,
            'adminSt': cx_Oracle.STRING,
            'autoNeg': cx_Oracle.STRING,
            'bw': cx_Oracle.NUMBER,
            'childAction': cx_Oracle.STRING,
            'createTime': cx_Oracle.STRING,
            'ctrl': cx_Oracle.STRING,
            'delay': cx_Oracle.NUMBER,
            'descr': cx_Oracle.STRING,
            'dn': cx_Oracle.STRING,
            'dot1qEtherType': cx_Oracle.STRING,
            'ethpmCfgFailedBmp': cx_Oracle.STRING,
            'ethpmCfgFailedTs': cx_Oracle.STRING,
            'ethpmCfgState': cx_Oracle.NUMBER,
            'fcotChannelNumber': cx_Oracle.STRING,
            'fop': cx_Oracle.STRING,
            'hashDist': cx_Oracle.STRING,
            'id': cx_Oracle.STRING,
            'inhBw': cx_Oracle.STRING,
            'iod': cx_Oracle.NUMBER,
            'isPlatformSupported': cx_Oracle.STRING,
            'isReflectiveRelayCfgSupported': cx_Oracle.STRING,
            'lastBundleMbr': cx_Oracle.STRING,
            'lastBundleTime': cx_Oracle.STRING,
            'lastSt': cx_Oracle.STRING,
            'lastStCause': cx_Oracle.STRING,
            'lastTime': cx_Oracle.STRING,
            'lastUnbundleMbr': cx_Oracle.STRING,
            'lastUnbundleTime': cx_Oracle.STRING,
            'layer': cx_Oracle.STRING,
            'lcOwn': cx_Oracle.STRING,
            'lif': cx_Oracle.NUMBER,
            'linkDebounce': cx_Oracle.NUMBER,
            'linkLog': cx_Oracle.STRING,
            'loadDeferStartTime': cx_Oracle.STRING,
            'ltl': cx_Oracle.NUMBER,
            'maxActive': cx_Oracle.NUMBER,
            'maxLinks': cx_Oracle.NUMBER,
            'mdix': cx_Oracle.STRING,
            'medium': cx_Oracle.STRING,
            'minLinks': cx_Oracle.NUMBER,
            'modTs': cx_Oracle.STRING,
            'int_mode': cx_Oracle.STRING,
            'monPolDn': cx_Oracle.STRING,
            'mtu': cx_Oracle.NUMBER,
            'name': cx_Oracle.STRING,
            'operChannelMode': cx_Oracle.STRING,
            'osSum': cx_Oracle.STRING,
            'pathSDescr': cx_Oracle.STRING,
            'pcId': cx_Oracle.NUMBER,
            'pcMode': cx_Oracle.STRING,
            'pcmCfgFailedBmp': cx_Oracle.STRING,
            'pcmCfgFailedTs': cx_Oracle.STRING,
            'pcmCfgState': cx_Oracle.NUMBER,
            'portT': cx_Oracle.STRING,
            'prioFlowCtrl': cx_Oracle.STRING,
            'reflectiveRelayEn': cx_Oracle.STRING,
            'routerMac': cx_Oracle.STRING,
            'rowSt': cx_Oracle.NUMBER,
            'snmpTrapSt': cx_Oracle.STRING,
            'spanMode': cx_Oracle.STRING,
            'speed': cx_Oracle.STRING,
            'status': cx_Oracle.STRING,
            'suspMinlinks': cx_Oracle.STRING,
            'switchingSt': cx_Oracle.STRING,
            'trunkLog': cx_Oracle.STRING,
            'usage': cx_Oracle.STRING,
            'ethpmAggrIf_accessVlan': cx_Oracle.STRING,
            'ethpmAggrIf_activeMbrs': cx_Oracle.STRING,
            'ethpmAggrIf_allowedVlans': cx_Oracle.STRING,
            'ethpmAggrIf_backplaneMac': cx_Oracle.STRING,
            'ethpmAggrIf_bundleBupId': cx_Oracle.NUMBER,
            'ethpmAggrIf_bundleIndex': cx_Oracle.STRING,
            'ethpmAggrIf_cfgAccessVlan': cx_Oracle.STRING,
            'ethpmAggrIf_cfgNativeVlan': cx_Oracle.STRING,
            'ethpmAggrIf_childAction': cx_Oracle.STRING,
            'ethpmAggrIf_currErrIndex': cx_Oracle.NUMBER,
            'ethpmAggrIf_diags': cx_Oracle.STRING,
            'ethpmAggrIf_encap': cx_Oracle.NUMBER,
            'ethpmAggrIf_errDisTimerRunning': cx_Oracle.STRING,
            'ethpmAggrIf_errVlanStatusHt': cx_Oracle.NUMBER,
            'ethpmAggrIf_errVlans': cx_Oracle.STRING,
            'ethpmAggrIf_hwBdId': cx_Oracle.NUMBER,
            'ethpmAggrIf_hwResourceId': cx_Oracle.NUMBER,
            'ethpmAggrIf_intfT': cx_Oracle.STRING,
            'ethpmAggrIf_iod': cx_Oracle.NUMBER,
            'ethpmAggrIf_lastErrors': cx_Oracle.NUMBER,
            'ethpmAggrIf_lastLinkStChg': cx_Oracle.STRING,
            'ethpmAggrIf_media': cx_Oracle.NUMBER,
            'ethpmAggrIf_modTs': cx_Oracle.STRING,
            'ethpmAggrIf_monPolDn': cx_Oracle.STRING,
            'ethpmAggrIf_nativeVlan': cx_Oracle.STRING,
            'ethpmAggrIf_numActivePorts': cx_Oracle.NUMBER,
            'ethpmAggrIf_numMbrUp': cx_Oracle.NUMBER,
            'ethpmAggrIf_numOfSI': cx_Oracle.NUMBER,
            'ethpmAggrIf_operBitset': cx_Oracle.STRING,
            'ethpmAggrIf_operDceMode': cx_Oracle.STRING,
            'ethpmAggrIf_operDuplex': cx_Oracle.STRING,
            'ethpmAggrIf_operEEERxWkTime': cx_Oracle.NUMBER,
            'ethpmAggrIf_operEEEState': cx_Oracle.STRING,
            'ethpmAggrIf_operEEETxWkTime': cx_Oracle.NUMBER,
            'ethpmAggrIf_operErrDisQual': cx_Oracle.STRING,
            'ethpmAggrIf_operFlowCtrl': cx_Oracle.NUMBER,
            'ethpmAggrIf_operMdix': cx_Oracle.NUMBER,
            'ethpmAggrIf_operMode': cx_Oracle.STRING,
            'ethpmAggrIf_operModeDetail': cx_Oracle.STRING,
            'ethpmAggrIf_operPhyEnSt': cx_Oracle.STRING,
            'ethpmAggrIf_operRouterMac': cx_Oracle.STRING,
            'ethpmAggrIf_operSpeed': cx_Oracle.STRING,
            'ethpmAggrIf_operSt': cx_Oracle.STRING,
            'ethpmAggrIf_operStQual': cx_Oracle.STRING,
            'ethpmAggrIf_operStQualCode': cx_Oracle.NUMBER,
            'ethpmAggrIf_operVlans': cx_Oracle.STRING,
            'ethpmAggrIf_osSum': cx_Oracle.STRING,
            'ethpmAggrIf_portCfgWaitFlags': cx_Oracle.NUMBER,
            'ethpmAggrIf_primaryVlan': cx_Oracle.STRING,
            'ethpmAggrIf_resetCtr': cx_Oracle.NUMBER,
            'ethpmAggrIf_rn': cx_Oracle.STRING,
            'ethpmAggrIf_siList': cx_Oracle.STRING,
            'ethpmAggrIf_status': cx_Oracle.STRING,
            'ethpmAggrIf_txT': cx_Oracle.STRING,
            'ethpmAggrIf_usage': cx_Oracle.STRING,
            'ethpmAggrIf_userCfgdFlags': cx_Oracle.NUMBER,
            'ethpmAggrIf_vdcId': cx_Oracle.NUMBER
        }

        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.save_from_array2(config, registros_to_insert)

class ApicPCInterfaceEgressRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'APIC_PC_INTERFACE_EGRESS_15_MIN'

    def delete_where_collectiontime_between(self, interface_id, fecha1, fecha2):
        fecha1_str = fecha1.strftime('%Y%m%d%H%M%S')
        fecha2_str = fecha2.strftime('%Y%m%d%H%M%S')
        sql = f"DELETE FROM {self.table} WHERE interface_id='{interface_id}' AND repIntvEnd>=TO_DATE('{fecha1_str}', 'YYYYMMDDHH24MISS') and repIntvEnd<=TO_DATE('{fecha2_str}', 'YYYYMMDDHH24MISS')"
        #self.db.query(sql)

    def delete_from_array_where_collectiontime_between(self, registros_to_delete):
        for i in range(len(registros_to_delete)):
            registros_to_delete[i]['fec_ini'] = registros_to_delete[i]['fec_ini'].strftime('%Y%m%d%H%M%S')
            registros_to_delete[i]['fec_fin'] = registros_to_delete[i]['fec_fin'].strftime('%Y%m%d%H%M%S')
        
        template = f"DELETE FROM {self.table} WHERE interface_id=:interface_id AND repIntvEnd>=TO_DATE(:fec_ini, 'YYYYMMDDHH24MISS') and repIntvEnd<=TO_DATE(:fec_fin, 'YYYYMMDDHH24MISS')"
        bindings = {'interface_id': cx_Oracle.STRING, 'fec_ini': cx_Oracle.STRING, 'fec_fin': cx_Oracle.STRING}
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.save_from_array2(config, registros_to_delete)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table} (bytesAvg, bytesCum, bytesMax, bytesMin, bytesPer, bytesRate, bytesRateAvg, bytesRateMax, bytesRateMin, bytesRateSpct, bytesRateThr, bytesRateTr, bytesSpct, bytesThr, bytesTr, childAction, cnt, lastCollOffset, modTs, pktsAvg, pktsCum, pktsMax, pktsMin, pktsPer, pktsRate, pktsRateAvg, pktsRateMax, pktsRateMin, pktsRateSpct, pktsRateThr, pktsRateTr, pktsSpct, pktsThr, pktsTr, repIntvEnd, repIntvStart, rn, status, utilAvg, utilMax, utilMin, utilSpct, utilThr, utilTr, interface_id) VALUES (:bytesAvg, :bytesCum, :bytesMax, :bytesMin, :bytesPer, :bytesRate, :bytesRateAvg, :bytesRateMax, :bytesRateMin, :bytesRateSpct, :bytesRateThr, :bytesRateTr, :bytesSpct, :bytesThr, :bytesTr, :childAction, :cnt, :lastCollOffset, :modTs, :pktsAvg, :pktsCum, :pktsMax, :pktsMin, :pktsPer, :pktsRate, :pktsRateAvg, :pktsRateMax, :pktsRateMin, :pktsRateSpct, :pktsRateThr, :pktsRateTr, :pktsSpct, :pktsThr, :pktsTr, to_date(:repIntvEnd, 'yyyy-mm-dd hh24:mi:ss'), to_date(:repIntvStart, 'yyyy-mm-dd hh24:mi:ss'), :rn, :status, :utilAvg, :utilMax, :utilMin, :utilSpct, :utilThr, :utilTr, :interface_id)"

        bindings = {'bytesAvg': cx_Oracle.NUMBER, 'bytesCum': cx_Oracle.NUMBER, 'bytesMax': cx_Oracle.NUMBER, 'bytesMin': cx_Oracle.NUMBER, 'bytesPer': cx_Oracle.NUMBER, 'bytesRate': cx_Oracle.NUMBER, 'bytesRateAvg': cx_Oracle.NUMBER, 'bytesRateMax': cx_Oracle.NUMBER, 'bytesRateMin': cx_Oracle.NUMBER, 'bytesRateSpct': cx_Oracle.NUMBER, 'bytesRateThr': cx_Oracle.STRING, 'bytesRateTr': cx_Oracle.NUMBER, 'bytesSpct': cx_Oracle.NUMBER, 'bytesThr': cx_Oracle.STRING, 'bytesTr': cx_Oracle.NUMBER, 'childAction': cx_Oracle.STRING, 'cnt': cx_Oracle.NUMBER, 'lastCollOffset': cx_Oracle.NUMBER, 'modTs': cx_Oracle.STRING, 'pktsAvg': cx_Oracle.NUMBER, 'pktsCum': cx_Oracle.NUMBER, 'pktsMax': cx_Oracle.NUMBER, 'pktsMin': cx_Oracle.NUMBER, 'pktsPer': cx_Oracle.NUMBER, 'pktsRate': cx_Oracle.NUMBER, 'pktsRateAvg': cx_Oracle.NUMBER, 'pktsRateMax': cx_Oracle.NUMBER, 'pktsRateMin': cx_Oracle.NUMBER, 'pktsRateSpct': cx_Oracle.NUMBER, 'pktsRateThr': cx_Oracle.STRING, 'pktsRateTr': cx_Oracle.NUMBER, 'pktsSpct': cx_Oracle.NUMBER, 'pktsThr': cx_Oracle.STRING, 'pktsTr': cx_Oracle.NUMBER, 'repIntvEnd': cx_Oracle.STRING, 'repIntvStart': cx_Oracle.STRING, 'rn': cx_Oracle.STRING, 'status': cx_Oracle.STRING, 'utilAvg': cx_Oracle.NUMBER, 'utilMax': cx_Oracle.NUMBER, 'utilMin': cx_Oracle.NUMBER, 'utilSpct': cx_Oracle.NUMBER, 'utilThr': cx_Oracle.STRING, 'utilTr': cx_Oracle.NUMBER, 'interface_id': cx_Oracle.STRING}

        registros_to_insert = self.db.map_data_by_bindings(registros_to_insert, bindings)
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.save_from_array2(config, registros_to_insert)

class ApicPCInterfaceIngressErrorRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'APIC_PC_INTERFACE_INGRESS_ERROR_15_MIN'

    def delete_from_array_where_collectiontime_between(self, registros_to_delete):
        for i in range(len(registros_to_delete)):
            registros_to_delete[i]['fec_ini'] = registros_to_delete[i]['fec_ini'].strftime('%Y%m%d%H%M%S')
            registros_to_delete[i]['fec_fin'] = registros_to_delete[i]['fec_fin'].strftime('%Y%m%d%H%M%S')
        
        template = f"DELETE FROM {self.table} WHERE interface_id=:interface_id AND repIntvEnd>=TO_DATE(:fec_ini, 'YYYYMMDDHH24MISS') and repIntvEnd<=TO_DATE(:fec_fin, 'YYYYMMDDHH24MISS')"
        bindings = {'interface_id': cx_Oracle.STRING, 'fec_ini': cx_Oracle.STRING, 'fec_fin': cx_Oracle.STRING}
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.save_from_array2(config, registros_to_delete)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(anyErrorAvg, anyErrorCum, anyErrorMax, anyErrorMin, anyErrorPer, anyErrorRate, anyErrorSpct, anyErrorThr, anyErrorTr, childAction, cnt, crcAvg, crcCountAvg, crcCountCum, crcCountMax, crcCountMin, crcCountPer, crcCountRate, crcCountRateAvg, crcCountRateMax, crcCountRateMin, crcCountRateSpct, crcCountRateThr, crcCountRateTr, crcCountSpct, crcCountThr, crcCountTr, crcMax, crcMin, crcSpct, crcThr, crcTr, discardAvg, discardCum, discardMax, discardMin, discardPer, discardRate, discardSpct, discardThr, discardTr, lastCollOffset, modTs, repIntvEnd, repIntvStart, rn, status, interface_id) VALUES (:anyErrorAvg, :anyErrorCum, :anyErrorMax, :anyErrorMin, :anyErrorPer, :anyErrorRate, :anyErrorSpct, :anyErrorThr, :anyErrorTr, :childAction, :cnt, :crcAvg, :crcCountAvg, :crcCountCum, :crcCountMax, :crcCountMin, :crcCountPer, :crcCountRate, :crcCountRateAvg, :crcCountRateMax, :crcCountRateMin, :crcCountRateSpct, :crcCountRateThr, :crcCountRateTr, :crcCountSpct, :crcCountThr, :crcCountTr, :crcMax, :crcMin, :crcSpct, :crcThr, :crcTr, :discardAvg, :discardCum, :discardMax, :discardMin, :discardPer, :discardRate, :discardSpct, :discardThr, :discardTr, :lastCollOffset, :modTs, to_date(:repIntvEnd, 'yyyy-mm-dd hh24:mi:ss'), to_date(:repIntvStart, 'yyyy-mm-dd hh24:mi:ss'), :rn, :status, :interface_id)"
        bindings = {
            'anyErrorAvg': cx_Oracle.NUMBER,
            'anyErrorCum': cx_Oracle.NUMBER,
            'anyErrorMax': cx_Oracle.NUMBER,
            'anyErrorMin': cx_Oracle.NUMBER,
            'anyErrorPer': cx_Oracle.NUMBER,
            'anyErrorRate': cx_Oracle.NUMBER,
            'anyErrorSpct': cx_Oracle.NUMBER,
            'anyErrorThr': cx_Oracle.STRING,
            'anyErrorTr': cx_Oracle.NUMBER,
            'childAction': cx_Oracle.STRING,
            'cnt': cx_Oracle.NUMBER,
            'crcAvg': cx_Oracle.NUMBER,
            'crcCountAvg': cx_Oracle.NUMBER,
            'crcCountCum': cx_Oracle.NUMBER,
            'crcCountMax': cx_Oracle.NUMBER,
            'crcCountMin': cx_Oracle.NUMBER,
            'crcCountPer': cx_Oracle.NUMBER,
            'crcCountRate': cx_Oracle.NUMBER,
            'crcCountRateAvg': cx_Oracle.NUMBER,
            'crcCountRateMax': cx_Oracle.NUMBER,
            'crcCountRateMin': cx_Oracle.NUMBER,
            'crcCountRateSpct': cx_Oracle.NUMBER,
            'crcCountRateThr': cx_Oracle.STRING,
            'crcCountRateTr': cx_Oracle.NUMBER,
            'crcCountSpct': cx_Oracle.NUMBER,
            'crcCountThr': cx_Oracle.STRING,
            'crcCountTr': cx_Oracle.NUMBER,
            'crcMax': cx_Oracle.NUMBER,
            'crcMin': cx_Oracle.NUMBER,
            'crcSpct': cx_Oracle.NUMBER,
            'crcThr': cx_Oracle.STRING,
            'crcTr': cx_Oracle.NUMBER,
            'discardAvg': cx_Oracle.NUMBER,
            'discardCum': cx_Oracle.NUMBER,
            'discardMax': cx_Oracle.NUMBER,
            'discardMin': cx_Oracle.NUMBER,
            'discardPer': cx_Oracle.NUMBER,
            'discardRate': cx_Oracle.NUMBER,
            'discardSpct': cx_Oracle.NUMBER,
            'discardThr': cx_Oracle.STRING,
            'discardTr': cx_Oracle.NUMBER,
            'lastCollOffset': cx_Oracle.NUMBER,
            'modTs': cx_Oracle.STRING,
            'repIntvEnd': cx_Oracle.STRING,
            'repIntvStart': cx_Oracle.STRING,
            'rn': cx_Oracle.STRING,
            'status': cx_Oracle.STRING,
            'interface_id': cx_Oracle.STRING
        }
        registros_to_insert = self.db.map_data_by_bindings(registros_to_insert, bindings)
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.save_from_array2(config, registros_to_insert)


class ApicPCInterfaceIngressRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'APIC_PC_INTERFACE_INGRESS_15_MIN'

    def delete_from_array_where_collectiontime_between(self, registros_to_delete):
        for i in range(len(registros_to_delete)):
            registros_to_delete[i]['fec_ini'] = registros_to_delete[i]['fec_ini'].strftime('%Y%m%d%H%M%S')
            registros_to_delete[i]['fec_fin'] = registros_to_delete[i]['fec_fin'].strftime('%Y%m%d%H%M%S')
        
        template = f"DELETE FROM {self.table} WHERE interface_id=:interface_id AND repIntvEnd>=TO_DATE(:fec_ini, 'YYYYMMDDHH24MISS') and repIntvEnd<=TO_DATE(:fec_fin, 'YYYYMMDDHH24MISS')"
        bindings = {'interface_id': cx_Oracle.STRING, 'fec_ini': cx_Oracle.STRING, 'fec_fin': cx_Oracle.STRING}
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.save_from_array2(config, registros_to_delete)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(bytesAvg, bytesCum, bytesMax, bytesMin, bytesPer, bytesRate, bytesRateAvg, bytesRateMax, bytesRateMin, bytesRateSpct, bytesRateThr, bytesRateTr, bytesSpct, bytesThr, bytesTr, childAction, cnt, lastCollOffset, modTs, pktsAvg, pktsCum, pktsMax, pktsMin, pktsPer, pktsRate, pktsRateAvg, pktsRateMax, pktsRateMin, pktsRateSpct, pktsRateThr, pktsRateTr, pktsSpct, pktsThr, pktsTr, repIntvEnd, repIntvStart, rn, status, utilAvg, utilMax, utilMin, utilSpct, utilThr, utilTr, interface_id) VALUES (:bytesAvg, :bytesCum, :bytesMax, :bytesMin, :bytesPer, :bytesRate, :bytesRateAvg, :bytesRateMax, :bytesRateMin, :bytesRateSpct, :bytesRateThr, :bytesRateTr, :bytesSpct, :bytesThr, :bytesTr, :childAction, :cnt, :lastCollOffset, :modTs, :pktsAvg, :pktsCum, :pktsMax, :pktsMin, :pktsPer, :pktsRate, :pktsRateAvg, :pktsRateMax, :pktsRateMin, :pktsRateSpct, :pktsRateThr, :pktsRateTr, :pktsSpct, :pktsThr, :pktsTr, to_date(:repIntvEnd, 'yyyy-mm-dd hh24:mi:ss'), to_date(:repIntvStart, 'yyyy-mm-dd hh24:mi:ss'), :rn, :status, :utilAvg, :utilMax, :utilMin, :utilSpct, :utilThr, :utilTr, :interface_id)"
        bindings = {
            'bytesAvg': cx_Oracle.NUMBER,
            'bytesCum': cx_Oracle.NUMBER,
            'bytesMax': cx_Oracle.NUMBER,
            'bytesMin': cx_Oracle.NUMBER,
            'bytesPer': cx_Oracle.NUMBER,
            'bytesRate': cx_Oracle.NUMBER,
            'bytesRateAvg': cx_Oracle.NUMBER,
            'bytesRateMax': cx_Oracle.NUMBER,
            'bytesRateMin': cx_Oracle.NUMBER,
            'bytesRateSpct': cx_Oracle.NUMBER,
            'bytesRateThr': cx_Oracle.STRING,
            'bytesRateTr': cx_Oracle.NUMBER,
            'bytesSpct': cx_Oracle.NUMBER,
            'bytesThr': cx_Oracle.STRING,
            'bytesTr': cx_Oracle.NUMBER,
            'childAction': cx_Oracle.STRING,
            'cnt': cx_Oracle.NUMBER,
            'lastCollOffset': cx_Oracle.NUMBER,
            'modTs': cx_Oracle.STRING,
            'pktsAvg': cx_Oracle.NUMBER,
            'pktsCum': cx_Oracle.NUMBER,
            'pktsMax': cx_Oracle.NUMBER,
            'pktsMin': cx_Oracle.NUMBER,
            'pktsPer': cx_Oracle.NUMBER,
            'pktsRate': cx_Oracle.NUMBER,
            'pktsRateAvg': cx_Oracle.NUMBER,
            'pktsRateMax': cx_Oracle.NUMBER,
            'pktsRateMin': cx_Oracle.NUMBER,
            'pktsRateSpct': cx_Oracle.NUMBER,
            'pktsRateThr': cx_Oracle.STRING,
            'pktsRateTr': cx_Oracle.NUMBER,
            'pktsSpct': cx_Oracle.NUMBER,
            'pktsThr': cx_Oracle.STRING,
            'pktsTr': cx_Oracle.NUMBER,
            'repIntvEnd': cx_Oracle.STRING,
            'repIntvStart': cx_Oracle.STRING,
            'rn': cx_Oracle.STRING,
            'status': cx_Oracle.STRING,
            'utilAvg': cx_Oracle.NUMBER,
            'utilMax': cx_Oracle.NUMBER,
            'utilMin': cx_Oracle.NUMBER,
            'utilSpct': cx_Oracle.NUMBER,
            'utilThr': cx_Oracle.STRING,
            'utilTr': cx_Oracle.NUMBER,
            'interface_id': cx_Oracle.STRING
        }
        registros_to_insert = self.db.map_data_by_bindings(registros_to_insert, bindings)
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.save_from_array2(config, registros_to_insert)