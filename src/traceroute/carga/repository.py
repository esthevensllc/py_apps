from src.shared.carga.repository import InMemoryConfigRepository

class InMemoryTracerouteConfigRepository(InMemoryConfigRepository):
    def __init__(self):
        self.config_by_group = {
            'traceroute': {
                'id': '1',
                # 'name': 'Aeropuerto_ftth_398',
                # 'type': 'alarm',
                # 'server_id': 'cdr',
                'work_dir': "/var/index/{server_name}/index2/estadisticas/Indicadores_Traceroute/{str_date}",
                'wk_date_format': '%Y%m%d',
                'wk_loop_time': '{"days": 1}',
                'file_pattern': '^mediciones_traceroute_{server_name}_([0-9]{14}).csv$',
                'file_date_format': '%Y%m%d%H%M%S',
                'file_delimiter': ',',
                'skip_lines': 1,
                'chunk_limit': 1000,
                'tablename': "dr_transporte_kpi.tx_traceroute_cgnat_fuente",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': None,
                'exec_after_st': """BEGIN
                    PK_PADM_QUEUE.SP_TRACEROUTE_RESUMEN_PRODUCER;
                END;""",
                'files_permission': None,
                'search_time_ago': '{"days": 4}',
                'loop_time': '{"minutes": 1}',
                'steps': None,
                'event_format': 'mxm',
                "msg_send_filename": True,
                "msg_send_granularity": True,
                'm_group': 'traceroute',
                'fields': [
                    {'fieldname': "anomalia_id", 'src_fieldname': "anomalia_id", 'type': "varchar2"},
                    {'fieldname': "anomalia_tipo", 'src_fieldname': "anomalia_tipo", 'type': "varchar2"},
                    {'fieldname': "result_time", 'src_fieldname': "timestamp", 'type': "date"},
                    {'fieldname': "ip", 'src_fieldname': "ip", 'type': "varchar2"},
                    {'fieldname': "hopnum", 'src_fieldname': "hopnum", 'type': "number"},
                    {'fieldname': "ip1", 'src_fieldname': "ip1", 'type': "varchar2"},
                    {'fieldname': "latency1", 'src_fieldname': "latency1", 'type': "number"},
                    {'fieldname': "ip2", 'src_fieldname': "ip2", 'type': "varchar2"},
                    {'fieldname': "latency2", 'src_fieldname': "latency2", 'type': "number"},
                    {'fieldname': "servidor", 'src_fieldname': "server_name", 'type': "varchar2", 'to_reload': 1, 'reload_argument': '{server_name}'},
                    {'fieldname': "archivo", 'src_fieldname': "filename", 'type': "varchar2", 'to_reload': 1, 'reload_argument': '{filename}'},
                ]
            }
        }
        self.config_by_id = {
            "1": {
                "server_id": "stlmedlatf01",
                "server_name": "Aeropuerto_ftth_398",
                'm_group': 'traceroute',
                'queue_id': "traceroute.aeropuerto_ftth_398",
            },
            "2": {
                "server_id": "stlmedlatf01",
                "server_name": "Aeropuerto_hfc_393",
                'm_group': 'traceroute',
                'queue_id': "traceroute.aeropuerto_hfc_393",
            },
            "3": {
                "server_id": "stlmedlatf01",
                "server_name": "Aeropuerto_ipv6_378",
                'm_group': 'traceroute',
                'queue_id': "traceroute.aeropuerto_ipv6_378",
            },
            "4": {
                "server_id": "stlmedlatf01",
                "server_name": "aviacion_ftth_382",
                'm_group': 'traceroute',
                'queue_id': "traceroute.aviacion_ftth_382",
            },
            "5": {
                "server_id": "stlmedlatf01",
                "server_name": "aviacion_hfc_387",
                'm_group': 'traceroute',
                'queue_id': "traceroute.aviacion_hfc_387",
            },
            "6": {
                "server_id": "stlmedlatf01",
                "server_name": "Ayacucho_ftth_396",
                'm_group': 'traceroute',
                'queue_id': "traceroute.ayacucho_ftth_396",
            },
            "7": {
                "server_id": "stlmedlatf01",
                "server_name": "Ayacucho_hfc_391",
                'm_group': 'traceroute',
                'queue_id': "traceroute.ayacucho_hfc_391",
            },
            "8": {
                "server_id": "stlmedlatf01",
                "server_name": "Ayacucho_ipv6_376",
                'm_group': 'traceroute',
                'queue_id': "traceroute.ayacucho_ipv6_376",
            },
            "9": {
                "server_id": "stlmedlatf01",
                "server_name": "Ica_ftth_395",
                'm_group': 'traceroute',
                'queue_id': "traceroute.ica_ftth_395",
            },
            "10": {
                "server_id": "stlmedlatf01",
                "server_name": "Ica_hfc_390",
                'm_group': 'traceroute',
                'queue_id': "traceroute.ica_hfc_390",
            },
            "11": {
                "server_id": "stlmedlatf01",
                "server_name": "Ica_ipv6_375",
                'm_group': 'traceroute',
                'queue_id': "traceroute.ica_ipv6_375",
            },
            "12": {
                "server_id": "stlmedlatf01",
                "server_name": "lurin_ftth_381",
                'm_group': 'traceroute',
                'queue_id': "traceroute.lurin_ftth_381",
            },
            "13": {
                "server_id": "stlmedlatf01",
                "server_name": "lurin_hfc_386",
                'm_group': 'traceroute',
                'queue_id': "traceroute.lurin_hfc_386",
            },
            "14": {
                "server_id": "stlmedlatf01",
                "server_name": "san_juan_ftth_383",
                'm_group': 'traceroute',
                'queue_id': "traceroute.san_juan_ftth_383",
            },
            "15": {
                "server_id": "stlmedlatf01",
                "server_name": "san_juan_hfc_388",
                'm_group': 'traceroute',
                'queue_id': "traceroute.san_juan_hfc_388",
            },
            "16": {
                "server_id": "stlmedlatf01",
                "server_name": "santa_luzmila_ftth_380",
                'm_group': 'traceroute',
                'queue_id': "traceroute.santa_luzmila_ftth_380",
            },
            "17": {
                "server_id": "stlmedlatf01",
                "server_name": "santa_luzmila_hfc_385",
                'm_group': 'traceroute',
                'queue_id': "traceroute.santa_luzmila_hfc_385",
            },
            "18": {
                "server_id": "stlmedlatf01",
                "server_name": "Huancayo_ftth_384",
                'm_group': 'traceroute',
                'queue_id': "traceroute.huancayo_ftth_384",
            },
        }

        config_ids = list(self.config_by_id.keys())
        for config_id in config_ids:
            group = self.config_by_id[config_id]['m_group']
            row = {**self.config_by_group[group], **self.config_by_id[config_id]}
            row['id'] = config_id
            row['name'] = row['server_name']
            row['work_dir'] = row['work_dir'].replace('{server_name}', row['server_name'])
            row['file_pattern'] = row['file_pattern'].replace('{server_name}', row['server_name'])
            self.config_by_id[config_id] = row
