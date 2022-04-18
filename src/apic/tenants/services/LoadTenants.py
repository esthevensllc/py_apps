import datetime

class LoadTenants:
    def __init__(self, repository, tenant_epg_repo, tenant_l3out_repo, apic_service):
        self.repository = repository
        self.tenant_epg_repo = tenant_epg_repo
        self.tenant_l3out_repo = tenant_l3out_repo
        self.apic_service = apic_service
        self.fvSubnet_attr = {
            "annotation": None,
            "childAction": None,
            "ctrl": None,
            "descr": None,
            "extMngdBy": None,
            "ip": None,
            "lcOwn": None,
            "modTs": None,
            "monPolDn": None,
            "name": None,
            "nameAlias": None,
            "preferred": None,
            "rn": None,
            "scope": None,
            "status": None,
            "uid": None,
            "virtual": None
        }
        self.fvRsCtx_attr = {
            "annotation": None,
            "childAction": None,
            "extMngdBy": None,
            "forceResolve": None,
            "lcOwn": None,
            "modTs": None,
            "monPolDn": None,
            "rType": None,
            "rn": None,
            "state": None,
            "stateQual": None,
            "status": None,
            "tCl": None,
            "tContextDn": None,
            "tDn": None,
            "tRn": None,
            "tType": None,
            "tnFvCtxName": None,
            "uid": None
        }
        self.fvRsBd_attr = {
            'fvRsBd_annotation': None,
            'fvRsBd_childAction': None,
            'fvRsBd_extMngdBy': None,
            'fvRsBd_forceResolve': None,
            'fvRsBd_lcOwn': None,
            'fvRsBd_modTs': None,
            'fvRsBd_monPolDn': None,
            'fvRsBd_rType': None,
            'fvRsBd_rn': None,
            'fvRsBd_state': None,
            'fvRsBd_stateQual': None,
            'fvRsBd_status': None,
            'fvRsBd_tCl': None,
            'fvRsBd_tContextDn': None,
            'fvRsBd_tDn': None,
            'fvRsBd_tRn': None,
            'fvRsBd_tType': None,
            'fvRsBd_tnFvBDName': None,
            'fvRsBd_uid': None
        }

        # L3OUT
        self.bgpExtP_attr = {
            "annotation": None,
            "childAction": None,
            "descr": None,
            "extMngdBy": None,
            "lcOwn": None,
            "modTs": None,
            "monPolDn": None,
            "name": None,
            "nameAlias": None,
            "rn": None,
            "status": None,
            "uid": None
        }

        self.l3extRsEctx_attr = {
            "annotation": None,
            "childAction": None,
            "extMngdBy": None,
            "forceResolve": None,
            "lcOwn": None,
            "modTs": None,
            "monPolDn": None,
            "rType": None,
            "rn": None,
            "state": None,
            "stateQual": None,
            "status": None,
            "tCl": None,
            "tContextDn": None,
            "tDn": None,
            "tRn": None,
            "tType": None,
            "tnFvCtxName": None,
            "uid": None
        }

    def execute(self):
        # Bridge domains
        params = {
            'query-target': 'children',
            'target-subtree-class': 'fvBD',
            'query-target-filter': 'not(wcard(fvBD.dn,"__ui_"))',
            'rsp-subtree': 'full',
            'rsp-subtree-class': 'fvSubnet,fvRsCtx',
            #'subscription': 'yes',
            'order-by': 'fvBD.name|asc',
            #'page': '0',
            #'page-size': '100000'
        }
        response = self.apic_service.get(f'node/mo/uni/tn-TN_CLARO_IT.json', {'params': params})
        response = response.json()

        registros_to_insert = []
        for row in response['imdata']:
            # print(row.keys())
            # break
            to_add = row['fvBD']['attributes']
            fvSubnet = self.fvSubnet_attr.copy()
            fvRsCtx = self.fvRsCtx_attr.copy()
            childrens = row['fvBD']['children']
            for child in childrens:
                if 'fvSubnet' in child.keys():
                    fvSubnet = child['fvSubnet']['attributes']
                if 'fvRsCtx' in child.keys():
                    fvRsCtx = child['fvRsCtx']['attributes']
            
            for attr in fvSubnet.keys():
                to_add[f'fvSubnet_{attr}'] = fvSubnet[attr]
            
            for attr in fvRsCtx.keys():
                to_add[f'fvRsCtx_{attr}'] = fvRsCtx[attr]

            to_add['modTs'] = self.utc_to_loaddate(to_add['modTs'])
            to_add['fvSubnet_modTs'] = self.utc_to_loaddate(to_add['fvSubnet_modTs'])
            to_add['fvRsCtx_modTs'] = self.utc_to_loaddate(to_add['fvRsCtx_modTs'])
            to_add['tn_uid'] = to_add['uid']
            to_add.pop('uid')
            registros_to_insert.append(to_add)
        # print(registros_to_insert[0])
        self.repository.delete_all()
        self.repository.insert_from_array(registros_to_insert)

        # EPG
        params = {
            'query-target': 'subtree',
            'target-subtree-class': 'fvAEPg',
            'query-target-filter': 'and(not(wcard(fvAEPg.dn,"__ui_")),eq(fvAEPg.isAttrBasedEPg,"false"))',
            'rsp-subtree': 'children',
            'rsp-subtree-class': 'fvRsBd',
            #'subscription': 'yes',
            'order-by': 'fvAEPg.name|asc',
            #'page': '0',
            #'page-size': '15'
        }
        response = self.apic_service.get(f'node/mo/uni/tn-TN_CLARO_IT/ap-AP_CLARO_IT.json', {'params': params})
        response = response.json()

        registros_to_insert = []
        for row in response['imdata']:
            to_add = row['fvAEPg']['attributes']
            fvRsBd = self.fvRsBd_attr.copy()
            childrens = row['fvAEPg']['children']
            for child in childrens:
                if 'fvRsBd' in child.keys():
                    fvRsBd = child['fvRsBd']['attributes']

            for attr in fvRsBd.keys():
                to_add[f'fvRsBd_{attr}'] = fvRsBd[attr]

            to_add['modTs'] = self.utc_to_loaddate(to_add['modTs'])
            to_add['fvRsBd_modTs'] = self.utc_to_loaddate(to_add['fvRsBd_modTs'])
            to_add['tn_uid'] = to_add['uid']
            to_add.pop('uid')
            registros_to_insert.append(to_add)

        self.tenant_epg_repo.delete_all()
        self.tenant_epg_repo.insert_from_array(registros_to_insert)

        # L3OUT
        params = {
            'query-target': 'children',
            'target-subtree-class': 'l3extOut',
            'query-target-filter': 'not(wcard(l3extOut.dn,"__ui_"))',
            'rsp-subtree': 'full',
            'rsp-subtree-class': 'bgpExtP,ospfExtP,eigrpExtP,pimExtP,l3extRsEctx',
            'order-by': 'l3extOut.name|asc'
        }
        response = self.apic_service.get(f'node/mo/uni/tn-TN_CLARO_IT.json', {'params': params})
        response = response.json()

        registros_to_insert = []
        for row in response['imdata']:
            to_add = row['l3extOut']['attributes']
            bgpExtP = self.bgpExtP_attr.copy()
            l3extRsEctx = self.l3extRsEctx_attr.copy()
            childrens = row['l3extOut']['children']
            for child in childrens:
                if 'bgpExtP' in child.keys():
                    bgpExtP = child['bgpExtP']['attributes']
                if 'l3extRsEctx' in child.keys():
                    l3extRsEctx = child['l3extRsEctx']['attributes']

            for attr in bgpExtP.keys():
                to_add[f'bgpExtP_{attr}'] = bgpExtP[attr]
            for attr in l3extRsEctx.keys():
                to_add[f'l3extRsEctx_{attr}'] = l3extRsEctx[attr]

            to_add['modTs'] = self.utc_to_loaddate(to_add['modTs'])
            to_add['bgpExtP_modTs'] = self.utc_to_loaddate(to_add['bgpExtP_modTs'])
            to_add['l3extRsEctx_modTs'] = self.utc_to_loaddate(to_add['l3extRsEctx_modTs'])
            to_add['tn_uid'] = to_add['uid']
            to_add.pop('uid')
            registros_to_insert.append(to_add)

        self.tenant_l3out_repo.delete_all()
        self.tenant_l3out_repo.insert_from_array(registros_to_insert)

    def utc_to_loaddate(self, str_utc, dtformat = '%Y-%m-%dT%H:%M:%S.%f%z'):
        if str_utc is not None:
            return datetime.datetime.strptime(str_utc, dtformat).strftime('%Y-%m-%d %H:%M:%S')
        return None