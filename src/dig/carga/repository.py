from src.shared.carga.repository import InMemoryConfigRepository

class InMemoryDigCgnatConfigRepository(InMemoryConfigRepository):
    def __init__(self):
        self.config_by_group = {
            'dig_cgnat': {
                'work_dir': "/var/index/{server_name}/index2/estadisticas/Indicadores_Dig/mediciones/{str_date}",
                'wk_date_format': '%Y_%m_%d/%Y_%m_%d_%H',
                'wk_loop_time': '{"hours": 1}',
                'file_pattern': '^medicion_dig_{server_name}_([0-9]{14}).txt$',
                'file_date_format': '%Y%m%d%H%M%S',
                'file_delimiter': '|',
                'skip_lines': 1,
                'chunk_limit': 1000,
                'tablename': "dr_transporte_kpi.TX_MEDICION_DIG_{str_filemonth}",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': None,
                'exec_after_st': """BEGIN
                    PK_PADM_QUEUE.SP_DIG_FILE_SUCCESS('{queue_id}', '{str_file_date}', '{filename}', '{server_name_upper}');
                END;""",
                'files_permission': None,
                'search_time_ago': '{"hours": 24}',
                'loop_time': '{"minutes": 5}',
                'steps': None,
                'event_format': 'mxm',
                "msg_send_filename": True,
                "msg_send_granularity": True,
                'm_group': 'fping',
                'fields': [
                    # Fecha|IP_Address|Tipo_IP|Dominio|DNS_Server|querytime_1|querytime_2|querytime_3
                    # fecha─┬─ip_address─┬─tipo_ip─┬─dominio────────┬─dns─────────────┬─query_time_1─┬─query_time_2─┬─query_time_3─┬─servidor
                    {'fieldname': "fecha", 'src_fieldname': "Fecha", 'type': "date", 'to_reload': 1, 'reload_argument': '{file_date}'},
                    {'fieldname': "ip_address", 'src_fieldname': "IP_Address", 'type': "varchar2"},
                    {'fieldname': "tipo_ip", 'src_fieldname': "Tipo_IP", 'type': "varchar2"},
                    {'fieldname': "dominio", 'src_fieldname': "Dominio", 'type': "varchar2"},
                    {'fieldname': "dns", 'src_fieldname': "DNS_Server", 'type': "varchar2"},
                    {'fieldname': "query_time_1", 'src_fieldname': "querytime_1", 'type': "number"},
                    {'fieldname': "query_time_2", 'src_fieldname': "querytime_2", 'type': "number"},
                    {'fieldname': "query_time_3", 'src_fieldname': "querytime_3", 'type': "number"},
                    {'fieldname': "servidor", 'src_fieldname': "server_name_upper", 'type': "varchar2", 'to_reload': 1, 'reload_argument': '{server_name_upper}'},
                ]
            }
        }
        self.config_by_id = {
            # Arequipa
            "19": {
                "server_id": "arqmedlatf01",
                "server_name": "Apacheta_ftth_381",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.apacheta_ftth_381",
            },
            "20": {
                "server_id": "arqmedlatf01",
                "server_name": "Apacheta_hfc_396",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.apacheta_hfc_396",
            },
            "21": {
                "server_id": "arqmedlatf01",
                "server_name": "Arequipa7_ftth_382",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.arequipa7_ftth_382",
            },
            "22": {
                "server_id": "arqmedlatf01",
                "server_name": "Arequipa7_hfc_397",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.arequipa7_hfc_397",
            },
            "23": {
                "server_id": "arqmedlatf01",
                "server_name": "Arequipa_hfc_410",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.arequipa_hfc_410",
            },
            "24": {
                "server_id": "arqmedlatf01",
                "server_name": "Characato_ftth_384",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.characato_ftth_384",
            },
            "25": {
                "server_id": "arqmedlatf01",
                "server_name": "Characato_hfc_399",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.characato_hfc_399",
            },
            "26": {
                "server_id": "arqmedlatf01",
                "server_name": "CiudadMunicipal_ftth_383",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.ciudadmunicipal_ftth_383",
            },
            "27": {
                "server_id": "arqmedlatf01",
                "server_name": "CiudadMunicipal_hfc_398",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.ciudadmunicipal_hfc_398",
            },
            "28": {
                "server_id": "arqmedlatf01",
                "server_name": "PDIJuliaca_ftth_386",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.pdijuliaca_ftth_386",
            },
            "29": {
                "server_id": "arqmedlatf01",
                "server_name": "PDIJuliaca_hfc_401",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.pdijuliaca_hfc_401",
            },
            "30": {
                "server_id": "arqmedlatf01",
                "server_name": "Tiabaya2_ftth_385",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.tiabaya2_ftth_385",
            },
            "31": {
                "server_id": "arqmedlatf01",
                "server_name": "Tiabaya2_hfc_400",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.tiabaya2_hfc_400",
            },
            "42": {
                "server_id": "arqmedlatf01",
                "server_name": "AS-CUZ-SanJeronimo_ftth_392",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.as_cuz_sanjeronimo_ftth_392",
            },
            "43": {
                "server_id": "arqmedlatf01",
                "server_name": "AS-CUZ-SanJeronimo_hfc_407",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.as_cuz_sanjeronimo_hfc_407",
            },
            "44": {
                "server_id": "arqmedlatf01",
                "server_name": "ASG-PNO-CACPuno_ftth_389",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.asg_pno_cacpuno_ftth_389",
            },
            "45": {
                "server_id": "arqmedlatf01",
                "server_name": "ASG-PNO-CACPuno_hfc_404",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.asg_pno_cacpuno_hfc_404",
            },
            "46": {
                "server_id": "arqmedlatf01",
                "server_name": "rHUBCuzco_ftth_390",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.rhubcuzco_ftth_390",
            },
            "47": {
                "server_id": "arqmedlatf01",
                "server_name": "rHUBCuzco_hfc_405",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.rhubcuzco_hfc_405",
            },
            "48": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSCuzco6_ftth_391",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.rmplscuzco6_ftth_391",
            },
            "49": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSCuzco6_hfc_406",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.rmplscuzco6_hfc_406",
            },
            "50": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSJuliaca3_ftth_387",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.rmplsjuliaca3_ftth_387",
            },
            "51": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSJuliaca3_hfc_402",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.rmplsjuliaca3_hfc_402",
            },
            "52": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSJuliaca4_ftth_388",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.rmplsjuliaca4_ftth_388",
            },
            "53": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSJuliaca4_hfc_403",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.rmplsjuliaca4_hfc_403",
            },
            # piura
            "32": {
                "server_id": "stlmedlatf01",
                "server_name": "chiclayo_ftth_381",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Dig/mediciones/{str_date}",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.chiclayo_ftth_381",
            },
            "33": {
                "server_id": "stlmedlatf01",
                "server_name": "chiclayo_hfc_391",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Dig/mediciones/{str_date}",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.chiclayo_hfc_391",
            },
            "34": {
                "server_id": "stlmedlatf01",
                "server_name": "chimbote4_ftth_384",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Dig/mediciones/{str_date}",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.chimbote4_ftth_384",
            },
            "35": {
                "server_id": "stlmedlatf01",
                "server_name": "chimbote5_ftth_385",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Dig/mediciones/{str_date}",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.chimbote5_ftth_385",
            },
            "36": {
                "server_id": "stlmedlatf01",
                "server_name": "chimbote5_hfc_395",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Dig/mediciones/{str_date}",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.chimbote5_hfc_395",
            },
            "37": {
                "server_id": "stlmedlatf01",
                "server_name": "pacasmayo_ftth_383",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Dig/mediciones/{str_date}",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.pacasmayo_ftth_383",
            },
            "38": {
                "server_id": "stlmedlatf01",
                "server_name": "pacasmayo_hfc_393",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Dig/mediciones/{str_date}",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.pacasmayo_hfc_393",
            },
            "39": {
                "server_id": "stlmedlatf01",
                "server_name": "piura_hfc_390",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Dig/mediciones/{str_date}",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.piura_hfc_390",
            },
            "40": {
                "server_id": "stlmedlatf01",
                "server_name": "trujillo_ftth_382",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Dig/mediciones/{str_date}",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.trujillo_ftth_382",
            },
            "41": {
                "server_id": "stlmedlatf01",
                "server_name": "trujillo_hfc_392",
                'work_dir': "/var/index/piura_cgnat/{server_name}/index2/estadisticas/Indicadores_Dig/mediciones/{str_date}",
                'm_group': 'dig_cgnat',
                'queue_id': "dig.trujillo_hfc_392",
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
            row['exec_after_st'] = row['exec_after_st'].replace('{queue_id}', row['queue_id'])
            self.config_by_id[config_id] = row
