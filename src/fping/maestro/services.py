import csv
import os
import asyncio
import aiohttp
import datetime as dt
from src.shared.config import STORAGE_DIR

class IpInfoFinder:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.max_workers = 5

    async def find(self, ips: list):
        semaphore = asyncio.Semaphore(self.max_workers)
        result = []
        async with aiohttp.ClientSession() as session:
            # tasks = [asyncio.create_task(self._fetch(semaphore, session, ip)) for ip in ips]
            # result = [await task for task in asyncio.as_completed(tasks)]
            # print(result)
            tasks = [self._fetch(semaphore, session, ip) for ip in ips]
            result = await asyncio.gather(*tasks)
            result = [value for i, value in enumerate(result)]
        return result

    async def _fetch(self, semaphore, session: aiohttp.ClientSession, ip: str):
        async with semaphore:
            async with session.get(f"{self.base_url}/{ip}?token={self.token}", proxy="http://C19884:BRUTALIDAD2025**@claro-proxy:80") as response:
                if response.status == 200:
                    result = await response.json()
                    return {'ip': ip, 'response': result}
                else:
                    text = await response.text()
                    return {'ip': ip, 'response': Exception(text)}

class FpingIpFinderProcess:
    def __init__(self, queue_service, ip_info_finder: IpInfoFinder, ch_db):
        self.ch_db = ch_db
        self.queue_service = queue_service
        self.ip_info_finder = ip_info_finder
        self.queue_id = "fping_cgnat.find_ip_details"
        self.max_number_of_messages = 100
        self.tablename = "dr_transporte_kpi.maestro_tx_fping_ips_busqueda"
        self.maestro_updated = MaestroFpingCgnatUpdater(ch_db)

    def execute(self):
        print(f"{self.queue_id}")
        print("max_number_of_messages", self.max_number_of_messages)
        reload_maestro = False

        while True:
            if self.count_last_api_usage() >= 900:
                print("No se puede superar el maximo de busquedas permitidas")
                break

            fecha_ini = dt.datetime.now()
            events = self.queue_service.receive_message(self.queue_id, self.max_number_of_messages)
            if len(events) == 0:
                break

            try:
                ips = [row['msg_body'].get('ip') for row in events]
                result = self.find_ip_destails(ips)
                valid_result = list(filter(lambda row: not isinstance(row['response'], Exception), result))
                error_result = list(filter(lambda row: isinstance(row['response'], Exception), result))
                ok_ips = {}
                error_ips = {}
                for row in valid_result:
                    ok_ips[row['ip']] = 1
                for row in error_result:
                    error_ips[row['ip']] = str(row['response'])

                self._insert_result(self._map_result(valid_result))
                fecha_fin = dt.datetime.now()

                events = [{
                    'id': row['id'],
                    'estado': ok_ips.get(row['msg_body'].get('ip'), -1),
                    'message': error_ips.get(row['msg_body'].get('ip')),
                    'fecha_ini_exec': fecha_ini.strftime('%d/%m/%Y %H:%M:%S'),
                    'fecha_fin_exec': fecha_fin.strftime('%d/%m/%Y %H:%M:%S'),
                } for row in events]
                
                for row in events:
                    self.queue_service.updateResultOfEvent(row)

                reload_maestro = True
            except BaseException as error:
                fecha_fin = dt.datetime.now()
                events = [{
                    'id': row['id'],
                    'estado': -1,
                    'message': str(error),
                    'fecha_ini_exec': fecha_ini.strftime('%d/%m/%Y %H:%M:%S'),
                    'fecha_fin_exec': fecha_fin.strftime('%d/%m/%Y %H:%M:%S'),
                } for row in events]
                for row in events:
                    self.queue_service.updateResultOfEvent(row)
        
        if reload_maestro:
            print(f"actualizando proceso")
            self.maestro_updated.execute()

    def count_last_api_usage(self):
        result = self.ch_db.fetch(f"select count(*) from {self.tablename} where fecha >= now() - interval '1' day")
        return result[0][0]

    def find_ip_destails(self, ips):
        return asyncio.run(self.ip_info_finder.find(ips))
    
    def _map_result(self, result):
        result_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        mapped_data = []
        for row in result:
            data = row['response']
            mapped_data.append([
                result_time,
                data['ip'],
                data.get('city', ''),
                data.get('region', ''),
                data.get('country', ''),
                data.get('loc', ''),
                data.get('org', ''),
                data.get('postal', ''),
                data.get('timezone', '')
            ])
        return mapped_data
    
    def _insert_result(self, data):
        print(f"table:", self.tablename)
        print(f"data:", len(data))
        config = {
            "template": self.tablename,
            "row_type": "array",
            "bindings": [
                {'name': 'fecha', 'type': 'datetime'},
                {'name': 'ip_add', 'type': 'string'},
                {'name': 'city', 'type': 'string'},
                {'name': 'region', 'type': 'string'},
                {'name': 'country', 'type': 'string'},
                {'name': 'loc', 'type': 'string'},
                {'name': 'org', 'type': 'string'},
                {'name': 'postal', 'type': 'string'},
                {'name': 'timezone', 'type': 'string'},
            ]
        }
        self.ch_db.insert(config, data)


class MaestroFpingCgnatUpdater:
    def __init__(self, ch_db):
        self.ch_db = ch_db

    def execute(self):
        max_id_ip = self.ch_db.fetch(f"select max(id_ip) from dr_transporte_kpi.maestro_tx_fping_ips")
        max_id_ip = max_id_ip[0][0]

        self.ch_db.query(f"truncate table dr_transporte_kpi.maestro_tx_fping_ips_temp")

        query_update = f"""insert into dr_transporte_kpi.maestro_tx_fping_ips_temp(
        id_ip,fecha,ip_add,city,region,country,loc,org,postal,timezone,tipo_ip,estado,site,
        protocolo,servicio,nombre,red,asn_domain,asn_route,asn_type,host_name,servidor_medicion,region_red,
        flag_protected
        )
        select
        a.id_ip,
        a.fecha,
        a.ip_add,
        case when b.city != '' then b.city else a.city end city,
        case when b.region != '' then b.region else a.region end region,
        case when b.country != '' then b.country else a.country end country,
        case when b.loc != '' then b.loc else a.loc end loc,
        case when b.org != '' then b.org else a.org end org,
        case when b.postal != '' then b.postal else a.postal end postal,
        case when b.timezone != '' then b.timezone else a.timezone end timezone,
        a.tipo_ip,
        1 estado,
        a.site,
        a.protocolo,
        a.servicio,
        a.nombre,
        a.red,
        a.asn_domain,
        a.asn_route,
        a.asn_type,
        a.host_name,
        a.servidor_medicion,
        a.region_red,
        a.flag_protected
        from dr_transporte_kpi.maestro_tx_fping_ips a
        left join (
            select * from (
                select a.*, row_number() over (partition by ip_add order by fecha desc) as rownumber from dr_transporte_kpi.maestro_tx_fping_ips_busqueda a
            )
            where rownumber = 1
        ) b
        on b.ip_add = a.ip_add"""
        self.ch_db.query(query_update)

        query_insert = f"""insert into dr_transporte_kpi.maestro_tx_fping_ips_temp(
        id_ip,fecha,ip_add,city,region,country,loc,org,postal,timezone,tipo_ip,estado,protocolo
        )
        select
        row_number() over () + {max_id_ip} id_ip,
        fecha,ip_add,city,region,country,loc,org,postal,timezone,
        null tipo_ip,
        1 estado,
        case
            when ip_add like '%:%' then 'IPV6'
            else 'IPV4'
        end protocolo
        from (
            select * from (
                select a.*, row_number() over (partition by ip_add order by fecha desc) as rownumber from dr_transporte_kpi.maestro_tx_fping_ips_busqueda a
            )
            where rownumber = 1
        ) a
        left join dr_transporte_kpi.maestro_tx_fping_ips b
        on b.ip_add = a.ip_add
        where b.ip_add = ''
        """
        self.ch_db.query(query_insert)

        query_update = """alter table dr_transporte_kpi.maestro_tx_fping_ips_temp update estado = 0
        where not (
            tipo_ip in ('ROUTER_CGNAT', 'CACHING', 'DNS', 'OUT_INTER')
            or ip_add in (
                select server_ip from dr_transporte_kpi.inventario_top_ips
                where semana = (select max(semana) from dr_transporte_kpi.inventario_top_ips)
            )
            or flag_protected = 1
        )
        """
        self.ch_db.query(query_update)

        self.ch_db.query(f"truncate table dr_transporte_kpi.maestro_tx_fping_ips")

        insert_from_temp = f"""insert into dr_transporte_kpi.maestro_tx_fping_ips(
        id_ip,fecha,ip_add,city,region,country,loc,org,postal,timezone,tipo_ip,estado,site,
        protocolo,servicio,nombre,red,asn_domain,asn_route,asn_type,host_name,servidor_medicion,region_red,
        flag_protected
        )
        select
        id_ip,fecha,ip_add,city,region,country,loc,org,postal,timezone,tipo_ip,estado,site,
        protocolo,servicio,nombre,red,asn_domain,asn_route,asn_type,host_name,servidor_medicion,region_red,
        flag_protected
        from dr_transporte_kpi.maestro_tx_fping_ips_temp"""

        self.ch_db.query(insert_from_temp)


class SendFileActiveIps:
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
        ipsv4_list = self.ch_db.fetch(f"""select ip_add from dr_transporte_kpi.maestro_tx_fping_ips
        where estado = 1
        and ip_add not like '%:%'
        """)
        localfilepath = self.write_temp_file(ipsv4_list)
        self.sftp_service.useConnection('stlmedlatf01')
        
        print(f"ipv4: {len(ipsv4_list)}")
        for server_path in self.path_ipv4_list:
            print(f"{server_path}/index1/tareas/Indicadores_Fping/files/active_ips.txt")
            self.sftp_service.put(localfilepath, f"{server_path}/index1/tareas/Indicadores_Fping/files/active_ips.txt")

        ipsv6_list = self.ch_db.fetch(f"""select ip_add from dr_transporte_kpi.maestro_tx_fping_ips
        where estado = 1
        and (
            ip_add like '%:%'
            or (ip_add not like '%:%' and not match(ip_add, '^\\d+\\.\\d+\\.\\d+\\.\\d+$'))
        )
        """)
        localfilepath = self.write_temp_file(ipsv6_list)
        print()
        print(f"ipv6: {len(ipsv6_list)}")
        for server_path in self.path_ipv6_list:
            print(f"{server_path}/index1/tareas/Indicadores_Fping/files/active_ips.txt")
            self.sftp_service.put(localfilepath, f"{server_path}/index1/tareas/Indicadores_Fping/files/active_ips.txt")

    def write_temp_file(self, ip_list):
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        
        with open(f"{self.storage_dir}/active_ips.txt", "w", newline='') as csv_ref:
            writer = csv.writer(csv_ref)
            writer.writerows(ip_list)
            # for row in ip_list:
            #     writer.writerow(row)

        return f"{self.storage_dir}/active_ips.txt"