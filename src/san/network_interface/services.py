from src.san.shared.services import BaseSanService
import xml.etree.ElementTree as ET
import json
import datetime as dt

class LoadNetworkInterfaces(BaseSanService):
    def __init__(self, repo, san_service, control_carga_repo, sam_id):
        self.repo = repo
        self.san_service = san_service
        self.control_carga_repo = control_carga_repo
        self.queueid_by_id = {
            "san": "san.network_interface",
            "sam_5620": "sam_5620.network_interface"
        }
        self.queue_id = self.queueid_by_id[sam_id]
        self.sam_id = sam_id

    def execute(self):
        start_time = dt.datetime.now()
        is_succesfull = False
        data_count = 0
        shelf_count = 0
        error=None

        try:
            registros = self._get_data()

            self.repo.load_temp_table(registros)
            self.repo.merge_table()
            print(f"registros: {len(registros)}")

            data_count = len(registros)
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
            f"{self.sam_id}_network_interface_{fecha.strftime('%Y%m%d')}",
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
            if error is not None:
                raise error
            else:
                raise Exception("Ocurrió un error no identificado al realizar la carga")

    def _get_data(self):
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
        return registros

    def event_handler(self, event):
        self.execute()
