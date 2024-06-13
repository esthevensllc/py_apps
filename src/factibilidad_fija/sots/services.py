import cx_Oracle
import datetime as dt
import csv

query_soap = """
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

class UpdateInfoSots:
    def __init__(self, db, soap):
        self.db = db
        self.soap = soap
    
    def execute(self):
        sots = self.get_sots()
        search_results = []
        error_results = []
        counter = 0
        error_counter = 0
        print(f"sots: {len(sots)}")
        for row in sots:
            # busqueda = self.soap.ebsConsultaPDR(row)
            busqueda = None
            try:
                busqueda = self.get_lat_lng(row)
            except:
                error_counter += 1
            if busqueda is not None:
                counter += 1
                if str(busqueda["latitud"]) != '0' and str(busqueda["longitud"]) != '0':
                    search_results.append({
                        "id": row["rowid"],
                        "latitud": float(busqueda["latitud"]),
                        "longitud": float(busqueda["longitud"]),
                    })
                else:
                    error_results.append({"id": row["rowid"]})
            else:
                error_results.append({"id": row["rowid"]})
        print(f"error_counter: {error_counter}")
        print(f"ok_counter: {counter}")
        print(f"results: {len(search_results)}")
        # for row in search_results:
        # print(row)

        self.update_lat_lng(search_results)
        self.update_search_errors(error_results)


    def get_sots(self):
        query = """
        SELECT a.rowid, m.ubigeo, a.direccion FROM FIJA_SOTS_FACTIBILIDAD a
        inner join fija_maestro_planos_pap m
        on m.plano = a.idplano
        WHERE LATITUD_CLIENTE IS NULL AND LONGITUD_CLIENTE IS NULL and fecha_generacion_sot >= trunc(sysdate - 1, 'dd')
        and search_errors < 1
        fetch first '100' rows only
        """
        result = self.db.fetch(query)
        data = []
        for row in result:
            data.append({
                "rowid": row[0],
                "ubigeo": row[1],
                "direccion": row[2]
            })
        return data

    def get_lat_lng(self, params):
        str_now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = f"""<soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:server">
        <soapenv:Header/>
        <soapenv:Body>
            <urn:client soapenv:encodingStyle=http://schemas.xmlsoap.org/soap/encoding/>
                <id xsi:type="xsd:string">USRSC</id>
            </urn:client>
            <urn:ebsConsultaPDR soapenv:encodingStyle=http://schemas.xmlsoap.org/soap/encoding/>
                <ubigeo xsi:type="xsd:string">{params['ubigeo']}</ubigeo>
                <direccion xsi:type="xsd:string">{params['direccion']}</direccion>
                <requestTime xsi:type="xsd:string">{str_now}</requestTime>
            </urn:ebsConsultaPDR>
        </soapenv:Body>
        </soapenv:Envelope>"""
        result = self.soap.ebsConsultaPDR(body)
        if int(result["auditResponse"]["codRespuesta"]) == 200:
            return result["accionResponse"]

    def update_lat_lng(self, data):
        config = {
            "template": """UPDATE FIJA_SOTS_FACTIBILIDAD
            set latitud_cliente = :latitud, longitud_cliente = :longitud
            where rowid = :id""",
            "row_type": "object",
            "limit_to_commit": 10000,
            "bindings": {
                "id": cx_Oracle.STRING,
                "latitud": cx_Oracle.NUMBER,
                "longitud": cx_Oracle.NUMBER
            }
        }
        self.db.save_from_array2(config, data)

    def update_search_errors(self, data):
        config = {
            "template": """UPDATE FIJA_SOTS_FACTIBILIDAD
            set search_errors = search_errors + 1
            where rowid = :id""",
            "row_type": "object",
            "limit_to_commit": 10000,
            "bindings": {
                "id": cx_Oracle.STRING
            }
        }
        self.db.save_from_array2(config, data)
