from src.san.shared.services import BaseSanService
import xml.etree.ElementTree as ET
import json
import datetime as dt

class LoadServiceManager(BaseSanService):
    def __init__(self, repository, site_repo, san_service, control_carga_repo, sam_id):
        self.repository = repository
        self.site_repo = site_repo
        self.san_service = san_service
        self.control_carga_repo = control_carga_repo
        self.queueid_by_id = {
            "san": "san.service_manager",
            "sam_5620": "sam_5620.service_manager"
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
            registros, epipe_sites = self._get_data()

            self.repository.load_temp_table(registros)
            self.repository.merge_table()

            self.site_repo.load_temp_table(epipe_sites)
            self.site_repo.merge_table()

            data_count = len(registros)
            sub_data_count = len(epipe_sites)

            print(f"registros: {data_count}")
            print(f"epipe_sites: {sub_data_count}")
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
            f"{self.sam_id}_service_manager_{fecha.strftime('%Y%m%d')}",
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
                    <requestID>epipe.Epipe</requestID>
                </header>
            </soapenv:Header>
            <soapenv:Body>
                <find xmlns="xmlapi_1.0">
                    <fullClassName>service.ServiceManager</fullClassName>
                    <resultFilter>
                        <attribute/>
                        <children>
                            <resultFilter class="epipe.Epipe">
                                <attribute>id</attribute>
                                <attribute>displayedName</attribute>
                                <attribute>description</attribute>
                                <attribute>serviceId</attribute>
                                <attribute>subscriberId</attribute>
                                <attribute>customerName</attribute>
                                <attribute>objectFullName</attribute>
                                <children>
                                    <resultFilter class="epipe.Site">
                                        <attribute>displayedName</attribute>
                                        <attribute>description</attribute>
                                        <attribute>serviceId</attribute>
                                        <attribute>vcId</attribute>
                                        <attribute>subscriberId</attribute>
                                        <attribute>subscriberName</attribute>
                                        <attribute>numberOfAccessInterfaces</attribute>
                                        <attribute>name</attribute>
                                        <attribute>objectFullName</attribute>								
                                        <children>
                                            <resultFilter class="svt.SpokeSdpBinding">
                                                <attribute>serviceId</attribute>
                                                <attribute>serviceName</attribute>
                                                <attribute>serviceType</attribute>
                                                <attribute>siteId</attribute>										
                                                <attribute>subscriberId</attribute>
                                                <attribute>subscriberName</attribute>
                                                <attribute>description</attribute>										
                                                <attribute>vcId</attribute>
                                                <attribute>vcType</attribute>
                                                <attribute>circuitType</attribute>
                                                <attribute>pathId</attribute>
                                                <attribute>pathName</attribute>
                                                <attribute>endpointPrecedence</attribute>										
                                                <attribute>returnPathId</attribute>
                                                <attribute>returnPathName</attribute>										
                                                <attribute>fromNodeId</attribute>
                                                <attribute>fromNodeName</attribute>
                                                <attribute>toNodeId</attribute>
                                                <attribute>toNodeName</attribute>
                                                <attribute>objectFullName</attribute>
                                                <children/>
                                            </resultFilter>
                                        </children>
                                        <children>
                                            <resultFilter class="vll.L2AccessInterface">
                                                <attribute>nodeId</attribute>
                                                <attribute>nodeName</attribute>
                                                <attribute>portId</attribute>
                                                <attribute>portName</attribute>
                                                <attribute>terminatedPortClassName</attribute>
                                                <attribute>displayedName</attribute>
                                                <attribute>description</attribute>										
                                                <attribute>innerEncapValue</attribute>
                                                <attribute>outerEncapValue</attribute>
                                                <attribute>serviceId</attribute>
                                                <attribute>serviceName</attribute>
                                                <attribute>serviceType</attribute>
                                                <attribute>portPointer</attribute>
                                                <attribute>ingressPolicyId</attribute>
                                                <attribute>ingressPolicyName</attribute>
                                                <attribute>egressPolicyId</attribute>
                                                <attribute>egressPolicyName</attribute>										
                                                <attribute>operationalState</attribute>	
                                                <attribute>administrativeState</attribute>	
                                                <attribute>objectFullName</attribute>									
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
        response = self.san_service.invoke({'data': body})

        root = ET.fromstring(response.text)
        children_set = root[1][0][0][0][0]
        registros = self._map_entryset_to_row(children_set)
        first = None
        epipe_sites = []
        for row in registros:
            if 'epipe_Site' in list(row):
                for site in row['epipe_Site']:
                    if 'svt_SpokeSdpBinding' in list(site):
                        site['svt_SpokeSdpBinding'] = json.dumps(site['svt_SpokeSdpBinding'])
                    else:
                        site['svt_SpokeSdpBinding'] = json.dumps([])
                    
                    if 'vll_L2AccessInterface' in list(site):
                        site['vll_L2AccessInterface'] = json.dumps(site['vll_L2AccessInterface'])
                    else:
                        site['vll_L2AccessInterface'] = json.dumps([])
                    site['service_manager_id'] = row['objectFullName']
                    epipe_sites.append(site)
                row.pop('epipe_Site')

        return registros, epipe_sites

    def event_handler(self, event):
        self.execute()
