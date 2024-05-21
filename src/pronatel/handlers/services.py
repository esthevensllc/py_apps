import datetime as dt
import os
import csv
from src.shared.config import STORAGE_DIR, DTFORMAT_BY_ALIAS
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.pronatel.shared.services import (
    SEND_FLAG_HFC,
    SEND_FLAG_FTTH,
    SEND_SCORE_HFC,
    SEND_SCORE_FTTH,
    SEND_OCURRENCIAS_FIJA,
    SEND_VMAX,
    SEND_WIFI_HFC,
    SEND_REINICIOS_FTTH_HFC_DET,
    SEND_EQUIPO_NO_RECOMENDADO_HFC_DET
)

class SendSoporteClientesFile:
    def __init__(self, db, sftp_service):
        self.db = db
        self.sftp_service = sftp_service
        self.base_storage_dir = f"{STORAGE_DIR}pronatel_handlers"
        self.query = ""
        self.headers = []
        self.server_id = "anadw"
        self.remote_path = "/space/data/sftpserver/datawh/files/BASE_FLAG_TRACERT/output"
        # self.remote_path = "/space/test"

    def execute(self, fecha):
        self.sftp_service.useConnection(self.server_id)
        if not os.path.exists(self.base_storage_dir):
            os.makedirs(self.base_storage_dir)
        
        data = self.get_data(fecha)
        csv_name = self.get_filename(fecha)
        localfile = f"{self.base_storage_dir}/{csv_name}"
        with open(localfile, 'w', encoding="utf-8",  newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows([self.headers])
            writer.writerows(data)
        print(f"{csv_name} created")

        self.sftp_service.put(localfile, f"{self.remote_path}/{csv_name}")

    def get_filename(self, fecha):
        return ""

    def get_data(self, fecha):
        str_date = fecha.strftime("%Y-%m-%d")
        return self.db.fetch(self.query, {"fecha": str_date})

    def event_handler(self, event):
        self.__guard(event)
        date_format = DTFORMAT_BY_ALIAS[event['msg_body']['format']]
        fecha = dt.datetime.strptime(event['msg_body']['fec_ini'], date_format)
        self.execute(fecha)

    def __guard(self, event):
        msg_body_keys = event['msg_body'].keys()
        if 'fec_ini' not in msg_body_keys or 'format' not in msg_body_keys:
            raise Exception("Error no se encontro el atributo fec_ini o format")

        if event['msg_body']['format'] not in list(DTFORMAT_BY_ALIAS):
            raise Exception(f"Formato '{event['msg_body']['format']}' no valido")

class SendFlagHfc(SendSoporteClientesFile):
    def __init__(self, db, sftp_service):
        super().__init__(db, sftp_service)
        self.query = """select
            TO_CHAR(A.FECHA, 'DD/MM/YYYY') FECHA,
            A.MACADDRESS,
            A.PLANO,
            A.ALTO_SERVICIO,
            A.AUTOSATURADOS,
            A.EQUIPOS_APROPIADOS,
            A.VELOCIDAD_MAXIMA,
            A.REINICIOS,
            A.ALERTA_PLANO,
            A.IN_HOUSE,
            A.PEXT,
            A.CONSUMO_MINIMO,
            A.COBERTURA_WIFI,
            b.NRO_CLIENTE AS CODIGO_CLIENTE
        from FIJA_FLAG_HFC A
        LEFT JOIN FIJA_HFC_NRO_CLIENTE B ON 
        REPLACE(UPPER(A.MACADDRESS), ':', '') = REPLACE(UPPER(B.MAC_USUARIO), ':', '') 
        where fecha = to_date(:fecha, 'yyyy-mm-dd')"""
        self.headers = ["FECHA","MACADDRESS","PLANO","ALTO_SERVICIO","AUTOSATURADOS","EQUIPOS_APROPIADOS","VELOCIDAD_MAXIMA","REINICIOS","ALERTA_PLANO","IN_HOUSE","PEXT","CONSUMO_MINIMO","COBERTURA_WIFI","CODIGO_CLIENTE"]

    def get_filename(self, fecha):
        str_date_formated = fecha.strftime("%Y%m%d")
        return f"flags_hfc_{str_date_formated}.csv"


class SendFlagFtth(SendSoporteClientesFile):
    def __init__(self, db, sftp_service):
        super().__init__(db, sftp_service)
        self.query = """select 
            TO_CHAR(A.FECHA, 'DD/MM/YYYY') FECHA,
            A.SERIALNUMBER,
            A.PLANO,
            A.ALTO_USO_SERVICIO AS ALTO_SERVICIO,
            A.AUTOSATURADO AS AUTOSATURADOS,
            A.EQUIPOS_APROPIADOS, --
            A.VEL_MAXIMA AS VELOCIDAD_MAXIMA,
            A.REINICIOS, --
            A.ALERTA_PLANO, --
            A.IN_HOUSE, --
            A.PEXT, --
            A.CONSUMO AS CONSUMO_MINIMO,
            A.COBERTURA_WIFI COBERTURA_WIFI,
            b.NRO_CLIENTE AS CODIGO_CLIENTE
        from FIJA_FLAG_FTTH A
        LEFT JOIN FIJA_FTTH_NRO_CLIENTE B ON 
        UPPER(A.SERIALNUMBER) = UPPER(B.MAC_USUARIO)
        where fecha = to_date(:fecha, 'yyyy-mm-dd')"""
        self.headers = ["FECHA","SERIALNUMBER","PLANO","ALTO_SERVICIO","AUTOSATURADOS","EQUIPOS_APROPIADOS","VELOCIDAD_MAXIMA","REINICIOS","ALERTA_PLANO","IN_HOUSE","PEXT","CONSUMO_MINIMO","COBERTURA_WIFI","CODIGO_CLIENTE"]

    def get_filename(self, fecha):
        str_date_formated = fecha.strftime("%Y%m%d")
        return f"flags_ftth_{str_date_formated}.csv"


class SendScoreHfc(SendSoporteClientesFile):
    def __init__(self, db, sftp_service):
        super().__init__(db, sftp_service)
        self.query = """SELECT
            distinct 
            TO_CHAR(A.FECHA, 'DD/MM/YYYY') FECHA,
            a.macaddress, 
            a.plano, 
            a.device, 
            a.puntaje, 
            a.score, 
            a.auto, 
            a.equipo, 
            a.vel, 
            a.reinicio, 
            a.alerta_plano, 
            a.wifi, 
            a.in_house, 
            A.pext, 
            A.cant_sot,
            B.NRO_CLIENTE
        FROM FIJA_TSF_SCORE_MAC_30D A
        LEFT JOIN FIJA_HFC_NRO_CLIENTE B ON 
        REPLACE(UPPER(A.MACADDRESS), ':', '') = REPLACE(UPPER(B.MAC_USUARIO), ':', '') 
        where fecha = to_date(:fecha, 'yyyy-mm-dd')"""
        self.headers = ["FECHA","MACADDRESS","PLANO","DEVICE","PUNTAJE","SCORE","AUTO","EQUIPO","VEL","REINICIO","ALERTA_PLANO","WIFI","IN_HOUSE","PEXT","CANT_SOT","NRO_CLIENTE"]

    def get_filename(self, fecha):
        str_date_formated = fecha.strftime("%Y%m%d")
        return f"score_hfc_{str_date_formated}.csv"


class SendScoreFtth(SendSoporteClientesFile):
    def __init__(self, db, sftp_service):
        super().__init__(db, sftp_service)
        self.query = """SELECT
            distinct 
            TO_CHAR(A.FECHA_ARCHIVO, 'DD/MM/YYYY') FECHA,
            a.macaddress, 
            a.plano, 
            a.device, 
            a.puntaje, 
            a.score, 
            a.auto, 
            a.equipo, 
            a.vel, 
            a.reinicio, 
            a.alerta_plano, 
            a.wifi, 
            a.in_house, 
            A.pext, 
            A.cant_sot,
            B.NRO_CLIENTE
        FROM FIJA_TSF_SCORE_SN_30D A
        LEFT JOIN FIJA_FTTH_NRO_CLIENTE B ON 
        REPLACE(UPPER(A.MACADDRESS), ':', '') = REPLACE(UPPER(B.MAC_USUARIO), ':', '') 
        where fecha_archivo = to_date(:fecha, 'yyyy-mm-dd')"""
        self.headers = ["FECHA","MACADDRESS","PLANO","DEVICE","PUNTAJE","SCORE","AUTO","EQUIPO","VEL","REINICIO","ALERTA_PLANO","WIFI","IN_HOUSE","PEXT","CANT_SOT","NRO_CLIENTE"]

    def get_filename(self, fecha):
        str_date_formated = fecha.strftime("%Y%m%d")
        return f"score_ftth_{str_date_formated}.csv"


class SendOcurrenciasFija(SendSoporteClientesFile):
    def __init__(self, db, sftp_service):
        super().__init__(db, sftp_service)
        self.query = """SELECT
        TO_CHAR(RESULT_TIME, 'DD/MM/YYYY') RESULT_TIME,
        MAC,
        CUSTOMER_ID,
        NODO,
        DEVICE_NAME,
        ALERTA_PLANO,
        HORA_INICIO_EVENTO,
        HORA_FIN_EVENTO,
        DURACION_DEL_EVENTO
        FROM fija_reporte_ocurrencias
        where RESULT_TIME = to_date(:fecha, 'yyyy-mm-dd')"""
        self.headers = ["RESULT_TIME","MAC","CUSTOMER_ID","NODO","DEVICE_NAME","ALERTA_PLANO","HORA_INICIO_EVENTO","HORA_FIN_EVENTO","DURACION_DEL_EVENTO"]

    def get_filename(self, fecha):
        str_date_formated = fecha.strftime("%Y%m%d")
        return f"fija_ocurrencias_{str_date_formated}.csv"


class SendVmax(SendSoporteClientesFile):
    def __init__(self, db, sftp_service):
        super().__init__(db, sftp_service)
        self.query = """SELECT
        TO_CHAR(RESULT_TIME, 'DD/MM/YYYY') RESULT_TIME,
        MAC_ADDRESS,
        CUSTOMER_ID,
        NODO,
        DEVICE_NAME,
        PC_VELOCIDAD_ALCANZADA
        FROM fija_reporte_velocidad_maxima
        where RESULT_TIME = to_date(:fecha, 'yyyy-mm-dd')"""
        self.headers = ["RESULT_TIME","MAC_ADDRESS","CUSTOMER_ID","NODO","DEVICE_NAME","PC_VELOCIDAD_ALCANZADA"]

    def get_filename(self, fecha):
        str_date_formated = fecha.strftime("%Y%m%d")
        return f"fija_vmax_{str_date_formated}.csv"


class SendWifiHfc(SendSoporteClientesFile):
    def __init__(self, db, sftp_service):
        super().__init__(db, sftp_service)
        self.query = """SELECT
        TO_CHAR(FECHA, 'DD/MM/YYYY') FECHA, NRO_CLIENTE, MAC, DISPO_MENOR_60, TOTAL_DISP, PORCENTAJE, RANGO_PORCENTAJE, RANGO_CANT_DISP 
        FROM FIJA_REPORTE_WIFI_HFC
        where FECHA = to_date(:fecha, 'yyyy-mm-dd')"""
        self.headers = ["FECHA","NRO_CLIENTE","MAC","DISPO_MENOR_60","TOTAL_DISP","PORCENTAJE","RANGO_PORCENTAJE","RANGO_CANT_DISP"]
        self.remote_path = "/space/data/sftpserver/datawh/files/BASE_INCOGNITO/output"

    def get_filename(self, fecha):
        str_date_formated = fecha.strftime("%Y%m%d")
        return f"reporte_wifi_hfc_{str_date_formated}.csv"


class SendReiniciosFtthHfcDet(SendSoporteClientesFile):
    def __init__(self, db, sftp_service):
        super().__init__(db, sftp_service)
        self.query = """SELECT
        MACADDRESS, NRO_CLIENTE, PLANO, DISPLAYNAME, CANTIDAD_REINICIOS
        FROM Fija_Reporte_Reinicios_Ftth_Hfc_Det
        where RESULT_TIME = to_date(:fecha, 'yyyy-mm-dd')"""
        self.headers = ["MacAddress","nro_cliente","plano","displayName","cantidad_reinicios"]
        self.remote_path = "/space/data/sftpserver/datawh/files/BASE_INCOGNITO/output"

    def get_filename(self, fecha):
        str_date_formated = fecha.strftime("%Y%m%d")
        return f"reporte_reinicios_ftth_hfc_detallado_{str_date_formated}.csv"


class SendEquipoNoRecomendadoHfcDet(SendSoporteClientesFile):
    def __init__(self, db, sftp_service):
        super().__init__(db, sftp_service)
        self.query = """SELECT
        MACADDRESS, CUSTOMER_ID, NODO, DEVICE_NAME, N_PORTADORAS_CM, VELOCIDAD_CONTRATADA, PORCENTAJE_OFRECIDA_CM 
        FROM FIJA_REP_EQUIPO_NO_RECOMENDADO_HFC_DET
        where RESULT_TIME = to_date(:fecha, 'yyyy-mm-dd')"""
        self.headers = ["macaddress","customer_id","nodo","device_name","n_portadoras_cm","velocidad_contratada","porcentaje_ofrecida_cm"]
        self.remote_path = "/space/data/sftpserver/datawh/files/BASE_INCOGNITO/output"

    def get_filename(self, fecha):
        str_date_formated = fecha.strftime("%Y%m%d")
        return f"reporte_equipo_no_recomendado_hfc_detallado_{str_date_formated}.csv"
        

class SoporteClientesHandlerEventConsumer(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.1
        self.loop = False
        self.pronatel_configs = {}

        self.queue_handlers["soportecli.fija_flag_hfc.send_file"] = {'handler': SEND_FLAG_HFC, 'callback': lambda s, e: s.event_handler(e)}
        self.queue_handlers["soportecli.fija_flag_ftth.send_file"] = {'handler': SEND_FLAG_FTTH, 'callback': lambda s, e: s.event_handler(e)}
        self.queue_handlers["soportecli.fija_score_hfc.send_file"] = {'handler': SEND_SCORE_HFC, 'callback': lambda s, e: s.event_handler(e)}
        self.queue_handlers["soportecli.fija_score_ftth.send_file"] = {'handler': SEND_SCORE_FTTH, 'callback': lambda s, e: s.event_handler(e)}
        self.queue_handlers["soportecli.reporte_ocurrencias.send_file"] = {'handler': SEND_OCURRENCIAS_FIJA, 'callback': lambda s, e: s.event_handler(e)}
        self.queue_handlers["soportecli.reporte_velocidad_max.send_file"] = {'handler': SEND_VMAX, 'callback': lambda s, e: s.event_handler(e)}
        self.queue_handlers["soportecli.reporte_wifi_hfc.sendfile"] = {'handler': SEND_WIFI_HFC, 'callback': lambda s, e: s.event_handler(e)}
        self.queue_handlers["soportecli.reporte_reinicios_ftth_hfc_det.sendfile"] = {'handler': SEND_REINICIOS_FTTH_HFC_DET, 'callback': lambda s, e: s.event_handler(e)}
        self.queue_handlers["soportecli.rep_equipo_no_recomen_hfc_det.sendfile"] = {'handler': SEND_EQUIPO_NO_RECOMENDADO_HFC_DET, 'callback': lambda s, e: s.event_handler(e)}

        self.queue_ids = list(self.queue_handlers)