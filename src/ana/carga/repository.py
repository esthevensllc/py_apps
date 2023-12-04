import cx_Oracle

class ANAConfigRepository:
    def __init__(self, db):
        self.db = db
        self.config_by_id = {
            "1": {
                'id': '1',
                'name': 'Portabilidad',
                'type': 'stats',
                'server_id': 'ana',
                'work_dir': '/space/data/sftpuserTD/files/BASE_NEID/output/',
                'file_pattern': 'Base_Site_Portabilidad_([0-9]{8}).zip',
                'file_date_format': '%Y%m%d',
                'limit_to_commit': 5000,
                'tablename': "ANA_SITE_PORTABILIDAD",
                'queue_id': "Portabilidad",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': None,
                'exec_after_st': None,
                'files_permission': "group",
                'search_time_ago': '{"days": 30}',
                'loop_time': '{"days": 7}',
                'steps': 'unzip',
                'event_format': 'dxd',
                'm_group': '1',
                'fields': [
                    {'fieldname': "DIA", 'src_fieldname': "0", 'type': "date", 'to_reload': None},
                    {'fieldname': "SITE_ID", 'src_fieldname': "1", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "MOVISTAR_OUT", 'src_fieldname': "2", 'type': "number", 'to_reload': None},
                    {'fieldname': "ENTEL_OUT", 'src_fieldname': "3", 'type': "number", 'to_reload': None},
                    {'fieldname': "BITEL_OUT", 'src_fieldname': "4", 'type': "number", 'to_reload': None},
                    {'fieldname': "POSTPAGO_OUT", 'src_fieldname': "5", 'type': "number", 'to_reload': None},
                    {'fieldname': "PREPAGO_OUT", 'src_fieldname': "6", 'type': "number", 'to_reload': None},
                    {'fieldname': "PORT_OUT", 'src_fieldname': "7", 'type': "number", 'to_reload': None},
                    {'fieldname': "PORT_IN", 'src_fieldname': "8", 'type': "number", 'to_reload': None},
                    {'fieldname': "PORT_TOTAL", 'src_fieldname': "9", 'type': "number", 'to_reload': None},
                    {'fieldname': "RESULT_TIME", 'src_fieldname': "0", 'type': "date", 'map_with': "{env['str_filedate']}", 'to_reload': 1}
                ],
            },
            "2": {
                'id': '2',
                'name': 'Base_Red_Neid',
                'type': 'stats',
                'server_id': 'ana',
                'work_dir': '/space/data/sftpuserTD/files/BASE_NEID/output/',
                'file_pattern': 'Base_Red_Neid_([0-9]{8}).zip',
                'file_date_format': '%Y%m%d',
                'limit_to_commit': 10000,
                'tablename': "ana_red_neid",
                'queue_id': "Base_Red_Neid",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': None,
                'exec_after_st': None,
                'files_permission': "group",
                'search_time_ago': '{"days": 5}',
                'loop_time': '{"days": 1}',
                'steps': 'unzip',
                'event_format': 'dxd',
                'm_group': '2',
                'fields': [
                    {'fieldname': "FECHA", 'src_fieldname': "0", 'type': "date", 'to_reload': 1},
                    {'fieldname': "NEID", 'src_fieldname': "1", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "TECNOLOGIA", 'src_fieldname': "2", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "USERS", 'src_fieldname': "3", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "TRAFFIC", 'src_fieldname': "4", 'type': "number", 'to_reload': None},
                ]
            },
            "3": {
                'id': '3',
                'name': 'Base_Sites_Cei',
                'type': 'stats',
                'server_id': 'ana',
                'work_dir': '/space/data/sftpuserTD/files/BASE_CEI/output/',
                'file_pattern': 'Base_Sites_Cei([0-9]{8}).zip',
                'file_date_format': '%Y%m%d',
                'limit_to_commit': 5000,
                'tablename': "ana_sites_cei",
                'queue_id': "Base_Sites_Cei",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': None,
                'exec_after_st': None,
                'files_permission': "group",
                'search_time_ago': '{"days": 30}',
                'loop_time': '{"days": 7}',
                'steps': 'unzip',
                'event_format': 'dxd',
                'm_group': '3',
                'fields': [
                    {'fieldname': "FECHA_REGISTRO", 'src_fieldname': "0", 'type': "date", 'map_with': "{env['str_filedate']}", 'to_reload': 1},
                    {'fieldname': "ID", 'src_fieldname': "0", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "NEID", 'src_fieldname': "1", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "MUY_BUENO", 'src_fieldname': "2", 'type': "number", 'to_reload': None},
                    {'fieldname': "BUENO", 'src_fieldname': "3", 'type': "number", 'to_reload': None},
                    {'fieldname': "REGULAR", 'src_fieldname': "4", 'type': "number", 'to_reload': None},
                    {'fieldname': "MALO", 'src_fieldname': "5", 'type': "number", 'to_reload': None},
                    {'fieldname': "MUY_MALO", 'src_fieldname': "6", 'type': "number", 'to_reload': None}
                ]
            },
            "4": {
                'id': '4',
                'name': 'Evolucion_Clientes_Moviles_Claro',
                'type': 'stats',
                'server_id': 'ana',
                'work_dir': '/space/data/sftpuserTD/files/BASE_NEID/output',
                'file_pattern': 'Evolucion_Clientes_Moviles_Claro_([0-9]{8}).csv',
                'file_date_format': '%Y%m%d',
                'limit_to_commit': 10000,
                'tablename': "ana_evolucion_movil",
                'temp_table': "ana_evolucion_movil_temp",
                'queue_id': "Evolucion_Clientes_Moviles_Claro",
                'status': 1,
                'reload_by': "all",
                'exec_after_by': "all",
                'exec_after_st': """BEGIN
                    DELETE FROM {tablename}
                    WHERE year||'-'||lpad(semana, 2, '0') IN (SELECT MAX(year||'-'||lpad(semana, 2, '0')) FROM {temp_table});
                    COMMIT;

                    INSERT INTO {tablename}(
                    REGION, DEPARTAMENTO, PROVINCIA, DISTRITO, UBIGEO, SEGMENTO, YEAR_SEMANA, YEAR, SEMANA, CANTIDAD
                    )
                    SELECT
                    REGION, DEPARTAMENTO, PROVINCIA, DISTRITO, UBIGEO, SEGMENTO, YEAR||'-'||SEMANA, YEAR, SEMANA, CANTIDAD
                    FROM {temp_table}
                    where YEAR||'-'||SEMANA NOT IN (SELECT DISTINCT YEAR||'-'||SEMANA FROM {tablename});
                    commit;
                END;""",
                'files_permission': "group",
                'search_time_ago': '{"days": 30}',
                'loop_time': '{"days": 7}',
                'steps': None,
                'event_format': 'dxd',
                'm_group': '4',
                'fields': [
                    {'fieldname': "REGION", 'src_fieldname': "0", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "DEPARTAMENTO", 'src_fieldname': "1", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "PROVINCIA", 'src_fieldname': "2", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "DISTRITO", 'src_fieldname': "3", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "UBIGEO", 'src_fieldname': "4", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "SEGMENTO", 'src_fieldname': "5", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "YEAR_SEMANA", 'src_fieldname': "6", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "YEAR", 'src_fieldname': "7", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "SEMANA", 'src_fieldname': "8", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "CANTIDAD", 'src_fieldname': "9", 'type': "number", 'to_reload': None},
                ]
            },
            "5": {
                'id': '5',
                'name': 'Evolucion_Clientes_Moviles_Claro_Trafico',
                'type': 'stats',
                'server_id': 'ana',
                'work_dir': '/space/data/sftpuserTD/files/BASE_NEID/output',
                'file_pattern': 'Evolucion_Clientes_Moviles_Claro_Trafico_([0-9]{8}).csv',
                'file_date_format': '%Y%m%d',
                'limit_to_commit': 10000,
                'tablename': "ana_evolucion_movil_trafico",
                'temp_table': "ana_evolucion_movil_trafico_temp",
                'queue_id': "ana.evol_movil_trafico",
                'status': 1,
                'reload_by': "all",
                'exec_after_by': "all",
                'exec_after_st': """BEGIN
                    INSERT INTO {tablename}(
                    REGION, DEPARTAMENTO, PROVINCIA, DISTRITO, UBIGEO, YEAR_SEMANA, YEAR, SEMANA, TRAFICO_PRE_GB, TRAFICO_PRO_GB, TRAFICO_TOTAL_GB
                    )
                    SELECT
                    REGION, DEPARTAMENTO, PROVINCIA, DISTRITO, UBIGEO, YEAR_SEMANA, YEAR, SEMANA, TRAFICO_PRE_GB, TRAFICO_PRO_GB, TRAFICO_TOTAL_GB
                    FROM {temp_table}
                    where YEAR_SEMANA NOT IN (SELECT DISTINCT YEAR_SEMANA FROM {tablename});
                    commit;
                END;""",
                'files_permission': "group",
                'search_time_ago': '{"days": 30}',
                'loop_time': '{"days": 7}',
                'steps': None,
                'event_format': 'dxd',
                'm_group': '5',
                'fields': [
                    {'fieldname': "REGION", 'src_fieldname': "0", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "DEPARTAMENTO", 'src_fieldname': "1", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "PROVINCIA", 'src_fieldname': "2", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "DISTRITO", 'src_fieldname': "3", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "UBIGEO", 'src_fieldname': "4", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "YEAR_SEMANA", 'src_fieldname': "5", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "YEAR", 'src_fieldname': "6", 'type': "number", 'to_reload': None},
                    {'fieldname': "SEMANA", 'src_fieldname': "7", 'type': "number", 'to_reload': None},
                    {'fieldname': "TRAFICO_PRE_GB", 'src_fieldname': "8", 'type': "number", 'to_reload': None},
                    {'fieldname': "TRAFICO_PRO_GB", 'src_fieldname': "9", 'type': "number", 'to_reload': None},
                    {'fieldname': "TRAFICO_TOTAL_GB", 'src_fieldname': "10", 'type': "number", 'to_reload': None}
                ]
            },
            "6": {
                'id': '6',
                'name': 'Evolucion_Clientes_Moviles_Claro_Recargas',
                'type': 'stats',
                'server_id': 'ana',
                'work_dir': '/space/data/sftpuserTD/files/BASE_NEID/output',
                'file_pattern': 'Evolucion_Clientes_Moviles_Claro_Recargas_([0-9]{8}).csv',
                'file_date_format': '%Y%m%d',
                'limit_to_commit': 10000,
                'tablename': "ana_evolucion_movil_recargas",
                'temp_table': "ana_evolucion_movil_recargas_temp",
                'queue_id': "ana.evol_movil_recargas",
                'status': 1,
                'reload_by': "all",
                'exec_after_by': "all",
                'exec_after_st': """BEGIN
                    INSERT INTO {tablename}(YEAR, SEMANA, REGION, MONTO_RECARGAS)
                    SELECT
                    YEAR, SEMANA, REGION, MONTO_RECARGAS
                    FROM {temp_table}
                    where (YEAR, SEMANA) NOT IN (SELECT DISTINCT YEAR, SEMANA FROM {tablename});
                    commit;
                END;""",
                'files_permission': "group",
                'search_time_ago': '{"days": 30}',
                'loop_time': '{"days": 7}',
                'steps': None,
                'event_format': 'dxd',
                'm_group': '6',
                'fields': [
                    {'fieldname': "YEAR", 'src_fieldname': "0", 'type': "number", 'to_reload': None},
                    {'fieldname': "SEMANA", 'src_fieldname': "1", 'type': "number", 'to_reload': None},
                    {'fieldname': "REGION", 'src_fieldname': "2", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "MONTO_RECARGAS", 'src_fieldname': "3", 'type': "number", 'to_reload': None}
                ]
            }
        }
    
    def get(self):
        result = []
        for id in list(self.config_by_id):
            row = dict(**self.config_by_id[id])
            row.pop("fields")
            result.append(row)
        return result

    def get_by_group_id(self, group_id):
        result = self.get()
        return list(filter(lambda r: r["m_group"] == group_id, result))

    def find(self, id):
        if id in self.config_by_id.keys():
            row = dict(**self.config_by_id[id])
            row.pop("fields")
            return row
        return None
    
    def get_fields_by_id(self, config_id):
        if config_id in self.config_by_id.keys():
            return self.config_by_id[config_id]["fields"]
        return []