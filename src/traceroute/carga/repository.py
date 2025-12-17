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
                    {'fieldname': "fecha_programada", 'src_fieldname': "fecha_programada", 'type': "date"},
                    {'fieldname': "ip", 'src_fieldname': "ip", 'type': "varchar2"},
                    {'fieldname': "ip_add_resuelta", 'src_fieldname': "ip_add_resuelta", 'type': "varchar2"},
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
            # Arequipa
            "19": {
                "server_id": "arqmedlatf01",
                "server_name": "Apacheta_ftth_381",
                'm_group': 'traceroute',
                'queue_id': "traceroute.apacheta_ftth_381",
            },
            "20": {
                "server_id": "arqmedlatf01",
                "server_name": "Apacheta_hfc_396",
                'm_group': 'traceroute',
                'queue_id': "traceroute.apacheta_hfc_396",
            },
            "21": {
                "server_id": "arqmedlatf01",
                "server_name": "Arequipa7_ftth_382",
                'm_group': 'traceroute',
                'queue_id': "traceroute.arequipa7_ftth_382",
            },
            "22": {
                "server_id": "arqmedlatf01",
                "server_name": "Arequipa7_hfc_397",
                'm_group': 'traceroute',
                'queue_id': "traceroute.arequipa7_hfc_397",
            },
            "23": {
                "server_id": "arqmedlatf01",
                "server_name": "Arequipa_hfc_410",
                'm_group': 'traceroute',
                'queue_id': "traceroute.arequipa_hfc_410",
            },
            "24": {
                "server_id": "arqmedlatf01",
                "server_name": "Characato_ftth_384",
                'm_group': 'traceroute',
                'queue_id': "traceroute.characato_ftth_384",
            },
            "25": {
                "server_id": "arqmedlatf01",
                "server_name": "Characato_hfc_399",
                'm_group': 'traceroute',
                'queue_id': "traceroute.characato_hfc_399",
            },
            "26": {
                "server_id": "arqmedlatf01",
                "server_name": "CiudadMunicipal_ftth_383",
                'm_group': 'traceroute',
                'queue_id': "traceroute.ciudadmunicipal_ftth_383",
            },
            "27": {
                "server_id": "arqmedlatf01",
                "server_name": "CiudadMunicipal_hfc_398",
                'm_group': 'traceroute',
                'queue_id': "traceroute.ciudadmunicipal_hfc_398",
            },
            "28": {
                "server_id": "arqmedlatf01",
                "server_name": "PDIJuliaca_ftth_386",
                'm_group': 'traceroute',
                'queue_id': "traceroute.pdijuliaca_ftth_386",
            },
            "29": {
                "server_id": "arqmedlatf01",
                "server_name": "PDIJuliaca_hfc_401",
                'm_group': 'traceroute',
                'queue_id': "traceroute.pdijuliaca_hfc_401",
            },
            "30": {
                "server_id": "arqmedlatf01",
                "server_name": "Tiabaya2_ftth_385",
                'm_group': 'traceroute',
                'queue_id': "traceroute.tiabaya2_ftth_385",
            },
            "31": {
                "server_id": "arqmedlatf01",
                "server_name": "Tiabaya2_hfc_400",
                'm_group': 'traceroute',
                'queue_id': "traceroute.tiabaya2_hfc_400",
            },
            "42": {
                "server_id": "arqmedlatf01",
                "server_name": "AS-CUZ-SanJeronimo_ftth_392",
                'm_group': 'traceroute',
                'queue_id': "traceroute.as_cuz_sanjeronimo_ftth_392",
            },
            "43": {
                "server_id": "arqmedlatf01",
                "server_name": "AS-CUZ-SanJeronimo_hfc_407",
                'm_group': 'traceroute',
                'queue_id': "traceroute.as_cuz_sanjeronimo_hfc_407",
            },
            "44": {
                "server_id": "arqmedlatf01",
                "server_name": "ASG-PNO-CACPuno_ftth_389",
                'm_group': 'traceroute',
                'queue_id': "traceroute.asg_pno_cacpuno_ftth_389",
            },
            "45": {
                "server_id": "arqmedlatf01",
                "server_name": "ASG-PNO-CACPuno_hfc_404",
                'm_group': 'traceroute',
                'queue_id': "traceroute.asg_pno_cacpuno_hfc_404",
            },
            "46": {
                "server_id": "arqmedlatf01",
                "server_name": "rHUBCuzco_ftth_390",
                'm_group': 'traceroute',
                'queue_id': "traceroute.rhubcuzco_ftth_390",
            },
            "47": {
                "server_id": "arqmedlatf01",
                "server_name": "rHUBCuzco_hfc_405",
                'm_group': 'traceroute',
                'queue_id': "traceroute.rhubcuzco_hfc_405",
            },
            "48": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSCuzco6_ftth_391",
                'm_group': 'traceroute',
                'queue_id': "traceroute.rmplscuzco6_ftth_391",
            },
            "49": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSCuzco6_hfc_406",
                'm_group': 'traceroute',
                'queue_id': "traceroute.rmplscuzco6_hfc_406",
            },
            "50": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSJuliaca3_ftth_387",
                'm_group': 'traceroute',
                'queue_id': "traceroute.rmplsjuliaca3_ftth_387",
            },
            "51": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSJuliaca3_hfc_402",
                'm_group': 'traceroute',
                'queue_id': "traceroute.rmplsjuliaca3_hfc_402",
            },
            "52": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSJuliaca4_ftth_388",
                'm_group': 'traceroute',
                'queue_id': "traceroute.rmplsjuliaca4_ftth_388",
            },
            "53": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSJuliaca4_hfc_403",
                'm_group': 'traceroute',
                'queue_id': "traceroute.rmplsjuliaca4_hfc_403",
            },
            # piura
            "32": {
                "server_id": "stlmedlatf01",
                "server_name": "chiclayo_ftth_381",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Traceroute/{str_date}",
                'm_group': 'traceroute',
                'queue_id': "traceroute.chiclayo_ftth_381",
            },
            "33": {
                "server_id": "stlmedlatf01",
                "server_name": "chiclayo_hfc_391",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Traceroute/{str_date}",
                'm_group': 'traceroute',
                'queue_id': "traceroute.chiclayo_hfc_391",
            },
            "34": {
                "server_id": "stlmedlatf01",
                "server_name": "chimbote4_ftth_384",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Traceroute/{str_date}",
                'm_group': 'traceroute',
                'queue_id': "traceroute.chimbote4_ftth_384",
            },
            "35": {
                "server_id": "stlmedlatf01",
                "server_name": "chimbote5_ftth_385",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Traceroute/{str_date}",
                'm_group': 'traceroute',
                'queue_id': "traceroute.chimbote5_ftth_385",
            },
            "36": {
                "server_id": "stlmedlatf01",
                "server_name": "chimbote5_hfc_395",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Traceroute/{str_date}",
                'm_group': 'traceroute',
                'queue_id': "traceroute.chimbote5_hfc_395",
            },
            "37": {
                "server_id": "stlmedlatf01",
                "server_name": "pacasmayo_ftth_383",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Traceroute/{str_date}",
                'm_group': 'traceroute',
                'queue_id': "traceroute.pacasmayo_ftth_383",
            },
            "38": {
                "server_id": "stlmedlatf01",
                "server_name": "pacasmayo_hfc_393",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Traceroute/{str_date}",
                'm_group': 'traceroute',
                'queue_id': "traceroute.pacasmayo_hfc_393",
            },
            "39": {
                "server_id": "stlmedlatf01",
                "server_name": "piura_hfc_390",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Traceroute/{str_date}",
                'm_group': 'traceroute',
                'queue_id': "traceroute.piura_hfc_390",
            },
            "40": {
                "server_id": "stlmedlatf01",
                "server_name": "trujillo_ftth_382",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Traceroute/{str_date}",
                'm_group': 'traceroute',
                'queue_id': "traceroute.trujillo_ftth_382",
            },
            "41": {
                "server_id": "stlmedlatf01",
                "server_name": "trujillo_hfc_392",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Traceroute/{str_date}",
                'm_group': 'traceroute',
                'queue_id': "traceroute.trujillo_hfc_392",
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
