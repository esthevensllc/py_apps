from src.san.shared.services import BaseSanService
import xml.etree.ElementTree as ET

class LoadNotDiscPhysicalLM(BaseSanService):
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
                    <requestID>netw.PhysicalLink</requestID>
                </header>
            </soapenv:Header>
            <soapenv:Body>
                <find xmlns="xmlapi_1.0">
                    <fullClassName>netw.PhysicalLinkManager</fullClassName>
                    <resultFilter>
                        <attribute/>
                        <children>
                            <resultFilter class="netw.PhysicalLink">
                                <attribute>id</attribute>
                                <attribute>displayedName</attribute>
                                <attribute>description</attribute>
                                <attribute>endpointAPointer</attribute>
                                <attribute>endpointBPointer</attribute>
                                <attribute>objectFullName</attribute>
                                <children/>
                            </resultFilter>
                        </children>
                    </resultFilter>
                </find>
            </soapenv:Body>
        </soapenv:Envelope>
        """
        print("load_not_disc_physical_lm")
        response = self.san_service.invoke({'data': body})
        root = ET.fromstring(response.text)
        children_set = root[1][0][0][0][0]
        registros = self._map_entryset_to_row(children_set)

        print(response.status_code)

        self.repository.delete_all()
        self.repository.insert_from_array(registros)
