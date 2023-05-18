from src.san.shared.services import BaseSanService
import xml.etree.ElementTree as ET
import json
import datetime as dt

class LoadVPRN(BaseSanService):
    def __init__(self, repository, site_repo, san_service, control_carga_repo, sam_id):
        self.repository = repository
        self.site_repo = site_repo
        self.san_service = san_service
        self.control_carga_repo = control_carga_repo
        self.queueid_by_id = {
            "san": "san.vprn",
            "sam_5620": "sam_5620.vprn"
        }
        self.queue_id = self.queueid_by_id[sam_id]
        self.sam_id = sam_id

    def execute(self):
        start_time = dt.datetime.now()
        is_succesfull = False
        data_count = 0
        sub_data_count = 0
        error=None

        try:
            registros, sites = self._get_data()

            self.repository.load_temp_table(registros)
            self.repository.merge_table()

            self.site_repo.load_temp_table(sites)
            self.site_repo.merge_table()

            data_count = len(registros)
            sub_data_count = len(sites)

            print(f"registros: {data_count}")
            print(f"sites: {sub_data_count}")
            is_succesfull = True
        except BaseException as e:
            error = e
        except:
            error = Exception("Ocurrió un error no identificado al realizar la carga")
        
        end_time = dt.datetime.now()
        fecha = dt.datetime.strptime(start_time.strftime('%Y-%m-%d'), "%Y-%m-%d")
        estado_seguimiento = 'CARGADO' if is_succesfull == True else 'ERROR'

        self.control_carga_repo.save_carga(
            self.queue_id,
            f"{self.sam_id}_vprn_{fecha.strftime('%Y%m%d')}",
            data_count if is_succesfull == True else 0,
            data_count,
            start_time,
            end_time,
            estado_seguimiento,
            str(error) if error is not None else '',
            fecha
        )

        # envio de error
        if is_succesfull == False:
            raise error

    def _get_data(self):
        body = """
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Header>
                <header soapenv:actor="" soapenv:mustUnderstand="0" xmlns="xmlapi_1.0">
                    <security>
                        <user>oss_user_nbi</user>
                        <password hashed="false">Claro2020#$</password>
                    </security>
                    <requestID>vprn.Vprn</requestID>
                </header>
            </soapenv:Header>
            <soapenv:Body>
                <find xmlns="xmlapi_1.0">
                    <fullClassName>service.ServiceManager</fullClassName>
                    <resultFilter>
                        <attribute/>
                        <children>
                            <resultFilter class="vprn.Vprn">
                                <attribute>id</attribute>
                                <attribute>displayedName</attribute>
                                <attribute>description</attribute>
                                <attribute>serviceId</attribute>
                                <attribute>subscriberId</attribute>
                                <attribute>customerName</attribute>
                                <attribute>objectFullName</attribute>
                                <children>
                                    <resultFilter class="vprn.Site">
                                        <attribute>displayedName</attribute>
                                        <attribute>description</attribute>
                                        <attribute>serviceId</attribute>
                                        <attribute>serviceName</attribute>
                                        <attribute>vcId</attribute>
                                        <attribute>siteId</attribute>
                                        <attribute>subscriberId</attribute>
                                        <attribute>subscriberName</attribute>
                                        <attribute>svcComponentId</attribute>
                                        <attribute>routingInstanceId</attribute>
                                        <attribute>objectFullName</attribute>
                                        <children>
                                            <resultFilter class="l3fwd.ServiceSite">
                                                <attribute>vrfName</attribute>									
                                                <attribute>vpnId</attribute>										
                                                <attribute>vprnType</attribute>									
                                                <attribute>serviceId</attribute>									
                                                <attribute>serviceName</attribute>									
                                                <attribute>siteId</attribute>
                                                <attribute>siteName</attribute>
                                                <attribute>subscriberId</attribute>
                                                <attribute>subscriberName</attribute>										
                                                <attribute>routerId</attribute>
                                                <attribute>routerName</attribute>										
                                                <attribute>autonomousSystemNumber</attribute>
                                                <attribute>routingInstanceName</attribute>
                                                <attribute>routeDistinguisherType</attribute>										
                                                <attribute>routeDistinguisher</attribute>										
                                                <attribute>type0AdministrativeValue</attribute>
                                                <attribute>type0AssignedValue</attribute>
                                                <attribute>type1AdministrativeValue</attribute>
                                                <attribute>type1AssignedValue</attribute>
                                                <attribute>type2AdministrativeValue</attribute>
                                                <attribute>type2AssignedValue</attribute>
                                                <attribute>vrfTarget</attribute>
                                                <attribute>vrfTargetASValue</attribute>
                                                <attribute>vrfTargetCommunityValue</attribute>										
                                                <attribute>vrfTargetExtendedCommunityValue</attribute>
                                                <attribute>vrfTargetType</attribute>										
                                                <attribute>vrfExportTarget</attribute>										
                                                <attribute>vrfExportTargetASValue</attribute>										
                                                <attribute>vrfExportTargetCommunityValue</attribute>									
                                                <attribute>vrfExportTargetExtendedCommunityValue</attribute>	
                                                <attribute>vrfImportTarget</attribute>
                                                <attribute>vrfImportTargetASValue</attribute>	
                                                <attribute>vrfImportTargetCommunityValue</attribute>	
                                                <attribute>vrfImportTargetExtendedCommunityValue</attribute>
                                                <attribute>addressFamily</attribute>
                                                <attribute>objectFullName</attribute>
                                                <children/>
                                            </resultFilter>
                                        </children>
                                        <children>
                                            <resultFilter class="vprn.L3AccessInterface">
                                                <attribute>nodeId</attribute>
                                                <attribute>nodeName</attribute>									
                                                <attribute>serviceId</attribute>
                                                <attribute>serviceName</attribute>									
                                                <attribute>portId</attribute>
                                                <attribute>portName</attribute>									
                                                <attribute>displayedName</attribute>									
                                                <attribute>l3InterfaceDescription</attribute>									
                                                <attribute>terminatedPortClassName</attribute>									
                                                <attribute>innerEncapValue</attribute>
                                                <attribute>outerEncapValue</attribute>
                                                <attribute>primaryIPv4Address</attribute>
                                                <attribute>primaryIPv4PrefixLength</attribute>
                                                <attribute>portPointer</attribute>
                                                <attribute>ingressPolicyId</attribute>
                                                <attribute>ingressPolicyName</attribute>
                                                <attribute>egressPolicyId</attribute>
                                                <attribute>egressPolicyName</attribute>
                                                <attribute>operationalState</attribute>
                                                <attribute>l3InterfaceAdministrativeState</attribute>
                                                <attribute>administrativeState</attribute>									
                                                <attribute>objectFullName</attribute>
                                                <children/>
                                            </resultFilter>
                                        </children>
                                        <children>
                                            <resultFilter class="vprn.RoutingInstanceSite">
                                                <attribute>serviceId</attribute>
                                                <attribute>subscriberId</attribute>
                                                <attribute>subscriberName</attribute>
                                                <attribute>siteId</attribute>
                                                <attribute>siteName</attribute>										
                                                <attribute>routerId</attribute>
                                                <attribute>routerName</attribute>
                                                <attribute>autonomousSystemNumber</attribute>
                                                <attribute>displayedName</attribute>
                                                <attribute>name</attribute>
                                                <attribute>objectFullName</attribute>
                                                <children/>
                                            </resultFilter>
                                        </children>
                                    </resultFilter>
                                </children>
                            </resultFilter>
                        </children>
                    </resultFilter>
                </find>
            </soapenv:Body>
        </soapenv:Envelope>
        """
        print("load_vprn")
        response = self.san_service.invoke({'data': body})
        response_text = response.text

        root = ET.fromstring(response_text)
        children_set = root[1][0][0][0][0]
        registros = self._map_entryset_to_row(children_set)
        sites = []
        for row in registros:
            if 'vprn_Site' in list(row):
                for site in row['vprn_Site']:
                    site['vprn_id'] = row['objectFullName']
                    if 'l3fwd_ServiceSite' in list(site):
                        site['l3fwd_ServiceSite'] = json.dumps(site['l3fwd_ServiceSite'])
                    if 'vprn_L3AccessInterface' in list(site):
                        site['vprn_L3AccessInterface'] = json.dumps(site['vprn_L3AccessInterface'])
                    if 'vprn_RoutingInstanceSite' in list(site):
                        site['vprn_RoutingInstanceSite'] = json.dumps(site['vprn_RoutingInstanceSite'])
                    sites.append(site)
                row.pop('vprn_Site')

        #print(response.status_code)
        return registros, sites
    
    def event_handler(self, event):
        self.execute()
