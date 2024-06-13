import cx_Oracle
import datetime as dt
import csv
import time
import json

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
            busqueda = None
            log_busqueda = {
                "proyecto": "busqueda_direcciones",
                "archivo": json.dumps(row),
                "registros_cargados": 1,
                "registros_totales": 0,
                "inicio": dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "fin": None,
                "estado": "ERROR",
                "mensaje": None,
                "fecha_archivo": dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            try:
                busqueda = self.get_lat_lng(row)
            except Exception as e:
                error_counter += 1
                log_busqueda["fin"] = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_busqueda["mensaje"] = str(e)
                self.insert_log(log_busqueda)
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
                    log_busqueda["fin"] = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    log_busqueda["mensaje"] = json.dumps(busqueda)
                    self.insert_log(log_busqueda)
            else:
                error_results.append({"id": row["rowid"]})
            time.sleep(2)
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
        order by fecha_generacion_sot desc
        fetch first '50' rows only
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

    def insert_log(self, log):
        config = {
            "template": """INSERT INTO PADM_CARGA_LOG(proyecto, archivo, registros_cargados, registros_totales, inicio, fin, estado, mensaje, fecha_archivo)
            values(:proyecto, :archivo, :registros_cargados, :registros_totales, to_date(:inicio, 'yyyy-mm-dd hh24:mi:ss'), to_date(:fin, 'yyyy-mm-dd hh24:mi:ss'), :estado, :mensaje, to_date(:fecha_archivo, 'yyyy-mm-dd hh24:mi:ss'))""",
            "row_type": "object",
            "limit_to_commit": 10000,
            "bindings": {
                "proyecto": cx_Oracle.STRING,
                "archivo": cx_Oracle.STRING,
                "registros_cargados": cx_Oracle.NUMBER,
                "registros_totales": cx_Oracle.NUMBER,
                "inicio": cx_Oracle.STRING,
                "fin": cx_Oracle.STRING,
                "estado": cx_Oracle.STRING,
                "mensaje": cx_Oracle.STRING,
                "fecha_archivo": cx_Oracle.STRING,
            }
        }
        self.db.save_from_array2(config, [log])
