from src.shared.carga.repository import InMemoryConfigRepository

class InMemoryFpingMaestroConfigRepository(InMemoryConfigRepository):
    def __init__(self):
        self.config_by_id = {
            "1": {
                'id': '1',
                'name': 'fping_top_ips',
                # 'type': 'alarm',
                'server_id': 'ana',
                'work_dir': "/var/www/html/top_ips_dominios",
                'file_pattern': 'top1000_ips_w([0-9]+).csv',
                'file_date_format': '%G%V%u',
                # 'file_delimiter': ',',
                # 'skip_lines': 0,
                'chunk_limit': 1000,
                'tablename': "dr_transporte_kpi.inventario_top_ips",
                'queue_id': "fping_cgnat.top1000_ips",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': None,
                'exec_after_st': """BEGIN
                    insert into padm_queue_events(queue_id, msg_body)
                    select 'fping_cgnat.send_active_ips', '{{}}' from dual
                    where not exists(
                        select 1 from padm_queue_events
                        where queue_id = 'fping_cgnat.send_active_ips' and estado = 0
                    );

                    commit;
                END;""",
                'files_permission': None,
                'search_time_ago': '{"days": 20}',
                'loop_time': '{"days": 1}',
                'steps': None,
                'event_format': 'dxd',
                "msg_send_filename": True,
                "msg_send_granularity": False,
                'm_group': '1',
                'fields': [
                    {'fieldname': "server_ip", 'src_fieldname': "server_ip", 'type': "varchar2"},
                    {'fieldname': "usuarios", 'src_fieldname': "usuarios", 'type': "varchar2"},
                    {'fieldname': "trafico", 'src_fieldname': "traf_gb", 'type': "varchar2"},
                    {'fieldname': "semana", 'src_fieldname': "semana", 'type': "varchar2", 'to_reload': 1, 'reload_argument': '{semana}'},
                ]
            },
        }