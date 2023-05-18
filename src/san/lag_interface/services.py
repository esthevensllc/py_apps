from src.san.shared.services import BaseSanService
import xml.etree.ElementTree as ET
import json
import datetime as dt

class LoadLagInterfaces(BaseSanService):
    def __init__(self, repo, port_repo, san_service, control_carga_repo, sam_id):
        self.repo = repo
        self.port_repo = port_repo
        self.san_service = san_service
        self.control_carga_repo = control_carga_repo
        self.queueid_by_id = {
            "san": "san.lag_interface",
            "sam_5620": "sam_5620.lag_interface"
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
            registros, port_termination = self._get_data()

            self.repo.load_temp_table(registros)
            self.repo.merge_table()

            self.port_repo.load_temp_table(port_termination)
            self.port_repo.merge_table()

            data_count = len(registros)
            sub_data_count = len(port_termination)
            print(f"registros: {data_count}")
            print(f"ports: {sub_data_count}")
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
            f"{self.sam_id}_lag_interface_{fecha.strftime('%Y%m%d')}",
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
                                <attribute>objectFullName</attribute>
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
            # row['id'] = counter
            if 'lag_PortTermination' in list(row):
                for port in row['lag_PortTermination']:
                    port['interface_id'] = row['objectFullName']
                    port_termination.append(port)
                row.pop('lag_PortTermination')
            counter = counter+1

        print(response.status_code)
        return registros, port_termination

    def event_handler(self, event):
        self.execute()