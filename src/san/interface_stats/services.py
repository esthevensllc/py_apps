from src.san.shared.services import BaseSanService
import xml.etree.ElementTree as ET
import datetime as dt

class LoadInterfaceStats(BaseSanService):
    def __init__(self, repository, san_service):
        self.repository = repository
        self.san_service = san_service

    def execute(self):
        print("load_interface_stats")
        #fecha1 = dt.datetime.strptime('2022-06-16 18:00:00', '%Y-%m-%d %H:%M:%S')
        #fecha2 = dt.datetime.strptime('2022-06-17 19:00:00', '%Y-%m-%d %H:%M:%S')
        fecha1 = dt.datetime.now().replace(minute=0,second=0) - dt.timedelta(hours=1)
        fecha2 = fecha1 + dt.timedelta(hours=1)
        fecha_recorrido = fecha1
        while fecha_recorrido < fecha2:
            self.__load_data_between(fecha_recorrido, fecha_recorrido + dt.timedelta(hours=1))
            fecha_recorrido = fecha_recorrido + dt.timedelta(hours=1)
            print("")

    def __load_data_between(self, fecha1, fecha2):
        #print(fecha1.strftime('%Y-%m-%d %H:%M:%S'))
        registros = self.__get_data(fecha1, fecha2)
        print(len(registros))
        dates = []
        for row in registros:
            timeCaptured = dt.datetime.fromtimestamp(int(row['timeCaptured'])/1000)
            timeLogged = dt.datetime.fromtimestamp(int(row['timeLogged'])/1000)
            periodicTime = dt.datetime.utcfromtimestamp(int(row['periodicTime'])/1000)
            row['timeCaptured'] = timeCaptured.strftime('%Y-%m-%d %H:%M:%S')
            row['timeLogged'] = timeLogged.strftime('%Y-%m-%d %H:%M:%S')
            row['periodicTime'] = periodicTime.strftime('%H:%M:%S')
            row['receivedUnknownProtocolPP'] = row['receivedUnknownProtocolPacketsPeriodic']
            row.pop('receivedUnknownProtocolPacketsPeriodic')

            dates.append(timeCaptured.strftime('%Y%m%d%H%M%S'))
        
        if len(dates) > 0:
            str_min = min(dates)
            str_max = max(dates)
            fecha1 = dt.datetime.strptime(str_min, '%Y%m%d%H%M%S')
            fecha2 = dt.datetime.strptime(str_max, '%Y%m%d%H%M%S')
            print(fecha1, fecha2)
            self.repository.delete_where_collectiontime_between(fecha1, fecha2)

        self.repository.insert_from_array(registros)

    def __get_data(self, fecha1, fecha2):
        #<requestID>bgp.PeerStats</requestID>
        #equipment.InterfaceStats
        body = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Header>
                <header soapenv:actor="" soapenv:mustUnderstand="0" xmlns="xmlapi_1.0">
                    <security>
                        <user>oss_user_nbi</user>
                        <password hashed="false">Claro2020#$</password>
                    </security>
                    
                </header>
            </soapenv:Header>
            <soapenv:Body>
                <find xmlns="xmlapi_1.0">
                    <fullClassName>equipment.InterfaceStatsLogRecord</fullClassName>
                    <filter class="equipment.InterfaceStatsLogRecord">
                        <and>
                            <greaterOrEqual name="timeCaptured" value="{int(fecha1.timestamp()*1000)}"/>
                            <less name="timeCaptured" value="{int(fecha2.timestamp()*1000)}"/>
                        </and>
                    </filter>
                </find>
            </soapenv:Body>
        </soapenv:Envelope>
        """
        response = self.san_service.invoke({'data': body})
        root = ET.fromstring(response.text)
        registros = self._map_entryset_to_row(root[1][0][0])
        return registros
