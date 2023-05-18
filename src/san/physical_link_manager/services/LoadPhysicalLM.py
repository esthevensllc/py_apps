import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import xml.etree.ElementTree as ET
import datetime as dt

class LoadPhysicalLM:
    def __init__(self, repository, san_service, control_carga_repo, sam_id):
        self.repository = repository
        self.san_service = san_service
        self.control_carga_repo = control_carga_repo
        self.queueid_by_id = {
            "san": "san.physical_lm",
            "sam_5620": "sam_5620.physical_lm"
        }
        self.queue_id = self.queueid_by_id[sam_id]
        self.sam_id = sam_id

    def execute(self):
        start_time = dt.datetime.now()
        is_succesfull = False
        data_count = 0
        error=None

        try:
            registros = self._get_data()

            self.repository.load_temp_table(registros)
            self.repository.merge_table()

            data_count = len(registros)
            print(f"registros: {data_count}")
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
            f"{self.sam_id}_physical_lm_{fecha.strftime('%Y%m%d')}",
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
        return registros

    def event_handler(self, event):
        self.execute()

