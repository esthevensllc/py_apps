from src.shared.config import STORAGE_DIR
import csv
import os

class SendTracerouteFileActiveIps:
    def __init__(self, ch_db, sftp_service):
        self.ch_db = ch_db
        self.sftp_service = sftp_service
        self.storage_dir = f"{STORAGE_DIR}fping"
        self.path_ipv4_list = [
            "/var/index/Aeropuerto_ftth_398",
            "/var/index/Aeropuerto_hfc_393",
            "/var/index/aviacion_ftth_382",
            "/var/index/aviacion_hfc_387",
            "/var/index/Ayacucho_ftth_396",
            "/var/index/Ayacucho_hfc_391",
            "/var/index/Huancayo_ftth_384",
            "/var/index/Huancayo_hfc_389",
            "/var/index/Huanuco_ftth_397",
            "/var/index/Huanuco_hfc_392",
            "/var/index/Ica_ftth_395",
            "/var/index/Ica_hfc_390",
            "/var/index/lurin_ftth_381",
            "/var/index/lurin_hfc_386",
            "/var/index/san_juan_ftth_383",
            "/var/index/san_juan_hfc_388",
            "/var/index/santa_luzmila_ftth_380",
            "/var/index/santa_luzmila_hfc_385",
        ]
        self.path_ipv6_list = [
            "/var/index/Aeropuerto_ipv6_378",
            "/var/index/Ayacucho_ipv6_376",
            "/var/index/Huancayo_ipv6_374",
            "/var/index/Huanuco_ipv6_377",
            "/var/index/Ica_ipv6_375",
        ]

    def execute(self):
        ipsv4_list = self.ch_db.fetch(f"""select distinct ip_add from dr_transporte_kpi.vw_tx_anomalias_ip_latencia
        where fecha_fin is null
        and ip_add not like '%:%'
        and not match(ip_add, '^\\d+\\.\\d+\\.\\d+\\.\\d+$')
        """)
        localfilepath = self.write_temp_file(ipsv4_list)
        self.sftp_service.useConnection('stlmedlatf01')
        
        print(f"ipv4: {len(ipsv4_list)}")
        for server_path in self.path_ipv4_list:
            print(f"{server_path}/index1/tareas/Indicadores_Traceroute/files/active_ips.txt")
            self.sftp_service.put(localfilepath, f"{server_path}/index1/tareas/Indicadores_Traceroute/files/active_ips.txt")

        ipsv6_list = self.ch_db.fetch(f"""select distinct ip_add from dr_transporte_kpi.vw_tx_anomalias_ip_latencia
        where fecha_fin is null
        and (
            ip_add like '%:%'
            or (ip_add not like '%:%' and not match(ip_add, '^\\d+\\.\\d+\\.\\d+\\.\\d+$'))
        )""")
        localfilepath = self.write_temp_file(ipsv6_list)
        print()
        print(f"ipv6: {len(ipsv6_list)}")
        for server_path in self.path_ipv6_list:
            print(f"{server_path}/index1/tareas/Indicadores_Traceroute/files/active_ips.txt")
            self.sftp_service.put(localfilepath, f"{server_path}/index1/tareas/Indicadores_Traceroute/files/active_ips.txt")

    def write_temp_file(self, ip_list):
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        
        with open(f"{self.storage_dir}/active_ips.txt", "w", newline='', encoding="utf-8") as csv_ref:
            writer = csv.writer(csv_ref, lineterminator='\n')
            writer.writerows(ip_list)
        return f"{self.storage_dir}/active_ips.txt"
