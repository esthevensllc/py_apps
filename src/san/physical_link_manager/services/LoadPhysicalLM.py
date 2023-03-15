import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import xml.etree.ElementTree as ET

class LoadPhysicalLM:
    def __init__(self, repository, san_service):
        self.repository = repository
        self.san_service = san_service

    def execute(self):
        headers = {'Content-Type': 'application/xml'}
        body = """
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Header>
                <header soapenv:actor="" soapenv:mustUnderstand="0" xmlns="xmlapi_1.0">
                    <security>
                        <user>oss_user_nbi</user>
                        <password hashed="false">Claro2020#$</password>
                    </security>
                    <requestID>netw.DiscoveredPhysicalLink</requestID>
                </header>
            </soapenv:Header>
            <soapenv:Body>
                <find xmlns="xmlapi_1.0">
                    <fullClassName>netw.PhysicalLinkManager</fullClassName>
                    <resultFilter>
                        <attribute/>
                        <children>
                            <resultFilter class="netw.DiscoveredPhysicalLink">
                                <attribute>displayedName</attribute>
                                <attribute>objectFullName</attribute>
                                <attribute>description</attribute>
                                <attribute>endPointAPortId</attribute>
                                <attribute>endPointBPortId</attribute>
                                <attribute>endpointAPointer</attribute>						
                                <attribute>endpointBPointer</attribute>						
                                <attribute>endPointASiteId</attribute>
                                <attribute>endPointBSiteId</attribute>						
                                <attribute>endPointAType</attribute>
                                <attribute>endPointBType</attribute>
                                <attribute>usesManagedEndpointA</attribute>
                                <attribute>usesManagedEndpointB</attribute>
                                <children/>
                            </resultFilter>
                        </children>
                    </resultFilter>
                </find>
            </soapenv:Body>
        </soapenv:Envelope>
        """
        #response = requests.post('https://172.19.147.69:8443/xmlapi/invoke', data=body, headers=headers, verify=False)
        response = self.san_service.invoke({'data': body})
        xml_parsed = ET.fromstring(response.text)
        root = xml_parsed
        print(root[1][0][0][0])
        print()
        registros = []
        for children in root[1][0][0][0][0]:
            row_to_add = {}
            for attr in children:
                attr_name = attr.tag.split('}')[1]
                row_to_add[attr_name] = attr.text
            registros.append(row_to_add)
        
        self.repository.delete_all()
        self.repository.insert_from_array(registros)
        print(f"Registros: {len(registros)}")
