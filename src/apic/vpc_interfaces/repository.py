import cx_Oracle

class ApicVPCDomainRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'APIC_VPC_DOMAIN'

    def delete_by_topology_and_node(self, topology, node):
        sql = f"DELETE FROM {self.table} WHERE topology='{topology}' and NODE='{node}'"
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table} (batchedVpcInv, childAction, compatQual, compatQualStr, compatSt, deadIntvl, dn, dualActiveSt, id, issuFromVer, issuToVer, lacpRole, lcOwn, localMAC, localPrio, modTs, monPolDn, name, oldRole, operRole, operSt, orphanPortList, peerIp, peerMAC, peerPrio, peerSt, peerStQual, peerVersion, rolePrio, selfIniFabLinkFlapCnt, splitBrainTimerDuration, splitBrainTimerIsRun, splitBrainTimerStartTime, status, summOperRole, sysMac, sysPrio, tryRoleEstabTimerDuration, tryRoleEstabTimerIsRun, tryRoleEstabTimerStartTime, type2CompatQual, type2CompatQualStr, type2CompatSt, vIpAnnounceDelay, virtualIp, vpcCfgFailedBmp, vpcCfgFailedTs, vpcCfgState, vpcMAC, vpcPrio, topology, node, domain) VALUES (:batchedVpcInv, :childAction, :compatQual, :compatQualStr, :compatSt, :deadIntvl, :dn, :dualActiveSt, :id, :issuFromVer, :issuToVer, :lacpRole, :lcOwn, :localMAC, :localPrio, to_date(:modTs, 'yyyy-mm-dd hh24:mi:ss'), :monPolDn, :name, :oldRole, :operRole, :operSt, :orphanPortList, :peerIp, :peerMAC, :peerPrio, :peerSt, :peerStQual, :peerVersion, :rolePrio, :selfIniFabLinkFlapCnt, :splitBrainTimerDuration, :splitBrainTimerIsRun, to_date(:splitBrainTimerStartTime, 'yyyy-mm-dd hh24:mi:ss'), :status, :summOperRole, :sysMac, :sysPrio, :tryRoleEstabTimerDuration, :tryRoleEstabTimerIsRun, to_date(:tryRoleEstabTimerStartTime, 'yyyy-mm-dd hh24:mi:ss'), :type2CompatQual, :type2CompatQualStr, :type2CompatSt, :vIpAnnounceDelay, :virtualIp, :vpcCfgFailedBmp, :vpcCfgFailedTs, :vpcCfgState, :vpcMAC, :vpcPrio, :topology, :node, :domain)"
        bindings = {
            'batchedVpcInv': cx_Oracle.STRING,
            'childAction': cx_Oracle.STRING,
            'compatQual': cx_Oracle.NUMBER,
            'compatQualStr': cx_Oracle.STRING,
            'compatSt': cx_Oracle.STRING,
            'deadIntvl': cx_Oracle.NUMBER,
            'dn': cx_Oracle.STRING,
            'dualActiveSt': cx_Oracle.STRING,
            'id': cx_Oracle.STRING,
            'issuFromVer': cx_Oracle.STRING,
            'issuToVer': cx_Oracle.STRING,
            'lacpRole': cx_Oracle.STRING,
            'lcOwn': cx_Oracle.STRING,
            'localMAC': cx_Oracle.STRING,
            'localPrio': cx_Oracle.NUMBER,
            'modTs': cx_Oracle.STRING,
            'monPolDn': cx_Oracle.STRING,
            'name': cx_Oracle.STRING,
            'oldRole': cx_Oracle.STRING,
            'operRole': cx_Oracle.STRING,
            'operSt': cx_Oracle.STRING,
            'orphanPortList': cx_Oracle.NUMBER,
            'peerIp': cx_Oracle.STRING,
            'peerMAC': cx_Oracle.STRING,
            'peerPrio': cx_Oracle.NUMBER,
            'peerSt': cx_Oracle.STRING,
            'peerStQual': cx_Oracle.STRING,
            'peerVersion': cx_Oracle.NUMBER,
            'rolePrio': cx_Oracle.NUMBER,
            'selfIniFabLinkFlapCnt': cx_Oracle.NUMBER,
            'splitBrainTimerDuration': cx_Oracle.NUMBER,
            'splitBrainTimerIsRun': cx_Oracle.STRING,
            'splitBrainTimerStartTime': cx_Oracle.STRING,
            'status': cx_Oracle.STRING,
            'summOperRole': cx_Oracle.STRING,
            'sysMac': cx_Oracle.STRING,
            'sysPrio': cx_Oracle.NUMBER,
            'tryRoleEstabTimerDuration': cx_Oracle.NUMBER,
            'tryRoleEstabTimerIsRun': cx_Oracle.STRING,
            'tryRoleEstabTimerStartTime': cx_Oracle.STRING,
            'type2CompatQual': cx_Oracle.NUMBER,
            'type2CompatQualStr': cx_Oracle.STRING,
            'type2CompatSt': cx_Oracle.STRING,
            'vIpAnnounceDelay': cx_Oracle.NUMBER,
            'virtualIp': cx_Oracle.STRING,
            'vpcCfgFailedBmp': cx_Oracle.STRING,
            'vpcCfgFailedTs': cx_Oracle.STRING,
            'vpcCfgState': cx_Oracle.NUMBER,
            'vpcMAC': cx_Oracle.STRING,
            'vpcPrio': cx_Oracle.NUMBER,
            'topology': cx_Oracle.NUMBER,
            'node': cx_Oracle.NUMBER,
            'domain': cx_Oracle.NUMBER
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.save_from_array2(config, registros_to_insert)


class ApicVPCInterfaceRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'APIC_VPC_INTERFACE'

    def delete_by_topology_node_domain(self, topology, node, dom):
        sql = f"DELETE FROM {self.table} WHERE topology='{topology}' and NODE='{node}' and domain='{dom}'"
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        template = F"INSERT INTO {self.table}(accBndlGrpDn, cfgdAccessVlan, cfgdTrunkVlans, cfgdVlans, childAction, compatQual, compatQualStr, compatSt, descr, dn, fabEncMismatchVlans, fabEncMismatchVlansSet, fabricPathDn, id, lcOwn, localOperSt, modTs, monPolDn, name, pcMode, peerCfgdVlans, peerUpVlans, remoteOperSt, status, suspVlans, upVlans, usage, topology, node, domain, interface) VALUES (:accBndlGrpDn, :cfgdAccessVlan, :cfgdTrunkVlans, :cfgdVlans, :childAction, :compatQual, :compatQualStr, :compatSt, :descr, :dn, :fabEncMismatchVlans, :fabEncMismatchVlansSet, :fabricPathDn, :id, :lcOwn, :localOperSt, to_date(:modTs, 'yyyy-mm-dd hh24:mi:ss'), :monPolDn, :name, :pcMode, :peerCfgdVlans, :peerUpVlans, :remoteOperSt, :status, :suspVlans, :upVlans, :usage, :topology, :node, :domain, :interface)"
        bindings = {
            'accBndlGrpDn': cx_Oracle.STRING,
            'cfgdAccessVlan': cx_Oracle.STRING,
            'cfgdTrunkVlans': cx_Oracle.NUMBER,
            'cfgdVlans': cx_Oracle.STRING,
            'childAction': cx_Oracle.STRING,
            'compatQual': cx_Oracle.NUMBER,
            'compatQualStr': cx_Oracle.STRING,
            'compatSt': cx_Oracle.STRING,
            'descr': cx_Oracle.STRING,
            'dn': cx_Oracle.STRING,
            'fabEncMismatchVlans': cx_Oracle.STRING,
            'fabEncMismatchVlansSet': cx_Oracle.STRING,
            'fabricPathDn': cx_Oracle.STRING,
            'id': cx_Oracle.STRING,
            'lcOwn': cx_Oracle.STRING,
            'localOperSt': cx_Oracle.STRING,
            'modTs': cx_Oracle.STRING,
            'monPolDn': cx_Oracle.STRING,
            'name': cx_Oracle.STRING,
            'pcMode': cx_Oracle.STRING,
            'peerCfgdVlans': cx_Oracle.STRING,
            'peerUpVlans': cx_Oracle.STRING,
            'remoteOperSt': cx_Oracle.STRING,
            'status': cx_Oracle.STRING,
            'suspVlans': cx_Oracle.STRING,
            'upVlans': cx_Oracle.STRING,
            'usage': cx_Oracle.STRING,
            'topology': cx_Oracle.NUMBER,
            'node': cx_Oracle.NUMBER,
            'domain': cx_Oracle.NUMBER,
            'interface': cx_Oracle.NUMBER
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 100000}
        self.db.save_from_array2(config, registros_to_insert)