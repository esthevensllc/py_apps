from src.san.shared.services import BaseSanService
import xml.etree.ElementTree as ET
import json

class LoadLagInterfaces(BaseSanService):
    def __init__(self, repo, port_repo, san_service):
        self.repo = repo
        self.port_repo = port_repo
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
                    <requestID>lag.Interface</requestID>
                </header>
            </soapenv:Header>
            <soapenv:Body>
                <find xmlns="xmlapi_1.0">
                    <fullClassName>lag.Interface</fullClassName>
                    <resultFilter>
                        <attribute>id</attribute>
                        <attribute>lagId</attribute>
                        <attribute>snmpPortId</attribute>
                        <attribute>description</attribute>
                        <attribute>siteId</attribute>
                        <attribute>siteName</attribute>				
                        <attribute>shelfId</attribute>
                        <attribute>displayedName</attribute>
                        <attribute>operationalState</attribute>				
                        <attribute>administrativeState</attribute>
                        <attribute>objectFullName</attribute>
                        <children>
                            <resultFilter class="lag.PortTermination">
                                <attribute>nodeId</attribute>
                                <attribute>nodeName</attribute>
                                <attribute>lagId</attribute>
                                <attribute>portId</attribute>
                                <attribute>description</attribute>
                                <attribute>memberName</attribute>						
                                <attribute>portPointer</attribute>						
                                <attribute>shelfId</attribute>						
                                <children/>
                            </resultFilter>
                        </children>
                    </resultFilter>
                </find>
            </soapenv:Body>
        </soapenv:Envelope>
        """

        print("load_lag_interfaces")

        response = self.san_service.invoke({'data': body})
        root = ET.fromstring(response.text)
        children_set = root[1][0][0]
        registros = self._map_entryset_to_row(children_set)
        port_termination = []
        counter = 1
        for row in registros:
            row['id'] = counter
            if 'lag_PortTermination' in list(row):
                for port in row['lag_PortTermination']:
                    port['interface_id'] = row['id']
                    port_termination.append(port)
                row.pop('lag_PortTermination')
            counter = counter+1

        print(response.status_code)

        self.repo.delete_all()
        self.repo.insert_from_array(registros)
        print(f"registros: {len(registros)}")

        self.port_repo.delete_all()
        self.port_repo.insert_from_array(port_termination)
        print(f"ports: {len(port_termination)}")