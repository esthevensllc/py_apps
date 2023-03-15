from src.san.shared.services import BaseSanService
import xml.etree.ElementTree as ET
import json

class LoadNetworkInterfaces(BaseSanService):
    def __init__(self, repo, san_service):
        self.repo = repo
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
                    <requestID>rtr.NetworkInterface</requestID>
                </header>
            </soapenv:Header>
            <soapenv:Body>
                <find xmlns="xmlapi_1.0">
                    <fullClassName>rtr.NetworkInterface</fullClassName>
                    <resultFilter>
                        <attribute>nodeId</attribute>
                        <attribute>nodeName</attribute>
                        <attribute>portId</attribute>
                        <attribute>portName</attribute>
                        <attribute>terminatedObjectId</attribute>				
                        <attribute>displayedName</attribute>
                        <attribute>id</attribute>
                        <attribute>description</attribute>				
                        <attribute>interfaceClass</attribute>
                        <attribute>primaryIPv4Address</attribute>
                        <attribute>primaryIPv4PrefixLength</attribute>
                        <attribute>terminatedPortInnerEncapValue</attribute>
                        <attribute>terminatedPortOuterEncapValue</attribute>
                        <attribute>objectFullName</attribute>
                        <attribute>operationalState</attribute>
                        <attribute>administrativeState</attribute>
                        <children/>
                    </resultFilter>
                </find>
            </soapenv:Body>
        </soapenv:Envelope>
        """

        print("load_network_interfaces")

        response = self.san_service.invoke({'data': body})
        root = ET.fromstring(response.text)
        children_set = root[1][0][0]
        registros = self._map_entryset_to_row(children_set)

        print(response.status_code)

        self.repo.delete_all()
        self.repo.insert_from_array(registros)
        print(f"registros: {len(registros)}")
