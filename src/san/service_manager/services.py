from src.san.shared.services import BaseSanService
import xml.etree.ElementTree as ET
import json

class LoadServiceManager(BaseSanService):
    def __init__(self, repository, site_repo, san_service):
        self.repository = repository
        self.site_repo = site_repo
        self.san_service = san_service

    def execute(self):
        body = """
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Header>
                <header soapenv:actor="" soapenv:mustUnderstand="0" xmlns="xmlapi_1.0">
                    <security>
                        <user>oss_user_nbi</user>
                        <password hashed="false">Claro2020#$</password>
                    </security>
                    <requestID>epipe.Epipe</requestID>
                </header>
            </soapenv:Header>
            <soapenv:Body>
                <find xmlns="xmlapi_1.0">
                    <fullClassName>service.ServiceManager</fullClassName>
                    <resultFilter>
                        <attribute/>
                        <children>
                            <resultFilter class="epipe.Epipe">
                                <attribute>id</attribute>
                                <attribute>displayedName</attribute>
                                <attribute>description</attribute>
                                <attribute>serviceId</attribute>
                                <attribute>subscriberId</attribute>
                                <attribute>customerName</attribute>
                                <attribute>objectFullName</attribute>
                                <children>
                                    <resultFilter class="epipe.Site">
                                        <attribute>displayedName</attribute>
                                        <attribute>description</attribute>
                                        <attribute>serviceId</attribute>
                                        <attribute>vcId</attribute>
                                        <attribute>subscriberId</attribute>
                                        <attribute>subscriberName</attribute>
                                        <attribute>numberOfAccessInterfaces</attribute>
                                        <attribute>name</attribute>
                                        <attribute>objectFullName</attribute>								
                                        <children>
                                            <resultFilter class="svt.SpokeSdpBinding">
                                                <attribute>serviceId</attribute>
                                                <attribute>serviceName</attribute>
                                                <attribute>serviceType</attribute>
                                                <attribute>siteId</attribute>										
                                                <attribute>subscriberId</attribute>
                                                <attribute>subscriberName</attribute>
                                                <attribute>description</attribute>										
                                                <attribute>vcId</attribute>
                                                <attribute>vcType</attribute>
                                                <attribute>circuitType</attribute>
                                                <attribute>pathId</attribute>
                                                <attribute>pathName</attribute>
                                                <attribute>endpointPrecedence</attribute>										
                                                <attribute>returnPathId</attribute>
                                                <attribute>returnPathName</attribute>										
                                                <attribute>fromNodeId</attribute>
                                                <attribute>fromNodeName</attribute>
                                                <attribute>toNodeId</attribute>
                                                <attribute>toNodeName</attribute>
                                                <attribute>objectFullName</attribute>
                                                <children/>
                                            </resultFilter>
                                        </children>
                                        <children>
                                            <resultFilter class="vll.L2AccessInterface">
                                                <attribute>nodeId</attribute>
                                                <attribute>nodeName</attribute>
                                                <attribute>portId</attribute>
                                                <attribute>portName</attribute>
                                                <attribute>terminatedPortClassName</attribute>
                                                <attribute>displayedName</attribute>
                                                <attribute>description</attribute>										
                                                <attribute>innerEncapValue</attribute>
                                                <attribute>outerEncapValue</attribute>
                                                <attribute>serviceId</attribute>
                                                <attribute>serviceName</attribute>
                                                <attribute>serviceType</attribute>
                                                <attribute>portPointer</attribute>
                                                <attribute>ingressPolicyId</attribute>
                                                <attribute>ingressPolicyName</attribute>
                                                <attribute>egressPolicyId</attribute>
                                                <attribute>egressPolicyName</attribute>										
                                                <attribute>operationalState</attribute>	
                                                <attribute>administrativeState</attribute>	
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
        response = self.san_service.invoke({'data': body})

        root = ET.fromstring(response.text)
        children_set = root[1][0][0][0][0]
        registros = self._map_entryset_to_row(children_set)
        first = None
        epipe_sites = []
        for row in registros:
            if 'epipe_Site' in list(row):
                for site in row['epipe_Site']:
                    if 'svt_SpokeSdpBinding' in list(site):
                        site['svt_SpokeSdpBinding'] = json.dumps(site['svt_SpokeSdpBinding'])
                    else:
                        site['svt_SpokeSdpBinding'] = json.dumps([])
                    
                    if 'vll_L2AccessInterface' in list(site):
                        site['vll_L2AccessInterface'] = json.dumps(site['vll_L2AccessInterface'])
                    else:
                        site['vll_L2AccessInterface'] = json.dumps([])
                    site['service_manager_id'] = row['id']
                    epipe_sites.append(site)
                row.pop('epipe_Site')
        
        self.repository.delete_all()
        self.repository.insert_from_array(registros)

        self.site_repo.delete_all()
        self.site_repo.insert_from_array(epipe_sites)
        #print(first)

