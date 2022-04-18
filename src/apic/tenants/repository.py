import cx_Oracle

class ApicTenantRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'APIC_TENANT'

    def delete_all(self):
        sql = f'DELETE FROM {self.table}'
        self.db.query(sql)
    
    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table} (OptimizeWanBandwidth, annotation, arpFlood, bcastP, childAction, configIssues, descr, dn, epClear, epMoveDetectMode, extMngdBy, hostBasedRouting, intersiteBumTrafficAllow, intersiteL2Stretch, ipLearning, ipv6McastAllow, lcOwn, limitIpLearnToSubnets, llAddr, mac, mcastAllow, modTs, monPolDn, mtu, multiDstPktAct, name, nameAlias, ownerKey, ownerTag, pcTag, scope, seg, status, type, tn_uid, unicastRoute, unkMacUcastAct, unkMcastAct, v6unkMcastAct, vmac, fvSubnet_annotation, fvSubnet_childAction, fvSubnet_ctrl, fvSubnet_descr, fvSubnet_extMngdBy, fvSubnet_ip, fvSubnet_lcOwn, fvSubnet_modTs, fvSubnet_monPolDn, fvSubnet_name, fvSubnet_nameAlias, fvSubnet_preferred, fvSubnet_rn, fvSubnet_scope, fvSubnet_status, fvSubnet_uid, fvSubnet_virtual, fvRsCtx_annotation, fvRsCtx_childAction, fvRsCtx_extMngdBy, fvRsCtx_forceResolve, fvRsCtx_lcOwn, fvRsCtx_modTs, fvRsCtx_monPolDn, fvRsCtx_rType, fvRsCtx_rn, fvRsCtx_state, fvRsCtx_stateQual, fvRsCtx_status, fvRsCtx_tCl, fvRsCtx_tContextDn, fvRsCtx_tDn, fvRsCtx_tRn, fvRsCtx_tType, fvRsCtx_tnFvCtxName, fvRsCtx_uid) VALUES (:OptimizeWanBandwidth, :annotation, :arpFlood, :bcastP, :childAction, :configIssues, :descr, :dn, :epClear, :epMoveDetectMode, :extMngdBy, :hostBasedRouting, :intersiteBumTrafficAllow, :intersiteL2Stretch, :ipLearning, :ipv6McastAllow, :lcOwn, :limitIpLearnToSubnets, :llAddr, :mac, :mcastAllow, TO_DATE(:modTs, 'YYYY-MM-DD HH24:MI:SS'), :monPolDn, :mtu, :multiDstPktAct, :name, :nameAlias, :ownerKey, :ownerTag, :pcTag, :scope, :seg, :status, :type, :tn_uid, :unicastRoute, :unkMacUcastAct, :unkMcastAct, :v6unkMcastAct, :vmac, :fvSubnet_annotation, :fvSubnet_childAction, :fvSubnet_ctrl, :fvSubnet_descr, :fvSubnet_extMngdBy, :fvSubnet_ip, :fvSubnet_lcOwn, TO_DATE(:fvSubnet_modTs, 'YYYY-MM-DD HH24:MI:SS'), :fvSubnet_monPolDn, :fvSubnet_name, :fvSubnet_nameAlias, :fvSubnet_preferred, :fvSubnet_rn, :fvSubnet_scope, :fvSubnet_status, :fvSubnet_uid, :fvSubnet_virtual, :fvRsCtx_annotation, :fvRsCtx_childAction, :fvRsCtx_extMngdBy, :fvRsCtx_forceResolve, :fvRsCtx_lcOwn, TO_DATE(:fvRsCtx_modTs, 'YYYY-MM-DD HH24:MI:SS'), :fvRsCtx_monPolDn, :fvRsCtx_rType, :fvRsCtx_rn, :fvRsCtx_state, :fvRsCtx_stateQual, :fvRsCtx_status, :fvRsCtx_tCl, :fvRsCtx_tContextDn, :fvRsCtx_tDn, :fvRsCtx_tRn, :fvRsCtx_tType, :fvRsCtx_tnFvCtxName, :fvRsCtx_uid)"
        bindings = {
            'OptimizeWanBandwidth': cx_Oracle.STRING,
            'annotation': cx_Oracle.STRING,
            'arpFlood': cx_Oracle.STRING,
            'bcastP': cx_Oracle.STRING,
            'childAction': cx_Oracle.STRING,
            'configIssues': cx_Oracle.STRING,
            'descr': cx_Oracle.STRING,
            'dn': cx_Oracle.STRING,
            'epClear': cx_Oracle.STRING,
            'epMoveDetectMode': cx_Oracle.STRING,
            'extMngdBy': cx_Oracle.STRING,
            'hostBasedRouting': cx_Oracle.STRING,
            'intersiteBumTrafficAllow': cx_Oracle.STRING,
            'intersiteL2Stretch': cx_Oracle.STRING,
            'ipLearning': cx_Oracle.STRING,
            'ipv6McastAllow': cx_Oracle.STRING,
            'lcOwn': cx_Oracle.STRING,
            'limitIpLearnToSubnets': cx_Oracle.STRING,
            'llAddr': cx_Oracle.STRING,
            'mac': cx_Oracle.STRING,
            'mcastAllow': cx_Oracle.STRING,
            'modTs': cx_Oracle.STRING,
            'monPolDn': cx_Oracle.STRING,
            'mtu': cx_Oracle.STRING,
            'multiDstPktAct': cx_Oracle.STRING,
            'name': cx_Oracle.STRING,
            'nameAlias': cx_Oracle.STRING,
            'ownerKey': cx_Oracle.STRING,
            'ownerTag': cx_Oracle.STRING,
            'pcTag': cx_Oracle.NUMBER,
            'scope': cx_Oracle.NUMBER,
            'seg': cx_Oracle.NUMBER,
            'status': cx_Oracle.STRING,
            'type': cx_Oracle.STRING,
            'tn_uid': cx_Oracle.STRING,
            'unicastRoute': cx_Oracle.STRING,
            'unkMacUcastAct': cx_Oracle.STRING,
            'unkMcastAct': cx_Oracle.STRING,
            'v6unkMcastAct': cx_Oracle.STRING,
            'vmac': cx_Oracle.STRING,
            'fvSubnet_annotation': cx_Oracle.STRING,
            'fvSubnet_childAction': cx_Oracle.STRING,
            'fvSubnet_ctrl': cx_Oracle.STRING,
            'fvSubnet_descr': cx_Oracle.STRING,
            'fvSubnet_extMngdBy': cx_Oracle.STRING,
            'fvSubnet_ip': cx_Oracle.STRING,
            'fvSubnet_lcOwn': cx_Oracle.STRING,
            'fvSubnet_modTs': cx_Oracle.STRING,
            'fvSubnet_monPolDn': cx_Oracle.STRING,
            'fvSubnet_name': cx_Oracle.STRING,
            'fvSubnet_nameAlias': cx_Oracle.STRING,
            'fvSubnet_preferred': cx_Oracle.STRING,
            'fvSubnet_rn': cx_Oracle.STRING,
            'fvSubnet_scope': cx_Oracle.STRING,
            'fvSubnet_status': cx_Oracle.STRING,
            'fvSubnet_uid': cx_Oracle.STRING,
            'fvSubnet_virtual': cx_Oracle.STRING,
            'fvRsCtx_annotation': cx_Oracle.STRING,
            'fvRsCtx_childAction': cx_Oracle.STRING,
            'fvRsCtx_extMngdBy': cx_Oracle.STRING,
            'fvRsCtx_forceResolve': cx_Oracle.STRING,
            'fvRsCtx_lcOwn': cx_Oracle.STRING,
            'fvRsCtx_modTs': cx_Oracle.STRING,
            'fvRsCtx_monPolDn': cx_Oracle.STRING,
            'fvRsCtx_rType': cx_Oracle.STRING,
            'fvRsCtx_rn': cx_Oracle.STRING,
            'fvRsCtx_state': cx_Oracle.STRING,
            'fvRsCtx_stateQual': cx_Oracle.STRING,
            'fvRsCtx_status': cx_Oracle.STRING,
            'fvRsCtx_tCl': cx_Oracle.STRING,
            'fvRsCtx_tContextDn': cx_Oracle.STRING,
            'fvRsCtx_tDn': cx_Oracle.STRING,
            'fvRsCtx_tRn': cx_Oracle.STRING,
            'fvRsCtx_tType': cx_Oracle.STRING,
            'fvRsCtx_tnFvCtxName': cx_Oracle.STRING,
            'fvRsCtx_uid': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 10000}
        self.db.save_from_array2(config, registros_to_insert)


class ApicTenantEpgRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'APIC_TENANT_EPG'

    def delete_all(self):
        sql = f'DELETE FROM {self.table}'
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table} (annotation, childAction, configIssues, configSt, descr, dn, exceptionTag, extMngdBy, floodOnEncap, fwdCtrl, hasMcastSource, isAttrBasedEPg, isSharedSrvMsiteEPg, lcOwn, matchT, modTs, monPolDn, name, nameAlias, pcEnfPref, pcTag, prefGrMemb, prio, scope, shutdown, status, triggerSt, txId, tn_uid, fvRsBd_annotation, fvRsBd_childAction, fvRsBd_extMngdBy, fvRsBd_forceResolve, fvRsBd_lcOwn, fvRsBd_modTs, fvRsBd_monPolDn, fvRsBd_rType, fvRsBd_rn, fvRsBd_state, fvRsBd_stateQual, fvRsBd_status, fvRsBd_tCl, fvRsBd_tContextDn, fvRsBd_tDn, fvRsBd_tRn, fvRsBd_tType, fvRsBd_tnFvBDName, fvRsBd_uid) VALUES (:annotation, :childAction, :configIssues, :configSt, :descr, :dn, :exceptionTag, :extMngdBy, :floodOnEncap, :fwdCtrl, :hasMcastSource, :isAttrBasedEPg, :isSharedSrvMsiteEPg, :lcOwn, :matchT, TO_DATE(:modTs, 'YYYY-MM-DD HH24:MI:SS'), :monPolDn, :name, :nameAlias, :pcEnfPref, :pcTag, :prefGrMemb, :prio, :scope, :shutdown, :status, :triggerSt, :txId, :tn_uid, :fvRsBd_annotation, :fvRsBd_childAction, :fvRsBd_extMngdBy, :fvRsBd_forceResolve, :fvRsBd_lcOwn, TO_DATE(:fvRsBd_modTs, 'YYYY-MM-DD HH24:MI:SS'), :fvRsBd_monPolDn, :fvRsBd_rType, :fvRsBd_rn, :fvRsBd_state, :fvRsBd_stateQual, :fvRsBd_status, :fvRsBd_tCl, :fvRsBd_tContextDn, :fvRsBd_tDn, :fvRsBd_tRn, :fvRsBd_tType, :fvRsBd_tnFvBDName, :fvRsBd_uid)"
        bindings = {
            'annotation': cx_Oracle.STRING,
            'childAction': cx_Oracle.STRING,
            'configIssues': cx_Oracle.STRING,
            'configSt': cx_Oracle.STRING,
            'descr': cx_Oracle.STRING,
            'dn': cx_Oracle.STRING,
            'exceptionTag': cx_Oracle.STRING,
            'extMngdBy': cx_Oracle.STRING,
            'floodOnEncap': cx_Oracle.STRING,
            'fwdCtrl': cx_Oracle.STRING,
            'hasMcastSource': cx_Oracle.STRING,
            'isAttrBasedEPg': cx_Oracle.STRING,
            'isSharedSrvMsiteEPg': cx_Oracle.STRING,
            'lcOwn': cx_Oracle.STRING,
            'matchT': cx_Oracle.STRING,
            'modTs': cx_Oracle.STRING,
            'monPolDn': cx_Oracle.STRING,
            'name': cx_Oracle.STRING,
            'nameAlias': cx_Oracle.STRING,
            'pcEnfPref': cx_Oracle.STRING,
            'pcTag': cx_Oracle.STRING,
            'prefGrMemb': cx_Oracle.STRING,
            'prio': cx_Oracle.STRING,
            'scope': cx_Oracle.STRING,
            'shutdown': cx_Oracle.STRING,
            'status': cx_Oracle.STRING,
            'triggerSt': cx_Oracle.STRING,
            'txId': cx_Oracle.STRING,
            'tn_uid': cx_Oracle.STRING,
            'fvRsBd_annotation': cx_Oracle.STRING,
            'fvRsBd_childAction': cx_Oracle.STRING,
            'fvRsBd_extMngdBy': cx_Oracle.STRING,
            'fvRsBd_forceResolve': cx_Oracle.STRING,
            'fvRsBd_lcOwn': cx_Oracle.STRING,
            'fvRsBd_modTs': cx_Oracle.STRING,
            'fvRsBd_monPolDn': cx_Oracle.STRING,
            'fvRsBd_rType': cx_Oracle.STRING,
            'fvRsBd_rn': cx_Oracle.STRING,
            'fvRsBd_state': cx_Oracle.STRING,
            'fvRsBd_stateQual': cx_Oracle.STRING,
            'fvRsBd_status': cx_Oracle.STRING,
            'fvRsBd_tCl': cx_Oracle.STRING,
            'fvRsBd_tContextDn': cx_Oracle.STRING,
            'fvRsBd_tDn': cx_Oracle.STRING,
            'fvRsBd_tRn': cx_Oracle.STRING,
            'fvRsBd_tType': cx_Oracle.STRING,
            'fvRsBd_tnFvBDName': cx_Oracle.STRING,
            'fvRsBd_uid': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 10000}
        self.db.save_from_array2(config, registros_to_insert)



class ApicTenantL3outRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'APIC_TENANT_L3OUT'

    def delete_all(self):
        sql = f'DELETE FROM {self.table}'
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table} (annotation, childAction, descr, dn, enforceRtctrl, extMngdBy, lcOwn, modTs, monPolDn, name, nameAlias, ownerKey, ownerTag, status, targetDscp, tn_uid, bgpExtP_annotation, bgpExtP_childAction, bgpExtP_descr, bgpExtP_extMngdBy, bgpExtP_lcOwn, bgpExtP_modTs, bgpExtP_monPolDn, bgpExtP_name, bgpExtP_nameAlias, bgpExtP_rn, bgpExtP_status, bgpExtP_uid, l3extRsEctx_annotation, l3extRsEctx_childAction, l3extRsEctx_extMngdBy, l3extRsEctx_forceResolve, l3extRsEctx_lcOwn, l3extRsEctx_modTs, l3extRsEctx_monPolDn, l3extRsEctx_rType, l3extRsEctx_rn, l3extRsEctx_state, l3extRsEctx_stateQual, l3extRsEctx_status, l3extRsEctx_tCl, l3extRsEctx_tContextDn, l3extRsEctx_tDn, l3extRsEctx_tRn, l3extRsEctx_tType, l3extRsEctx_tnFvCtxName, l3extRsEctx_uid) VALUES (:annotation, :childAction, :descr, :dn, :enforceRtctrl, :extMngdBy, :lcOwn, TO_DATE(:modTs, 'YYYY-MM-DD HH24:MI:SS'), :monPolDn, :name, :nameAlias, :ownerKey, :ownerTag, :status, :targetDscp, :tn_uid, :bgpExtP_annotation, :bgpExtP_childAction, :bgpExtP_descr, :bgpExtP_extMngdBy, :bgpExtP_lcOwn, TO_DATE(:bgpExtP_modTs, 'YYYY-MM-DD HH24:MI:SS'), :bgpExtP_monPolDn, :bgpExtP_name, :bgpExtP_nameAlias, :bgpExtP_rn, :bgpExtP_status, :bgpExtP_uid, :l3extRsEctx_annotation, :l3extRsEctx_childAction, :l3extRsEctx_extMngdBy, :l3extRsEctx_forceResolve, :l3extRsEctx_lcOwn, TO_DATE(:l3extRsEctx_modTs, 'YYYY-MM-DD HH24:MI:SS'), :l3extRsEctx_monPolDn, :l3extRsEctx_rType, :l3extRsEctx_rn, :l3extRsEctx_state, :l3extRsEctx_stateQual, :l3extRsEctx_status, :l3extRsEctx_tCl, :l3extRsEctx_tContextDn, :l3extRsEctx_tDn, :l3extRsEctx_tRn, :l3extRsEctx_tType, :l3extRsEctx_tnFvCtxName, :l3extRsEctx_uid)"
        bindings = {
            'annotation': cx_Oracle.STRING,
            'childAction': cx_Oracle.STRING,
            'descr': cx_Oracle.STRING,
            'dn': cx_Oracle.STRING,
            'enforceRtctrl': cx_Oracle.STRING,
            'extMngdBy': cx_Oracle.STRING,
            'lcOwn': cx_Oracle.STRING,
            'modTs': cx_Oracle.STRING,
            'monPolDn': cx_Oracle.STRING,
            'name': cx_Oracle.STRING,
            'nameAlias': cx_Oracle.STRING,
            'ownerKey': cx_Oracle.STRING,
            'ownerTag': cx_Oracle.STRING,
            'status': cx_Oracle.STRING,
            'targetDscp': cx_Oracle.STRING,
            'tn_uid': cx_Oracle.STRING,
            'bgpExtP_annotation': cx_Oracle.STRING,
            'bgpExtP_childAction': cx_Oracle.STRING,
            'bgpExtP_descr': cx_Oracle.STRING,
            'bgpExtP_extMngdBy': cx_Oracle.STRING,
            'bgpExtP_lcOwn': cx_Oracle.STRING,
            'bgpExtP_modTs': cx_Oracle.STRING,
            'bgpExtP_monPolDn': cx_Oracle.STRING,
            'bgpExtP_name': cx_Oracle.STRING,
            'bgpExtP_nameAlias': cx_Oracle.STRING,
            'bgpExtP_rn': cx_Oracle.STRING,
            'bgpExtP_status': cx_Oracle.STRING,
            'bgpExtP_uid': cx_Oracle.STRING,
            'l3extRsEctx_annotation': cx_Oracle.STRING,
            'l3extRsEctx_childAction': cx_Oracle.STRING,
            'l3extRsEctx_extMngdBy': cx_Oracle.STRING,
            'l3extRsEctx_forceResolve': cx_Oracle.STRING,
            'l3extRsEctx_lcOwn': cx_Oracle.STRING,
            'l3extRsEctx_modTs': cx_Oracle.STRING,
            'l3extRsEctx_monPolDn': cx_Oracle.STRING,
            'l3extRsEctx_rType': cx_Oracle.STRING,
            'l3extRsEctx_rn': cx_Oracle.STRING,
            'l3extRsEctx_state': cx_Oracle.STRING,
            'l3extRsEctx_stateQual': cx_Oracle.STRING,
            'l3extRsEctx_status': cx_Oracle.STRING,
            'l3extRsEctx_tCl': cx_Oracle.STRING,
            'l3extRsEctx_tContextDn': cx_Oracle.STRING,
            'l3extRsEctx_tDn': cx_Oracle.STRING,
            'l3extRsEctx_tRn': cx_Oracle.STRING,
            'l3extRsEctx_tType': cx_Oracle.STRING,
            'l3extRsEctx_tnFvCtxName': cx_Oracle.STRING,
            'l3extRsEctx_uid': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 10000}
        self.db.save_from_array2(config, registros_to_insert)