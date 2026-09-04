import datetime as dt
from src.shared.database.ClickHouseDB import ClickHouseDB

class LoadTxMaestro:
    def __init__(self, oracle_db, ch):
        self.oracle_db = oracle_db
        self.ch = ch

    def execute(self):
        data = self.get_data()
        print(f"data:", len(data))
        if len(data) > 0:
            self.import_data(data)
            print(f"tx_nuevo_maetro_temp cargado")
            print(f"tx_nuevo_maetro2 cargado")
        else:
            print(f"no se cargo tx_nuevo_maetro2 porque no se tiene registros")

    def get_data(self):
        query = """
        select
        codigo,nombre_site,capa,vendor,region,departamento,provincia,estado,clase,tipo,detalle_tipo,tipo_enlace,servicio,distrito,to_char(result_time, 'yyyy-mm-dd hh24:mi:ss') result_time,
        monitoring_status,instance_name,resource_name,template,ne_name,origen,destino,puerto_origen,interface,interface_description,
        interface_type,ipv4_interface_ip,interface_speed_bps,interface_admin_status,interface_operator_status,inbound_rate_bps,
        outbound_rate_bps,inbound_bw_utilization,outbound_bw_utilization,inbound_crc_error_packets,the_number,max_rate_bps,
        max_bw_utilization,granularity,alarm_status,grupo,created_at_ne_time_zone,latest_start_time_ne_time_zone,remarks
        from tx_nuevo_maetro2
        """
        result = self.oracle_db.fetch(query)
        for row_index in range(len(result)):
            result[row_index] = list(result[row_index])
        return result
    
    def import_data(self, data):
        bindings = [
            {"name": 'codigo', "type": ClickHouseDB.STRING},
            {"name": 'nombre_site', "type": ClickHouseDB.STRING},
            {"name": 'capa', "type": ClickHouseDB.STRING},
            {"name": 'vendor', "type": ClickHouseDB.STRING},
            {"name": 'region', "type": ClickHouseDB.STRING},
            {"name": 'departamento', "type": ClickHouseDB.STRING},
            {"name": 'provincia', "type": ClickHouseDB.STRING},
            {"name": 'estado', "type": ClickHouseDB.STRING},
            {"name": 'clase', "type": ClickHouseDB.STRING},
            {"name": 'tipo', "type": ClickHouseDB.STRING},
            {"name": 'detalle_tipo', "type": ClickHouseDB.STRING},
            {"name": 'tipo_enlace', "type": ClickHouseDB.STRING},
            {"name": 'servicio', "type": ClickHouseDB.STRING},
            {"name": 'distrito', "type": ClickHouseDB.STRING},
            {"name": 'result_time', "type": ClickHouseDB.DATETIME},
            {"name": 'monitoring_status', "type": ClickHouseDB.STRING},
            {"name": 'instance_name', "type": ClickHouseDB.STRING},
            {"name": 'resource_name', "type": ClickHouseDB.STRING},
            {"name": 'template', "type": ClickHouseDB.STRING},
            {"name": 'ne_name', "type": ClickHouseDB.STRING},
            {"name": 'origen', "type": ClickHouseDB.STRING},
            {"name": 'destino', "type": ClickHouseDB.STRING},
            {"name": 'puerto_origen', "type": ClickHouseDB.STRING},
            {"name": 'interface', "type": ClickHouseDB.STRING},
            {"name": 'interface_description', "type": ClickHouseDB.STRING},
            {"name": 'interface_type', "type": ClickHouseDB.STRING},
            {"name": 'ipv4_interface_ip', "type": ClickHouseDB.STRING},
            {"name": 'interface_speed_bps', "type": ClickHouseDB.STRING},
            {"name": 'interface_admin_status', "type": ClickHouseDB.STRING},
            {"name": 'interface_operator_status', "type": ClickHouseDB.STRING},
            {"name": 'inbound_rate_bps', "type": ClickHouseDB.STRING},
            {"name": 'outbound_rate_bps', "type": ClickHouseDB.STRING},
            {"name": 'inbound_bw_utilization', "type": ClickHouseDB.STRING},
            {"name": 'outbound_bw_utilization', "type": ClickHouseDB.STRING},
            {"name": 'inbound_crc_error_packets', "type": ClickHouseDB.STRING},
            {"name": 'the_number', "type": ClickHouseDB.STRING},
            {"name": 'max_rate_bps', "type": ClickHouseDB.STRING},
            {"name": 'max_bw_utilization', "type": ClickHouseDB.STRING},
            {"name": 'granularity', "type": ClickHouseDB.STRING},
            {"name": 'alarm_status', "type": ClickHouseDB.STRING},
            {"name": 'grupo', "type": ClickHouseDB.STRING},
            {"name": 'created_at_ne_time_zone', "type": ClickHouseDB.STRING},
            {"name": 'latest_start_time_ne_time_zone', "type": ClickHouseDB.STRING},
            {"name": 'remarks', "type": ClickHouseDB.STRING},
        ]
        config = {'template': 'nce.tx_nuevo_maetro_temp', 'bindings': bindings, 'row_type': 'array', 'limit_to_commit': 5000}
        str_fields = ",".join(list(map(lambda row: row['name'], bindings)))

        self.ch.query("truncate table nce.tx_nuevo_maetro_temp")
        self.ch.insert(config, data)

        self.ch.query("truncate table nce.tx_nuevo_maetro2")
        self.ch.query(f"insert into nce.tx_nuevo_maetro2({str_fields}) select {str_fields} from nce.tx_nuevo_maetro_temp")