from src.shared.carga.repository import InMemoryConfigRepository

class InMemoryMmltaskConfigRepository(InMemoryConfigRepository):
    def __init__(self):
        self.config_by_id = {
            "8": {
                "server_id": "xmlhuawei2_01",
                "server_ip": "10.96.210.9",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/105922/history",
                'm_group': 'voltaje',
                'queue_id': "mmltask_01.voltage",
                'status': 1
            },
            "1": {
                "server_id": "xmlhuawei2_02",
                "server_ip": "10.96.210.10",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/105922/history",
                'm_group': 'voltaje',
                'queue_id': "mmltask_02.voltage",
                'status': 1
            },
            "2": {
                "server_id": "xmlhuawei2_03",
                "server_ip": "10.96.210.11",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/105922/history",
                'm_group': 'voltaje',
                'queue_id': "mmltask_03.voltage",
                'status': 1
            },
            "3": {
                "server_id": "xmlhuawei2_04",
                "server_ip": "10.96.210.12",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/105922/history",
                'm_group': 'voltaje',
                'queue_id': "mmltask_04.voltage",
                'status': 1
            },
            "4": {
                "server_id": "xmlhuawei2_05",
                "server_ip": "10.96.210.14",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/105922/history",
                'm_group': 'voltaje',
                'queue_id': "mmltask_05.voltage",
                'status': 1
            },
            "5": {
                "server_id": "xmlhuawei2_06",
                "server_ip": "10.96.210.15",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/105922/history",
                'm_group': 'voltaje',
                'queue_id': "mmltask_06.voltage",
                'status': 1
            },
            "6": {
                "server_id": "xmlhuawei2_07",
                "server_ip": "10.96.210.16",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/105922/history",
                'm_group': 'voltaje',
                'queue_id': "mmltask_07.voltage",
                'status': 1
            },
            "7": {
                "server_id": "xmlhuawei2_08",
                "server_ip": "10.96.210.17",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/105922/history",
                'm_group': 'voltaje',
                'queue_id': "mmltask_08.voltage",
                'status': 1
            },
            
            "9": {
                "server_id": "xmlhuawei2_09",
                "server_ip": "10.96.210.137",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/74387/history",
                'm_group': 'voltaje',
                'queue_id': "mmltask_09.voltage",
                'status': 1
            },
            "10": {
                "server_id": "xmlhuawei2_10",
                "server_ip": "10.96.210.138",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/74387/history",
                'm_group': 'voltaje',
                'queue_id': "mmltask_10.voltage",
                'status': 1
            },
            "11": {
                "server_id": "xmlhuawei2_11",
                "server_ip": "10.96.210.139",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/74387/history",
                'm_group': 'voltaje',
                'queue_id': "mmltask_11.voltage",
                'status': 1
            },
            "12": {
                "server_id": "xmlhuawei2_12",
                "server_ip": "10.96.210.140",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/74387/history",
                'm_group': 'voltaje',
                'queue_id': "mmltask_12.voltage",
                'status': 1
            },
            "13": {
                "server_id": "xmlhuawei2_14",
                "server_ip": "10.96.210.142",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/74387/history",
                'm_group': 'voltaje',
                'queue_id': "mmltask_14.voltage",
                'status': 1
            },
            "14": {
                "server_id": "xmlhuawei2_15",
                "server_ip": "10.96.210.143",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/74387/history",
                'm_group': 'voltaje',
                'queue_id': "mmltask_15.voltage",
                'status': 1
            },
            "15": {
                "server_id": "xmlhuawei2_16",
                "server_ip": "10.96.210.144",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/74387/history",
                'm_group': 'voltaje',
                'queue_id': "mmltask_16.voltage",
                'status': 1
            },
            "16": {
                "server_id": "xmlhuawei2_17",
                "server_ip": "10.96.210.145",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/74387/history",
                'm_group': 'voltaje',
                'queue_id': "mmltask_17.voltage",
                'status': 1
            },
            
            # temperatura

            "17": {
                "server_id": "xmlhuawei2_01",
                "server_ip": "10.96.210.9",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/105924/history",
                'm_group': 'temperatura',
                'queue_id': "mmltask_01.temperatura",
                'status': 1
            },
            "18": {
                "server_id": "xmlhuawei2_02",
                "server_ip": "10.96.210.10",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/105924/history",
                'm_group': 'temperatura',
                'queue_id': "mmltask_02.temperatura",
                'status': 1
            },
            "19": {
                "server_id": "xmlhuawei2_03",
                "server_ip": "10.96.210.11",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/105924/history",
                'm_group': 'temperatura',
                'queue_id': "mmltask_03.temperatura",
                'status': 1
            },
            "20": {
                "server_id": "xmlhuawei2_04",
                "server_ip": "10.96.210.12",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/105924/history",
                'm_group': 'temperatura',
                'queue_id': "mmltask_04.temperatura",
                'status': 1
            },
            "21": {
                "server_id": "xmlhuawei2_05",
                "server_ip": "10.96.210.14",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/105924/history",
                'm_group': 'temperatura',
                'queue_id': "mmltask_05.temperatura",
                'status': 1
            },
            "22": {
                "server_id": "xmlhuawei2_06",
                "server_ip": "10.96.210.15",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/105924/history",
                'm_group': 'temperatura',
                'queue_id': "mmltask_06.temperatura",
                'status': 1
            },
            "23": {
                "server_id": "xmlhuawei2_07",
                "server_ip": "10.96.210.16",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/105924/history",
                'm_group': 'temperatura',
                'queue_id': "mmltask_07.temperatura",
                'status': 1
            },
            "24": {
                "server_id": "xmlhuawei2_08",
                "server_ip": "10.96.210.17",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/105924/history",
                'm_group': 'temperatura',
                'queue_id': "mmltask_08.temperatura",
                'status': 1
            },
            
            "25": {
                "server_id": "xmlhuawei2_09",
                "server_ip": "10.96.210.137",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/74394/history",
                'm_group': 'temperatura',
                'queue_id': "mmltask_09.temperatura",
                'status': 1
            },
            "26": {
                "server_id": "xmlhuawei2_10",
                "server_ip": "10.96.210.138",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/74394/history",
                'm_group': 'temperatura',
                'queue_id': "mmltask_10.temperatura",
                'status': 1
            },
            "27": {
                "server_id": "xmlhuawei2_11",
                "server_ip": "10.96.210.139",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/74394/history",
                'm_group': 'temperatura',
                'queue_id': "mmltask_11.temperatura",
                'status': 1
            },
            "28": {
                "server_id": "xmlhuawei2_12",
                "server_ip": "10.96.210.140",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/74394/history",
                'm_group': 'temperatura',
                'queue_id': "mmltask_12.temperatura",
                'status': 1
            },
            "29": {
                "server_id": "xmlhuawei2_14",
                "server_ip": "10.96.210.142",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/74394/history",
                'm_group': 'temperatura',
                'queue_id': "mmltask_14.temperatura",
                'status': 1
            },
            "30": {
                "server_id": "xmlhuawei2_15",
                "server_ip": "10.96.210.143",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/74394/history",
                'm_group': 'temperatura',
                'queue_id': "mmltask_15.temperatura",
                'status': 1
            },
            "31": {
                "server_id": "xmlhuawei2_16",
                "server_ip": "10.96.210.144",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/74394/history",
                'm_group': 'temperatura',
                'queue_id': "mmltask_16.temperatura",
                'status': 1
            },
            "32": {
                "server_id": "xmlhuawei2_17",
                "server_ip": "10.96.210.145",
                "work_dir": "/export/home/sysm/ftproot/MMLTaskResult/74394/history",
                'm_group': 'temperatura',
                'queue_id': "mmltask_17.temperatura",
                'status': 1
            },
        }
        self.config_by_group = {
            "voltaje": {
                # 'id': '1',
                'name': 'mmltask_voltaje',
                'type': 'stats',
                'server_id': None,
                'work_dir': "/export/home/sysm/ftproot/MMLTaskResult/105922/history",
                'file_pattern': 'MMLTask_VALORES VOLTAJE_([0-9]{8}_[0-9]{6}).tar.gz',
                'file_date_format': '%Y%m%d_%H%M%S',
                'chunk_limit': 5000,
                'tablename': "MMLTASK_INDI_VOLTAGE",
                'queue_id': "mmltask.voltage",
                'status': 1,
                'exec_after_by': None,
                'exec_after_st': None,
                # 'files_permission': "group",
                'search_time_ago': '{"days": 2}',
                'loop_time': '{"day": 1}',
                'steps': None,
                'event_format': 'mxm',
                "msg_send_filename": True,
                'm_group': 'voltaje',
            },
            "temperatura": {
                'name': 'mmltask_temperatura',
                'type': 'stats',
                'server_id': None,
                'work_dir': "/export/home/sysm/ftproot/MMLTaskResult/105922/history",
                'file_pattern': 'MMLTask_VALORES TEMPERATURA_([0-9]{8}_[0-9]{6}).tar.gz',
                'file_date_format': '%Y%m%d_%H%M%S',
                'chunk_limit': 5000,
                'tablename': "MMLTASK_INDI_TEMPERATURE",
                'queue_id': "mmltask.temperatura",
                'status': 1,
                'exec_after_by': None,
                'exec_after_st': None,
                # 'files_permission': "group",
                'search_time_ago': '{"days": 2}',
                'loop_time': '{"day": 1}',
                'steps': None,
                'event_format': 'mxm',
                "msg_send_filename": True,
                'm_group': 'temperatura',
            }
        }
        self.fields_by_group = {
            "voltaje": [
                {'fieldname': "result_time", 'src_fieldname': "result_time", 'type': "date"},
                {'fieldname': "ne_name", 'src_fieldname': "ne_name", 'type': "varchar2"},
                {'fieldname': "cabinet_no", 'src_fieldname': "cabinet_no", 'type': "number"},
                {'fieldname': "subrack_no", 'src_fieldname': "subrack_no", 'type': "number"},
                {'fieldname': "slot_no", 'src_fieldname': "slot_no", 'type': "number"},
                {'fieldname': "upeu_spare_power", 'src_fieldname': "upeu_spare_power", 'type': "number"},
                {'fieldname': "bbu_spare_power", 'src_fieldname': "bbu_spare_power", 'type': "number"},
                {'fieldname': "input_voltage", 'src_fieldname': "input_voltage", 'type': "number"},
                {'fieldname': "fecha", 'src_fieldname': "fecha", 'type': "date"},
                {'fieldname': "archivo", 'src_fieldname': "archivo", 'type': "varchar2", 'reload_argument': '{filename}', 'to_reload': 1},
                {'fieldname': "servidor", 'src_fieldname': "servidor", 'type': "varchar2", 'reload_argument': '{servidor}', 'to_reload': 1},
            ],
            "temperatura": [
                {'fieldname': "result_time", 'src_fieldname': "result_time", 'type': "date"},
                {'fieldname': "ne_name", 'src_fieldname': "ne_name", 'type': "varchar2"},
                {'fieldname': "cabinet_no", 'src_fieldname': "cabinet_no", 'type': "number"},
                {'fieldname': "subrack_no", 'src_fieldname': "subrack_no", 'type': "number"},
                {'fieldname': "slot_no", 'src_fieldname': "slot_no", 'type': "number"},
                {'fieldname': "board_temperature", 'src_fieldname': "board_temperature", 'type': "number"},
                {'fieldname': "hpa_temperature", 'src_fieldname': "hpa_temperature", 'type': "number"},
                {'fieldname': "fecha", 'src_fieldname': "fecha", 'type': "date"},
                {'fieldname': "archivo", 'src_fieldname': "archivo", 'type': "varchar2", 'reload_argument': '{filename}', 'to_reload': 1},
                {'fieldname': "servidor", 'src_fieldname': "servidor", 'type': "varchar2", 'reload_argument': '{servidor}', 'to_reload': 1},
            ]
        }

    def get(self):
        result = []
        for id in list(self.config_by_id):
            row = dict(**self.config_by_id[id])
            row['id'] = id
            if row.get("status") is not None:
                if row["status"] != 1:
                    continue
            # row.pop("fields")
            result.append(row)
        return list(map(lambda row: self.find(row['id']), result))

    def find(self, id):
        if id in self.config_by_id.keys():
            config = self.config_by_id[id]
            row = dict(**self.config_by_group[config['m_group']])
            row['id'] = id
            row['name'] = config['queue_id'].replace('.', '_')
            row['server_id'] = config['server_id']
            row['work_dir'] = config['work_dir']
            row['queue_id'] = config['queue_id']
            # print(row)
            return row
        return None

    def get_fields_by_id(self, config_id):
        if config_id in self.config_by_id.keys():
            fields = self.fields_by_group[self.config_by_id[config_id]['m_group']]
            fields[len(fields)-1]['reload_argument'] = self.config_by_id[config_id]['server_ip']
            return fields
        return []