from src.shared.carga.repository import InMemoryConfigRepository

class InMemoryPMConfigRepository(InMemoryConfigRepository):
    def __init__(self, db):
        self.db = db
        self.config_by_id = {
            "1": {
                'id': '1',
                'name': 'pm_stats_component',
                'type': 'stats',
                'server_id': None,
                'work_dir': "",
                'api_query': "odata/api/components?$top=2000&$skip=0&top=200&$expand=device,virtualservermfs&$select=device/Name,Name,virtualservermfs/Timestamp,virtualservermfs/im_Bytes,virtualservermfs/im_BytesIn,virtualservermfs/im_BytesOut,virtualservermfs/im_TotalRequestsRecvd,virtualservermfs/im_TotalResponsesRecvd,virtualservermfs/im_CurrentClientConnections,virtualservermfs/im_CurrentServerConnections,virtualservermfs/im_CurrentServerUP&$filter=((startswith(Name, 'VIP') eq true) and (groups/Name eq 'DASHBOARD BALANCEADORES') and (virtualservermfs/Timestamp ne 0))&$format=text/csv",
                'file_pattern': 'pm_stats_component_([0-9]{12}).csv',
                'file_date_format': '%Y%m%d%H%M',
                'limit_to_commit': 5000,
                'tablename': "pm_ctrx_stats_component",
                'queue_id': "pm.stats_component",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': None,
                'exec_after_st': None,
                # 'files_permission': "group",
                'search_time_ago': '{"days": 2}',
                'loop_time': '{"minutes": 5}',
                'steps': None,
                'event_format': 'mxm',
                'm_group': 'stats',
                'fields': [
                    {'fieldname': "result_time", 'src_fieldname': "2", 'type': "date", 'map_with': "{dt.datetime.fromtimestamp(int(value)).strftime('%Y-%m-%d %H:%M:%S')}", 'to_reload': 1},
                    {'fieldname': "name", 'src_fieldname': "0", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "device_name", 'src_fieldname': "1", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "vservermfs_timestamp", 'src_fieldname': "2", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "vservermfs_im_bytes", 'src_fieldname': "3", 'type': "number", 'to_reload': None},
                    {'fieldname': "vservermfs_im_bytesin", 'src_fieldname': "4", 'type': "number", 'to_reload': None},
                    {'fieldname': "vservermfs_im_bytesout", 'src_fieldname': "5", 'type': "number", 'to_reload': None},
                    {'fieldname': "vservermfs_im_totalrequestsrecvd", 'src_fieldname': "6", 'type': "number", 'to_reload': None},
                    {'fieldname': "vservermfs_im_totalresponsesrecvd", 'src_fieldname': "7", 'type': "number", 'to_reload': None},
                    {'fieldname': "vservermfs_im_currentclientconnections", 'src_fieldname': "8", 'type': "number", 'to_reload': None},
                    {'fieldname': "vservermfs_im_currentserverconnections", 'src_fieldname': "9", 'type': "number", 'to_reload': None},
                    {'fieldname': "vservermfs_im_currentserverup", 'src_fieldname': "10", 'type': "number", 'to_reload': None},
                ]
            }
        }