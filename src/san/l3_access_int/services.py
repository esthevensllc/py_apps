from src.san.shared.services import BaseSanService
import xml.etree.ElementTree as ET
import json

class LoadL3AccessInterface(BaseSanService):
    def __init__(self, repository, san_service):
        self.repository = repository
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
                    <requestID>ies.L3AccessInterface</requestID>
                </header>
            </soapenv:Header>
            <soapenv:Body>
                <find xmlns="xmlapi_1.0">
                    <fullClassName>ies.L3AccessInterface</fullClassName>
                    <resultFilter>
                        <attribute>id</attribute>
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
                        <attribute>egressPolicyName</attribute>				
                        <attribute>objectFullName</attribute>				
                        <children/>
                    </resultFilter>
                </find>
            </soapenv:Body>
        </soapenv:Envelope>
        """
        response = self.san_service.invoke({'data': body})
        root = ET.fromstring(response.text)
        children_set = root[1][0][0]
        registros = self._map_entryset_to_row(children_set)

        print(response.status_code)

        self.repository.delete_all()
        self.repository.insert_from_array(registros)
        print(f"Registros: {len(registros)}")