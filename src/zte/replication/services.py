import datetime as dt
from src.shared.database.ClickHouseDB import ClickHouseDB
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.shared.config import DTFORMAT_BY_ALIAS
from src.zte.shared.services import (
    LOAD_ZTE_MAESTRO,
    LOAD_ZTE_EQUIPOS_TX_DESEMP,
)

class EventMapper:
    def execute(self, fecha):
        pass

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


class LoadZteMaestroFromOracle(EventMapper):
    def __init__(self, oracle_db, ch):
        self.oracle_db = oracle_db
        self.ch = ch

    def execute(self, fecha):
        data = self.get_data(fecha)
        print(f"data:", len(data))
        if len(data) > 0:
            self.import_data(data, fecha)
            print(f"tx_maestro_zte_intrfcs_temp cargado")
            print(f"tx_maestro_zte_intrfcs cargado")
        else:
            print(f"no se cargo tx_maestro_zte_intrfcs porque no se tiene registros")

    def get_data(self, fecha: dt.datetime):
        query = """
        select
        ME_ID, ME_POSITION, ME, SLOT, PORT_NUMBER, SIP, IP, FTP_S, FTP, PORT_NAME, PORT_TYPE,
        LAYER_RATE, ADMINISTRATIVE_STATUS, DESCRIPTION, BOARD_NAME, OPTICAL_ELECTRIC_PORT,
        L2MTU_BYTE, to_char(DIA_TRAFICO, 'yyyy-mm-dd hh24:mi:ss') DIA_TRAFICO
        from TX_MAESTRO_ZTE_INTRFCS
        where DIA_TRAFICO = to_date(:fecha, 'yyyy-mm-dd')
        """
        result = self.oracle_db.fetch(query, {'fecha': fecha.strftime(DTFORMAT_BY_ALIAS['dxd'])})
        for row_index in range(len(result)):
            row = list(result[row_index])
            row[0] = row[0] if row[0] is not None else ''
            row[1] = row[1] if row[1] is not None else ''
            row[2] = row[2] if row[1] is not None else ''
            row[3] = row[3] if row[3] is not None else ''
            row[4] = row[4] if row[4] is not None else ''
            result[row_index] = row
        return result
    
    def import_data(self, data, fecha: dt.datetime):
        bindings = [
            {"name": 'me_id', "type": ClickHouseDB.STRING},
            {"name": 'me_position', "type": ClickHouseDB.STRING},
            {"name": 'me', "type": ClickHouseDB.STRING},
            {"name": 'slot', "type": ClickHouseDB.STRING},
            {"name": 'port_number', "type": ClickHouseDB.STRING},
            {"name": 'sip', "type": ClickHouseDB.STRING},
            {"name": 'ip', "type": ClickHouseDB.STRING},
            {"name": 'ftp_s', "type": ClickHouseDB.FLOAT},
            {"name": 'ftp', "type": ClickHouseDB.STRING},
            {"name": 'port_name', "type": ClickHouseDB.STRING},
            {"name": 'port_type', "type": ClickHouseDB.STRING},
            {"name": 'layer_rate', "type": ClickHouseDB.STRING},
            {"name": 'administrative_status', "type": ClickHouseDB.STRING},
            {"name": 'description', "type": ClickHouseDB.STRING},
            {"name": 'board_name', "type": ClickHouseDB.STRING},
            {"name": 'optical_electric_port', "type": ClickHouseDB.STRING},
            {"name": 'l2mtu_byte', "type": ClickHouseDB.STRING},
            {"name": 'dia_trafico', "type": ClickHouseDB.DATETIME},
        ]
        config = {'template': 'zte.tx_maestro_zte_intrfcs_temp', 'bindings': bindings, 'row_type': 'array', 'limit_to_commit': 5000}
        str_fields = ",".join(list(map(lambda row: row['name'], bindings)))

        self.ch.query("truncate table zte.tx_maestro_zte_intrfcs_temp")
        self.ch.insert(config, data)

        str_fecha = fecha.strftime('%Y%m%d')
        self.ch.query(f"alter table zte.tx_maestro_zte_intrfcs drop partition '{str_fecha}'")
        self.ch.query(f"insert into zte.tx_maestro_zte_intrfcs({str_fields}) select {str_fields} from zte.tx_maestro_zte_intrfcs_temp")



class LoadZteEquiposTxDesempFromOracle(EventMapper):
    def __init__(self, oracle_db, ch):
        self.oracle_db = oracle_db
        self.ch = ch

    def execute(self, fecha):
        data = self.get_data(fecha)
        print(f"data:", len(data))
        if len(data) > 0:
            self.import_data(data, fecha)
            print(f"equipos_tx_desemp_temp cargado")
            print(f"equipos_tx_desemp cargado")
        else:
            print(f"no se cargo equipos_tx_desemp porque no se tiene registros")

    def get_data(self, fecha: dt.datetime):
        query = """
        select
        GESTOR, TIPO_RED, NOMBRE_EQUIPO, MODELO_EQUIPO, CODIGOSITE, NOMBRESITE, ORIGEN_SITE, TIPO_SITIO,
        LONGITUD, LATITUD, DEPARTAMENTO, PROVINCIA, DISTRITO, OPTICAL_NE,
        to_char(F_LAST_UPDATE, 'yyyy-mm-dd hh24:mi:ss') F_LAST_UPDATE_
        from equipos_tx_desemp
        """
        result = self.oracle_db.fetch(query)
        for row_index in range(len(result)):
            row = list(result[row_index])
            result[row_index] = row
        return result
    
    def import_data(self, data, fecha: dt.datetime):
        bindings = [
            {"name": 'gestor', "type": ClickHouseDB.STRING},
            {"name": 'tipo_red', "type": ClickHouseDB.STRING},
            {"name": 'nombre_equipo', "type": ClickHouseDB.STRING},
            {"name": 'modelo_equipo', "type": ClickHouseDB.STRING},
            {"name": 'codigosite', "type": ClickHouseDB.STRING},
            {"name": 'nombresite', "type": ClickHouseDB.STRING},
            {"name": 'origen_site', "type": ClickHouseDB.STRING},
            {"name": 'tipo_sitio', "type": ClickHouseDB.STRING},
            {"name": 'longitud', "type": ClickHouseDB.FLOAT},
            {"name": 'latitud', "type": ClickHouseDB.FLOAT},
            {"name": 'departamento', "type": ClickHouseDB.STRING},
            {"name": 'provincia', "type": ClickHouseDB.STRING},
            {"name": 'distrito', "type": ClickHouseDB.STRING},
            {"name": 'optical_ne', "type": ClickHouseDB.STRING},
            {"name": 'f_last_update', "type": ClickHouseDB.DATETIME},
        ]
        config = {'template': 'zte.equipos_tx_desemp_temp', 'bindings': bindings, 'row_type': 'array', 'limit_to_commit': 5000}
        str_fields = ",".join(list(map(lambda row: row['name'], bindings)))

        self.ch.query("truncate table zte.equipos_tx_desemp_temp")
        self.ch.insert(config, data)

        self.ch.query(f"truncate table zte.equipos_tx_desemp")
        self.ch.query(f"insert into zte.equipos_tx_desemp({str_fields}) select {str_fields} from zte.equipos_tx_desemp_temp")


class ZteReplicatorEventConsumer(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.1
        self.loop = False
        self.pronatel_configs = {}

        self.queue_handlers["ch_zte.tx_maestro_zte_intrfcs.load"] = {'handler': LOAD_ZTE_MAESTRO, 'callback': lambda s, e: s.event_handler(e)}
        self.queue_handlers["ch_zte.equipos_tx_desemp.load"] = {'handler': LOAD_ZTE_EQUIPOS_TX_DESEMP, 'callback': lambda s, e: s.event_handler(e)}

        self.queue_ids = list(self.queue_handlers)
