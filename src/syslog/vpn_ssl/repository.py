from src.shared.carga.repository import InMemoryConfigRepository

class InMemoryVpnSslConfigRepository(InMemoryConfigRepository):
    def __init__(self, db):
        self.db = db
        self.config_by_id = {
            "1": {
                'id': '1',
                'name': 'vpn_ssl',
                # 'type': 'stats',
                # 'work_dir': 'extracts/dsar_reports/',
                # 'file_pattern': 'dsar_report_(.{10}).zip',
                # 'file_date_format': '%Y-%m-%d',
                # 'limit_to_commit': 10000,
                'tablename': "vpn.vpn_ssl_log_{str_date}",
                'table_type': "interval_table",
                'table_date_format': "%Y%m%d",
                'delete_data_older_than': '{"days": 15}',
                'table_create_template': """CREATE TABLE IF NOT EXISTS vpn.vpn_ssl_log_{str_date}
                (
                    result_time DateTime DEFAULT '0000-00-00 00:00:00',
                    priority Int32 CODEC(T64, LZ4),
                    ip Nullable(String) DEFAULT NULL CODEC(LZ4),
                    level Nullable(String) DEFAULT NULL CODEC(LZ4),
                    process Nullable(String) DEFAULT NULL CODEC(LZ4),
                    pid Nullable(String) DEFAULT NULL CODEC(LZ4),
                    protocol Nullable(String) DEFAULT NULL CODEC(LZ4),
                    origin_ip Nullable(String) DEFAULT NULL CODEC(LZ4),
                    origin_port Nullable(Int32) DEFAULT NULL CODEC(T64, LZ4),
                    destination_ip Nullable(String) DEFAULT NULL CODEC(LZ4),
                    destination_port Nullable(Int32) DEFAULT NULL CODEC(T64, LZ4),
                    message Nullable(String) DEFAULT NULL CODEC(LZ4)
                )
                ENGINE = MergeTree
                PRIMARY KEY (result_time)
                ORDER BY (result_time)
                SETTINGS index_granularity = 8192""",
                # 'queue_id': "speedtest.dsar_report",
                'status': 1,
                # 'reload_by': "file",
                # 'exec_after_by': None,
                # 'exec_after_st': None,
                # 'search_time_ago': '{"days": 1}',
                # 'loop_time': '{"days": 1}',
                # 'steps': "unzip",
                # 'event_format': 'dxd',
                'm_group': 'vpn_ssl',
                'fields': []
            },
            "2": {
                'id': '2',
                'name': 'vpn_ivanty',
                'tablename': "vpn.vpn_ivanty_log_{str_date}",
                'table_type': "interval_table",
                'table_date_format': "%Y%m%d",
                'delete_data_older_than': '{"days": 15}',
                'table_create_template': """CREATE TABLE IF NOT EXISTS vpn.vpn_ivanty_log_{str_date}
                (
                    `result_time` DateTime DEFAULT '0000-00-00 00:00:00',
                    `code` Int32 CODEC(T64, LZ4),
                    `priority` Int32 CODEC(T64, LZ4),
                    `code2` Int32 CODEC(T64, LZ4),
                    `from` Nullable(String) DEFAULT NULL CODEC(LZ4),
                    `process` Nullable(String) DEFAULT NULL CODEC(LZ4),
                    `date` Nullable(DateTime) DEFAULT NULL,
                    `nodo` Nullable(String) DEFAULT NULL CODEC(LZ4),
                    `ip` Nullable(String) DEFAULT NULL CODEC(LZ4),
                    `message` Nullable(String) DEFAULT NULL CODEC(LZ4)
                )
                ENGINE = MergeTree
                PRIMARY KEY result_time
                ORDER BY result_time
                SETTINGS index_granularity = 8192;""",
                'status': 1,
                'm_group': 'vpn_ivanty',
                'fields': []
            }
        }