from src.shared.carga.repository import InMemoryConfigRepository

class InMemoryFpingCgnatConfigRepository(InMemoryConfigRepository):
    def __init__(self):
        self.config_by_group = {
            'fping_cgnat_arequipa': {
                'work_dir': "/var/index/{server_name}/index2/estadisticas/Indicadores_Fping/mediciones/{str_date}",
                'wk_date_format': '%Y_%m_%d/%Y_%m_%d_%H',
                'wk_loop_time': '{"hours": 1}',
                'file_pattern': '^mediciones_fping_{server_name}_([0-9]{14}).csv$',
                'file_date_format': '%Y%m%d%H%M%S',
                'file_delimiter': ',',
                'skip_lines': 0,
                'chunk_limit': 1000,
                'tablename': "dr_transporte_kpi.tx_fping_cgnat_fuente_{str_filedate}",
                # 'tablename': "default.tx_fping_cgnat_fuente_test_{str_filedate}",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': None,
                'exec_after_st': """BEGIN
                    insert into SEG_CARGA_FPING(fecha,flujo,tipo_carga,fecha_insercion,archivo,estado)
                    values(substr('{str_file_date}', 1, 12),upper('RESUMEN_FPING_MI_CGNAT_{server_name}'), 'C', sysdate, '{filename}', 0);
                    commit;
                    PK_PADM_QUEUE.SP_FPING_RESUMEN_PRODUCER;
                END;""",
                'files_permission': None,
                'search_time_ago': '{"hours": 24}',
                'loop_time': '{"minutes": 1}',
                'steps': None,
                'event_format': 'mxm',
                "msg_send_filename": True,
                "msg_send_granularity": True,
                'm_group': 'fping',
                'fields': [
                    {'fieldname': "result_time", 'src_fieldname': "0", 'type': "date"},
                    {'fieldname': "ip_add", 'src_fieldname': "1", 'type': "varchar2"},
                    {'fieldname': "xmt", 'src_fieldname': "2", 'type': "number"},
                    {'fieldname': "rcv", 'src_fieldname': "3", 'type': "number"},
                    {'fieldname': "porc_loss", 'src_fieldname': "4", 'type': "number"},
                    {'fieldname': "lat_min", 'src_fieldname': "5", 'type': "number"},
                    {'fieldname': "lat_avg", 'src_fieldname': "6", 'type': "number"},
                    {'fieldname': "lat_max", 'src_fieldname': "7", 'type': "number"},
                    {'fieldname': "servidor", 'src_fieldname': "8", 'type': "varchar2", 'to_reload': 1, 'reload_argument': '{server_name}'},
                    {'fieldname': "archivo", 'src_fieldname': "9", 'type': "varchar2", 'to_reload': 1, 'reload_argument': '{filename}'},
                    {'fieldname': "ip_add_resuelta", 'src_fieldname': "10", 'type': "varchar2"},
                ]
            }
        }
        self.config_by_id = {
            "1": {
                "server_id": "arqmedlatf01",
                "server_name": "Apacheta_ftth_381",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.apacheta_ftth_381",
            },
            "2": {
                "server_id": "arqmedlatf01",
                "server_name": "Apacheta_hfc_396",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.apacheta_hfc_396",
            },
            "3": {
                "server_id": "arqmedlatf01",
                "server_name": "Arequipa7_ftth_382",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.arequipa7_ftth_382",
            },
            "4": {
                "server_id": "arqmedlatf01",
                "server_name": "Arequipa7_hfc_397",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.arequipa7_hfc_397",
            },
            "5": {
                "server_id": "arqmedlatf01",
                "server_name": "Arequipa_hfc_410",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.arequipa_hfc_410",
            },
            "6": {
                "server_id": "arqmedlatf01",
                "server_name": "Characato_ftth_384",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.characato_ftth_384",
            },
            "7": {
                "server_id": "arqmedlatf01",
                "server_name": "Characato_hfc_399",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.characato_hfc_399",
            },
            "8": {
                "server_id": "arqmedlatf01",
                "server_name": "CiudadMunicipal_ftth_383",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.ciudadmunicipal_ftth_383",
            },
            "9": {
                "server_id": "arqmedlatf01",
                "server_name": "CiudadMunicipal_hfc_398",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.ciudadmunicipal_hfc_398",
            },
            "10": {
                "server_id": "arqmedlatf01",
                "server_name": "PDIJuliaca_ftth_386",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.pdijuliaca_ftth_386",
            },
            "11": {
                "server_id": "arqmedlatf01",
                "server_name": "PDIJuliaca_hfc_401",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.pdijuliaca_hfc_401",
            },
            "12": {
                "server_id": "arqmedlatf01",
                "server_name": "Tiabaya2_ftth_385",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.tiabaya2_ftth_385",
            },
            "13": {
                "server_id": "arqmedlatf01",
                "server_name": "Tiabaya2_hfc_400",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.tiabaya2_hfc_400",
            },
            "14": {
                "server_id": "arqmedlatf01",
                "server_name": "AS-CUZ-SanJeronimo_ftth_392",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.as_cuz_sanjeronimo_ftth_392",
            },
            "15": {
                "server_id": "arqmedlatf01",
                "server_name": "AS-CUZ-SanJeronimo_hfc_407",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.as_cuz_sanjeronimo_hfc_407",
            },
            "16": {
                "server_id": "arqmedlatf01",
                "server_name": "ASG-PNO-CACPuno_ftth_389",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.asg_pno_cacpuno_ftth_389",
            },
            "17": {
                "server_id": "arqmedlatf01",
                "server_name": "ASG-PNO-CACPuno_hfc_404",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.asg_pno_cacpuno_hfc_404",
            },
            "18": {
                "server_id": "arqmedlatf01",
                "server_name": "rHUBCuzco_ftth_390",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.rhubcuzco_ftth_390",
            },
            "19": {
                "server_id": "arqmedlatf01",
                "server_name": "rHUBCuzco_hfc_405",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.rhubcuzco_hfc_405",
            },
            "20": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSCuzco6_ftth_391",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.rmplscuzco6_ftth_391",
            },
            "21": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSCuzco6_hfc_406",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.rmplscuzco6_hfc_406",
            },
            "22": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSJuliaca3_ftth_387",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.rmplsjuliaca3_ftth_387",
            },
            "23": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSJuliaca3_hfc_402",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.rmplsjuliaca3_hfc_402",
            },
            "24": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSJuliaca4_ftth_388",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.rmplsjuliaca4_ftth_388",
            },
            "25": {
                "server_id": "arqmedlatf01",
                "server_name": "rMPLSJuliaca4_hfc_403",
                'm_group': 'fping_cgnat_arequipa',
                'queue_id': "fping_cgnat.rmplsjuliaca4_hfc_403",
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
