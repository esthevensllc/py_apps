from src.san.shared.services import BaseSanService
import xml.etree.ElementTree as ET
import json

class LoadNetworkElement(BaseSanService):
    def __init__(self, repository, shelf_repo, san_service):
        self.repository = repository
        self.shelf_repo = shelf_repo
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
                        <children>
                            <resultFilter class="equipment.Shelf">
                                <attribute>shelfType</attribute>
                                <attribute>shelfName</attribute>
                                <attribute>shelfId</attribute>
                                <attribute>siteId</attribute>
                                <attribute>serialNumber</attribute>
                                <attribute>manufacturerBoardNumber</attribute>
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
            row['id'] = counter
            if 'equipment_Shelf' in list(row):
                for sh in row['equipment_Shelf']:
                    sh['equipment_CardSlot'] = json.dumps(sh['equipment_CardSlot'])
                    sh['network_element_id'] = row['id']
                    shelfs.append(sh)
                row.pop('equipment_Shelf')
            counter = counter + 1

        print(1)

        self.repository.delete_all()
        self.repository.insert_from_array(registros)
        print(f"registros: {len(registros)}")

        self.shelf_repo.delete_all()
        self.shelf_repo.insert_from_array(shelfs)
        print(f"shelfs: {len(registros)}")