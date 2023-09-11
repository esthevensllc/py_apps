from src.shared.carga.repository import InMemoryConfigRepository
import json

class InMemoryArborConfigRepository(InMemoryConfigRepository):
    def __init__(self, db):
        self.db = db
        self.config_by_id = {
            "1": {
                'id': '1',
                'name': 'arbor_customer_int_traffic',
                'type': 'stats',
                # 'server_id': 'pronatel03',
                'work_dir': '/api/sp/traffic_queries/',
                'request_type': "POST",
                'request_body': json.dumps({
                    "data": {
                        "attributes": {
                            "filters": [
                                {"facet": "Customer", "values": [], "groupby": True},
                                {"facet": "Interface", "values": [], "groupby": True}
                            ],
                            "limit": 999999999,
                            "query_start_time": "[datetime_ini_utc]",
                            "query_end_time": "[datetime_fin_utc]",
                            "unit": "bps"
                        }
                    }
                }),
                'result_type': "traffic_queries",
                'file_pattern': 'arbor_customer_int_traffic_([0-9]{12}).json',
                'file_date_format': '%Y%m%d%H%M',
                'limit_to_commit': 10000,
                'tablename': "arbor_customer_interface_traffic",
                'queue_id': "arbor.customer_int_traffic",
                'status': 1,
                'reload_by': "all",
                'exec_after_by': None,
                'exec_after_st': None,
                'search_time_ago': '{"days": 30}',
                'loop_time': '{"hours": 1}',
                'steps': None,
                'event_format': 'hxh',
                'm_group': '1',
                "fields": [
                    {'fieldname': "collectiontime", 'src_fieldname': "timeserie", 'type': "date", 'to_reload': 1},
                    {'fieldname': "customer", 'src_fieldname': "customer", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "customer_id", 'src_fieldname': "facet_customer", 'type': "varchar2", 'map_with': "{value['id']}", 'to_reload': None},
                    {'fieldname': "interface", 'src_fieldname': "interface", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "interface_id", 'src_fieldname': "facet_interface", 'type': "varchar2", 'map_with': "{value['id']}", 'to_reload': None},
                    {'fieldname': "description", 'src_fieldname': "facet_interface", 'type': "varchar2", 'map_with': "{value['description']}", 'to_reload': None},
                    {'fieldname': "router", 'src_fieldname': "facet_interface", 'type': "varchar2", 'map_with': "{value['router']}", 'to_reload': None},
                    {'fieldname': "snmp_speed", 'src_fieldname': "facet_interface", 'type': "varchar2", 'map_with': "{value['snmp_speed']}", 'to_reload': None},
                    {'fieldname': "snmp_index", 'src_fieldname': "facet_interface", 'type': "varchar2", 'map_with': "{value['snmp_index']}", 'to_reload': None},
                    {'fieldname': "granularidad", 'src_fieldname': "step", 'type': "number", 'to_reload': None},
                    {'fieldname': "in_bps", 'src_fieldname': "in_bps", 'type': "number", 'to_reload': None},
                    {'fieldname': "out_bps", 'src_fieldname': "out_bps", 'type': "number", 'to_reload': None},
                ]
            }
        }