from src.san.shared.services import BaseSanService
import xml.etree.ElementTree as ET
import json
import datetime as dt

class LoadNetworkElement(BaseSanService):
    def __init__(self, repository, shelf_repo, san_service, control_carga_repo, sam_id):
        self.repository = repository
        self.shelf_repo = shelf_repo
        self.san_service = san_service
        self.control_carga_repo = control_carga_repo
        self.queueid_by_id = {
            "san": "san.load_network_element",
            "sam_5620": "sam_5620.load_network_element"
        }
        self.queue_id = self.queueid_by_id[sam_id]
        self.sam_id = sam_id

    def execute(self):
        start_time = dt.datetime.now()
        is_succesfull = False
        network_element_count = 0
        shelf_count = 0
        error=None
        try:
            registros, shelfs = self._get_data()

            self.repository.load_temp_table(registros)
            self.repository.merge_table()
            print(f"registros: {len(registros)}")

            self.shelf_repo.load_temp_table(shelfs)
            self.shelf_repo.merge_table()
            print(f"shelfs: {len(shelfs)}")

            network_element_count = len(registros)
            shelf_count = len(shelfs)
            is_succesfull = True
        except BaseException as e:
            error = e
        except:
            is_succesfull = False

        end_time = dt.datetime.now()
        fecha = dt.datetime.strptime(start_time.strftime('%Y-%m-%d'), "%Y-%m-%d")
        estado_seguimiento = 'CARGADO' if is_succesfull == True else 'ERROR'

        self.control_carga_repo.save_carga(
            self.queue_id,
            f"{self.sam_id}_network_element_{start_time.strftime('%Y%m%d')}",
            network_element_count if is_succesfull == True else 0,
            network_element_count,
            start_time,
            end_time,
            estado_seguimiento,
            str(error) if error is not None else '',
            fecha
        )

        self.control_carga_repo.save_carga(
            self.queue_id,
            f"{self.sam_id}_network_element_shelf_{start_time.strftime('%Y%m%d')}",
            shelf_count if is_succesfull == True else 0,
            shelf_count,
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
                    <requestID>netw.NetworkElement - NE and HW</requestID>
                </header>
            </soapenv:Header>
            <soapenv:Body>
                <find xmlns="xmlapi_1.0">
                    <fullClassName>netw.NetworkElement</fullClassName>
                    <resultFilter>
                        <attribute>id</attribute>
                        <attribute>ipAddress</attribute>
                        <attribute>chassisType</attribute>
                        <attribute>siteId</attribute>
                        <attribute>siteName</attribute>				
                        <attribute>displayedName</attribute>
                        <attribute>name</attribute>
                        <attribute>location</attribute>				
                        <attribute>version</attribute>
                        <attribute>descriptorVersion</attribute>
                        <attribute>objectFullName</attribute>
                        <children>
                            <resultFilter class="equipment.Shelf">
                                <attribute>shelfType</attribute>
                                <attribute>shelfName</attribute>
                                <attribute>shelfId</attribute>
                                <attribute>siteId</attribute>
                                <attribute>serialNumber</attribute>
                                <attribute>manufacturerBoardNumber</attribute>
                                <attribute>objectFullName</attribute>
                                <children>
                                    <resultFilter class="equipment.CardSlot">
                                        <attribute>slotId</attribute>
                                        <children>
                                            <resultFilter class="equipment.BaseCard">
                                                <attribute>specificType</attribute>
                                                <attribute>serialNumber</attribute>
                                                <attribute>manufacturerBoardNumber</attribute>
                                                <children>
                                                    <resultFilter class="equipment.DaughterCardSlot">
                                                        <attribute>daughterCardSlotId</attribute>
                                                        <children>
                                                            <resultFilter class="equipment.DaughterCard">
                                                                <attribute>specificType</attribute>
                                                                <attribute>serialNumber</attribute>
                                                                <attribute>manufacturerBoardNumber</attribute>
                                                                <children>
                                                                    <resultFilter class="equipment.PhysicalPort">
                                                                        <attribute>snmpPortId</attribute>
                                                                        <attribute>portId</attribute>
                                                                        <attribute>portName</attribute>
                                                                        <attribute>displayedName</attribute>
                                                                        <attribute>portClass</attribute>
                                                                        <attribute>description</attribute>
                                                                        <attribute>encapType</attribute>
                                                                        <attribute>mtuValue</attribute>
                                                                        <attribute>actualSpeed</attribute>
                                                                        <attribute>speed</attribute>								
                                                                        <attribute>operationalState</attribute>
                                                                        <attribute>administrativeState</attribute>
                                                                        <attribute>isEquipped</attribute>
                                                                        <attribute>macAddress</attribute>
                                                                        <attribute>objectFullName</attribute>
                                                                        <attribute>lagMembershipId</attribute>
                                                                        <attribute>shelfId</attribute>							
                                                                        <children>
                                                                            <resultFilter class="equipment.MediaAdaptor">
                                                                                <attribute>portId</attribute>
                                                                                <attribute>portName</attribute>
                                                                                <attribute>specificType</attribute>
                                                                                <attribute>connectorType</attribute>
                                                                                <attribute>sfpOpticalCompliance</attribute>
                                                                                <attribute>modelNumber</attribute>
                                                                                <attribute>vendorSerialNumber</attribute>
                                                                                <attribute>vendorPartNumber</attribute>
                                                                                <attribute>objectFullName</attribute>					
                                                                                <children/>
                                                                            </resultFilter>
                                                                        </children>
                                                                    </resultFilter>
                                                                </children>
                                                            </resultFilter>
                                                        </children>
                                                    </resultFilter>
                                                </children>
                                            </resultFilter>
                                        </children>
                                        <children>
                                            <resultFilter class="equipment.ProcessorCard">
                                                <attribute>specificType</attribute>
                                                <attribute>serialNumber</attribute>
                                                <attribute>manufacturerBoardNumber</attribute>
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
        print("load_network_element")
        response = self.san_service.invoke({'data': body})

        response_text = response.text

        root = ET.fromstring(response_text)
        children_set = root[1][0][0]
        registros = self._map_entryset_to_row(children_set)
        shelfs = []
        counter = 1
        for row in registros:
            # row['id'] = counter
            if 'equipment_Shelf' in list(row):
                for sh in row['equipment_Shelf']:
                    sh['equipment_CardSlot'] = json.dumps(sh['equipment_CardSlot'])
                    sh['network_element_id'] = row['objectFullName']
                    shelfs.append(sh)
                row.pop('equipment_Shelf')
            counter = counter + 1
        return registros, shelfs

    def event_handler(self, event):
        self.execute()
