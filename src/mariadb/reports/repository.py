from src.shared.carga.repository import InMemoryConfigRepository

class InMemoryMariadbConfigRepository(InMemoryConfigRepository):
    def __init__(self, db):
        self.db = db
        self.config_by_id = {
            "1": {
                'id': '1',
                'name': 'planos_caidos',
                'type': 'alarms',
                'server_id': None,
                'work_dir': "",
                'src_query': """select
                id, display_name, ifalias, muestra_inicial, muestra_1,
                DATE_FORMAT(fecha_inicial, '%Y-%m-%d %H:%i:%s') as fecha_inicial, DATE_FORMAT(fecha_fin, '%Y-%m-%d %H:%i:%s') as fecha_fin,
                estado_interno, incidencia_remedy, crq_remedy
                from vw_plano_caidas a
                where (STR_TO_DATE(%(fecha_fin)s, '%Y-%m-%d %H:%i:%s') - interval '25' minute) <= a.{date_field}
                and a.{date_field} <= STR_TO_DATE(%(fecha_ini)s, '%Y-%m-%d %H:%i:%s')""",
                'file_pattern': 'planos_caidos_([0-9]{12})_[0-9].json',
                'file_date_format': '%Y%m%d%H%M',
                'chunk_limit': 5000,
                'limit_to_commit': 5000,
                'skip_lines': 0,
                'tablename': "fija_planos_caidos_actual_aux",
                'queue_id': "mariadb.planos_caidos",
                'status': 1,
                'reload_by': "file",
                'exec_before_by': "all",
                'exec_before_st': """BEGIN
                    DELETE FROM fija_planos_caidos_actual_aux;
                    commit;
                END;""",
                'exec_after_by': "all",
                'exec_after_st': "begin PK_ALARM_MARIADB.sp_alarm_planos_caidos_load; end;",
                'search_time_ago': '{"days": 1}',
                'loop_time': '{"minutes": 5}',
                'msg_send_granularity': True,
                'steps': None,
                'event_format': 'mxm',
                'm_group': 'alarms',
                'fields': [
                    {'fieldname': "result_time", 'src_fieldname': 0, 'type': "date", 'map_with': "{env['str_filedate']}", 'to_reload': 1},
                    {'fieldname': "archivo", 'src_fieldname': 0, 'type': "varchar2", 'map_with': "{env['filename']}", 'to_reload': 1, 'reload_argument': '{filename}'},
                    {'fieldname': "id", 'src_fieldname': 0, 'type': "number", 'to_reload': None},
                    {'fieldname': "display_name", 'src_fieldname': 1, 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "ifalias", 'src_fieldname': 2, 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "muestra_inicial", 'src_fieldname': 3, 'type': "number", 'to_reload': None},
                    {'fieldname': "muestra_1", 'src_fieldname': 4, 'type': "number", 'to_reload': None},
                    {'fieldname': "fecha_inicial", 'src_fieldname': 5, 'type': "date", 'to_reload': None},
                    {'fieldname': "fecha_fin", 'src_fieldname': 6, 'type': "date", 'to_reload': None},
                    {'fieldname': "estado_interno", 'src_fieldname': 7, 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "incidencia_remedy", 'src_fieldname': 8, 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "crq_remedy", 'src_fieldname': 9, 'type': "varchar2", 'to_reload': None},
                ]
            }
        }