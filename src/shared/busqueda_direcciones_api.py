from lxml import etree
import requests

class BusquedaDireccionSoap:
    def ebsConsultaPDR(self, query):
        querysdf = """
        <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:server">
            <soapenv:Header/>
            <soapenv:Body>
                <urn:client soapenv:encodingStyle=http://schemas.xmlsoap.org/soap/encoding/>
                    <id xsi:type="xsd:string">USRSC</id>
                </urn:client>
                <urn:ebsConsultaPDR soapenv:encodingStyle=http://schemas.xmlsoap.org/soap/encoding/>
                    <ubigeo xsi:type="xsd:string">775180</ubigeo>
                    <direccion xsi:type="xsd:string">ENRIQUE LOPEZ ALBUJAR 574</direccion>
                    <requestTime xsi:type="xsd:string">2024-05-27 17:50:05</requestTime>
                </urn:ebsConsultaPDR>
            </soapenv:Body>
        </soapenv:Envelope>
        """

        headers = {"Content-Type": "text/xml", "Connection": "close"}
        # response = requests.post("http://172.16.102.104:7788/Busqueda_Direcciones/Ubicacion", data=query, headers=headers)
        response = requests.post("http://172.16.102.104:7788/Busqueda_Direcciones/Ubicacion", data=query, headers=headers)
        if response.status_code >= 500:
            raise Exception(response.text)
        # print(response.text)
        root = etree.fromstring(response.text)
        returnEl = root[0][0][0]
        auditResponse = returnEl[0]
        accionResponse = returnEl[1]

        response = {"auditResponse": {}, "accionResponse": {}}
        for child in auditResponse:
            response["auditResponse"][child.tag] = child.text
        for child in accionResponse:
            # print(child.tag, child.text)
            response["accionResponse"][child.tag] = child.text

        return response