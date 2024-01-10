from src.shared.carga.repository import InMemoryConfigRepository

class InMemoryNFAConfigRepository(InMemoryConfigRepository):
    def __init__(self, db):
        self.db = db
        self.config_by_id = {
            "1": {
                'id': '1',
                'name': 'tx_nfa_netflow_rmpls',
                'type': 'stats',
                'server_id': None,
                'work_dir': "",
                'api_query': "odata/api/interfaces?$select=RouterName,RouterId,Name,ID&$filter=((contains(RouterName, 'rmpls')) and (contains(Enabled, 'Enabled')))&$format=json",
                'sub_api_query': "odata/api/interfaces({id})/conversations?&$top=20&$format=json",
                'file_pattern': 'tx_nfa_netflow_rmpls_([0-9]{12}).json',
                'file_date_format': '%Y%m%d%H%M',
                'chunk_limit': 5000,
                'limit_to_commit': 5000,
                'skip_lines': 0,
                'tablename': "tx_nfa_netflow_rmpls",
                'queue_id': "nfa.netflow_rmpls",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': None,
                'exec_after_st': None,
                # 'files_permission': "group",
                'search_time_ago': '{"days": 1}',
                'loop_time': '{"minutes": 15}',
                'steps': None,
                'event_format': 'hxh',
                'm_group': 'stats',
                'fields': [
                    {'fieldname': "protocol", 'src_fieldname': "protocol", 'type': "number", 'to_reload': None},
                    {'fieldname': "inoctets", 'src_fieldname': "inoctets", 'type': "number", 'to_reload': None},
                    {'fieldname': "outoctets", 'src_fieldname': "outoctets", 'type': "number", 'to_reload': None},
                    {'fieldname': "SrcHost", 'src_fieldname': "SrcHost", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "interface", 'src_fieldname': "interface", 'type': "number", 'to_reload': None},
                    {'fieldname': "DestHost", 'src_fieldname': "DestHost", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "router", 'src_fieldname': "router", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "result_time", 'src_fieldname': "timestamp", 'type': "date", 'map_with': "{dt.datetime.fromtimestamp(int(value)).strftime('%Y-%m-%d %H:%M:%S')}", 'to_reload': 1},
                ]
            }
        }