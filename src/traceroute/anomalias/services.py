from src.shared.config import STORAGE_DIR
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.traceroute.shared.services import TRACEROUTE_RESUMEN
import csv
import os

class SendTracerouteFileActiveIps:
    def __init__(self, ch_db, sftp_service):
        self.ch_db = ch_db
        self.sftp_service = sftp_service
        self.storage_dir = f"{STORAGE_DIR}fping"
        self.path_ipv4_list = [
            "Aeropuerto_ftth_398",
            "Aeropuerto_hfc_393",
            "aviacion_ftth_382",
            "aviacion_hfc_387",
            "Ayacucho_ftth_396",
            "Ayacucho_hfc_391",
            "Huancayo_ftth_384",
            "Huancayo_hfc_389",
            "Huanuco_ftth_397",
            "Huanuco_hfc_392",
            "Ica_ftth_395",
            "Ica_hfc_390",
            "lurin_ftth_381",
            "lurin_hfc_386",
            "san_juan_ftth_383",
            "san_juan_hfc_388",
            "santa_luzmila_ftth_380",
            "santa_luzmila_hfc_385",
        ]
        self.path_ipv6_list = [
            "Aeropuerto_ipv6_378",
            "Ayacucho_ipv6_376",
            "Huancayo_ipv6_374",
            "Huanuco_ipv6_377",
            "Ica_ipv6_375",
        ]

    def execute(self):
        self.sftp_service.useConnection('stlmedlatf01')
        
        print(f"ipv4:")
        for server_path in self.path_ipv4_list:
            self.send_to_server_ipv4(server_path)
        print()
        # print(f"ipv6:")
        # for server_path in self.path_ipv6_list:
        #     print(f"{server_path}/index1/tareas/Indicadores_Traceroute/files/active_ips.txt")
        #     self.sftp_service.put(localfilepath, f"{server_path}/index1/tareas/Indicadores_Traceroute/files/active_ips.txt")

    def write_temp_file(self, ip_list, filename):
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        
        with open(f"{self.storage_dir}/{filename}", "w", newline='', encoding="utf-8") as csv_ref:
            writer = csv.writer(csv_ref, lineterminator='\n')
            writer.writerows(ip_list)
        return f"{self.storage_dir}/{filename}"
    
    def send_to_server_ipv4(self, server_name):
        query = """select id_anomalia, 1 tipo, ip_add from dr_transporte_kpi.vw_tx_anomalias_ip_latencia
        where fecha_fin is null
        and servidor = {servidor_1:String}
        and id_anomalia not in (
            select anomalia_id from dr_transporte_kpi.tx_traceroute_cgnat_fuente
            where anomalia_tipo=1
        )
        and (ip_add not like '%:%' and not match(ip_add, '^\\d+\\.\\d+\\.\\d+\\.\\d+$'))
        union all
        select id_anomalia, 2 tipo, ip_add from dr_transporte_kpi.vw_tx_anomalias_ip_latencia
        where fecha_fin >= now() - interval '6' hour
        and servidor = {servidor_2:String}
        and id_anomalia not in (
            select anomalia_id from dr_transporte_kpi.tx_traceroute_cgnat_fuente
            where anomalia_tipo=2
        )
        and (ip_add not like '%:%' and not match(ip_add, '^\\d+\\.\\d+\\.\\d+\\.\\d+$'))
        """
        result = self.ch_db.fetch(query, {'servidor_1': server_name, 'servidor_2': server_name})

        localfilepath = self.write_temp_file(result, f'active_ips_{server_name}.txt')

        print(f"{server_name}/index1/tareas/Indicadores_Traceroute/files/active_ips.txt:", len(result))
        self.sftp_service.put(localfilepath, f"/var/index/{server_name}/index1/tareas/Indicadores_Traceroute/files/active_ips.txt")

    def send_to_server_ipv6(self, server_name):
        query = """select id_anomalia, 1 tipo, ip_add from dr_transporte_kpi.vw_tx_anomalias_ip_latencia
        where fecha_fin is null
        and servidor = {servidor_1:String}
        and id_anomalia not in (
            select anomalia_id from dr_transporte_kpi.tx_traceroute_cgnat_fuente
            where anomalia_tipo=1
        )
        and (ip_add_resuelta like '%:%')
        union all
        select id_anomalia, 2 tipo, ip_add from dr_transporte_kpi.vw_tx_anomalias_ip_latencia
        where fecha_fin >= now() - interval '6' hour
        and servidor = {servidor_2:String}
        and id_anomalia not in (
            select anomalia_id from dr_transporte_kpi.tx_traceroute_cgnat_fuente
            where anomalia_tipo=2
        )
        and (ip_add_resuelta like '%:%')
        """
        result = self.ch_db.fetch(query, {'servidor_1': server_name, 'servidor_2': server_name})

        localfilepath = self.write_temp_file(result, f'active_ips_{server_name}.txt')

        print(f"{server_name}/index1/tareas/Indicadores_Traceroute/files/active_ips.txt:", len(result))
        self.sftp_service.put(localfilepath, f"/var/index/{server_name}/index1/tareas/Indicadores_Traceroute/files/active_ips.txt")


class TracerouteResumen:
    def __init__(self, ch_db):
        self.ch_db = ch_db

    def execute(self):
        query = """insert into dr_transporte_kpi.tx_traceroute_cgnat_anomalia(
        result_time, ip, hopnum, ip1, latency1, ip2, latency2, servidor, archivo
        )
        select
        result_time, ip, hopnum, ip1, latency1, ip2, latency2, servidor, archivo
        from dr_transporte_kpi.tx_traceroute_cgnat_fuente
        where result_time >= date_trunc('day', now()) - interval '7' day
        and (anomalia_id, anomalia_tipo, result_time) in (
            select anomalia_id,anomalia_tipo,  min(result_time) from dr_transporte_kpi.tx_traceroute_cgnat_fuente
            where result_time >= date_trunc('day', now()) - interval '7' day
            group by anomalia_id, anomalia_tipo
        )
        and (anomalia_id, anomalia_tipo) not in (
            select anomalia_id, anomalia_tipo from dr_transporte_kpi.tx_traceroute_cgnat_anomalia
            where result_time >= date_trunc('day', now()) - interval '7' day
        )"""
        self.ch_db.query(query, {})
        print("se cargaron correctamente las anomalias")

    def event_handler(self, event):
        self.execute()


class TracerouteResumenConsumer(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service):
        super().__init__(queue_service, app_container, notification_service)
        self.max_check_attemps = 1
        self.sleep_time_in_work = 0.1
        self.loop = False
    
    def execute(self):
        self.queue_handlers['traceroute.resumen_ch'] = {'handler': TRACEROUTE_RESUMEN, 'callback': lambda s, e: s.event_handler(e)}
        self.queue_ids = list(self.queue_handlers)
        super().execute()
