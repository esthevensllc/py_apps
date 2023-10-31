from src.shared.carga.repository import InMemoryConfigRepository

class InMemoryNetecoConfigRepository(InMemoryConfigRepository):
    def __init__(self, db):
        self.db = db
        self.config_by_id = {
            "1": {
                'id': '1',
                'name': 'managed_object',
                'type': 'inventory',
                # 'server_id': 'zte',
                'work_dir': 'openapi/neteco/nbi/v2/mo',
                'src_type': "paginated-api",
                # 'wk_date_format': '%Y%m%d',
                'file_pattern': 'managed_object_([0-9]{8}).json',
                'file_date_format': '%Y%m%d',
                'limit_to_commit': 5000,
                'tablename': "neteco_managed_object_temp",
                'queue_id': "neteco.managed_object",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': "file",
                'exec_after_st': """BEGIN
                    MERGE INTO neteco_managed_object A
                    USING (SELECT * FROM neteco_managed_object_temp
                    WHERE RESULT_TIME = TO_DATE('{str_filedate}', 'YYYY-MM-DD HH24:MI:SS')) B
                    ON (A.DN = B.DN)
                    WHEN MATCHED THEN UPDATE SET
                        a.CREATETIME = b.CREATETIME,
                        a.TYPENAME = b.TYPENAME,
                        a.NAME = b.NAME,
                        a.TYPEID = b.TYPEID,
                        a.ISROOTDEV = b.ISROOTDEV,
                        a.EXTENDEDATTRS = b.EXTENDEDATTRS,
                        a.TYPEVERID = b.TYPEVERID,
                        a.CATEGORY = b.CATEGORY,
                        a.SUBDEVDNS = b.SUBDEVDNS,
                        a.PARENTDN = b.PARENTDN,
                        a.STATUS = b.STATUS,
                        a.fecha_actualizacion = sysdate,
                        a.estado_seg = 1
                    WHEN NOT MATCHED THEN INSERT(CREATETIME, TYPENAME, NAME, TYPEID, DN, ISROOTDEV,
                    EXTENDEDATTRS, TYPEVERID, CATEGORY, SUBDEVDNS, PARENTDN, STATUS, fecha_insercion, estado_seg)
                    VALUES(b.CREATETIME, b.TYPENAME, b.NAME, b.TYPEID, b.DN, b.ISROOTDEV,
                    b.EXTENDEDATTRS, b.TYPEVERID, b.CATEGORY, b.SUBDEVDNS, b.PARENTDN, b.STATUS, sysdate, 1);
                    commit;

                    UPDATE neteco_managed_object SET estado_seg = 0
                    WHERE DN NOT IN (SELECT DN FROM neteco_managed_object_temp
                        WHERE RESULT_TIME = TO_DATE('{str_filedate}', 'YYYY-MM-DD HH24:MI:SS')
                        GROUP BY DN
                    );
                    COMMIT;

                    DELETE FROM neteco_managed_object_temp;
                    COMMIT;
                END;""",
                'files_permission': None,
                'search_time_ago': '{"days": 2}',
                'loop_time': '{"days": 1}',
                'steps': None,
                'event_format': 'dxd',
                'm_group': 'inventory',
                'fields': [
                    {'fieldname': "result_time", 'src_fieldname': "createTime", 'type': "date", 'map_with': "{env['str_filedate']}", 'to_reload': 1},
                    {'fieldname': "createTime", 'src_fieldname': "createTime", 'type': "date", 'map_with': "{dt.datetime.fromtimestamp(int(value)/1000).strftime('%Y-%m-%d %H:%M:%S')}", 'to_reload': None},
                    {'fieldname': "typeName", 'src_fieldname': "typeName", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "name", 'src_fieldname': "name", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "typeId", 'src_fieldname': "typeId", 'type': "number", 'to_reload': None},
                    {'fieldname': "dn", 'src_fieldname': "dn", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "isRootDev", 'src_fieldname': "isRootDev", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "extendedAttrs", 'src_fieldname': "extendedAttrs", 'type': "varchar2", 'map_with': "{json.dumps(value)}", 'to_reload': None},
                    {'fieldname': "typeVerId", 'src_fieldname': "typeVerId", 'type': "number", 'to_reload': None},
                    {'fieldname': "category", 'src_fieldname': "category", 'type': "number", 'to_reload': None},
                    {'fieldname': "subDevDns", 'src_fieldname': "subDevDns", 'type': "varchar2", 'map_with': "{json.dumps(value)}", 'to_reload': None},
                    {'fieldname': "parentDn", 'src_fieldname': "parentDn", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "status", 'src_fieldname': "status", 'type': "number", 'to_reload': None}
                ]
            },
            "2": {
                'id': '2',
                'name': 'managed_object_type',
                'type': 'inventory',
                'work_dir': 'openapi/neteco/nbi/v2/motype',
                'src_type': "paginated-api",
                'file_pattern': 'managed_object_type_([0-9]{8}).json',
                'file_date_format': '%Y%m%d',
                'limit_to_commit': 5000,
                'tablename': "neteco_managed_object_type_temp",
                'queue_id': "neteco.managed_object_type",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': "file",
                'exec_after_st': """BEGIN
                    MERGE INTO neteco_managed_object_type A
                    USING (SELECT * FROM neteco_managed_object_type_temp
                    WHERE RESULT_TIME = TO_DATE('{str_filedate}', 'YYYY-MM-DD HH24:MI:SS')) B
                    ON (A.typeId = B.typeId)
                    WHEN MATCHED THEN UPDATE SET
                        a.VERSIONDESC = b.VERSIONDESC,
                        a.PARENTTYPES = b.PARENTTYPES,
                        a.VENDOR = b.VENDOR,
                        a.TYPENAME = b.TYPENAME,
                        --a.TYPEID = b.TYPEID,
                        a.TYPEVERID = b.TYPEVERID,
                        a.PROTOCOLTYPE = b.PROTOCOLTYPE,
                        a.FECHA_ACTUALIZACION = sysdate,
                        a.ESTADO_SEG = 1
                    WHEN NOT MATCHED THEN INSERT(VERSIONDESC, PARENTTYPES, VENDOR, TYPENAME,
                    TYPEID, TYPEVERID, PROTOCOLTYPE, FECHA_INSERCION, ESTADO_SEG)
                    VALUES(b.VERSIONDESC, b.PARENTTYPES, b.VENDOR, b.TYPENAME,
                    b.TYPEID, b.TYPEVERID, b.PROTOCOLTYPE, sysdate, 1);
                    commit;

                    UPDATE neteco_managed_object_type SET estado_seg = 0
                    WHERE typeId NOT IN (SELECT typeId FROM neteco_managed_object_type_temp
                        WHERE RESULT_TIME = TO_DATE('{str_filedate}', 'YYYY-MM-DD HH24:MI:SS')
                        GROUP BY typeId
                    );
                    COMMIT;

                    DELETE FROM neteco_managed_object_type_temp;
                    COMMIT;
                END;""",
                'files_permission': None,
                'search_time_ago': '{"days": 2}',
                'loop_time': '{"days": 1}',
                'steps': None,
                'event_format': 'dxd',
                'm_group': 'inventory',
                'fields': [
                    {'fieldname': "result_time", 'src_fieldname': "versionDesc", 'type': "date", 'map_with': "{env['str_filedate']}", 'to_reload': 1},
                    {'fieldname': "versionDesc", 'src_fieldname': "versionDesc", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "parentTypes", 'src_fieldname': "parentTypes", 'type': "varchar2", 'map_with': "{json.dumps(value)}", 'to_reload': None},
                    {'fieldname': "vendor", 'src_fieldname': "vendor", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "typeName", 'src_fieldname': "typeName", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "typeId", 'src_fieldname': "typeId", 'type': "number", 'to_reload': None},
                    {'fieldname': "typeVerId", 'src_fieldname': "typeVerId", 'type': "number", 'to_reload': None},
                    {'fieldname': "protocolType", 'src_fieldname': "protocolType", 'type': "varchar2", 'to_reload': None},
                ]
            },
            "3": {
                'id': '3',
                'name': 'alarm_history',
                'type': 'stats',
                'work_dir': 'openapi/neteco/nbi/v2/alarm/history',
                'src_type': "paginated-api",
                'file_pattern': 'alarm_history_([0-9]{10}).json',
                'file_date_format': '%Y%m%d%H',
                'limit_to_commit': 5000,
                'tablename': "neteco_alarm_history",
                'queue_id': "neteco.alarm_history",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': None,
                'exec_after_st': None,
                'files_permission': None,
                'search_time_ago': '{"days": 3}',
                'loop_time': '{"hours": 1}',
                'steps': None,
                'event_format': 'hxh',
                'm_group': 'stats',
                'fields': [
                    {'fieldname': "result_time", 'src_fieldname': "clearedType", 'type': "date", 'map_with': "{env['str_filedate']}", 'to_reload': 1},
                    {'fieldname': "clearedType", 'src_fieldname': "clearedType", 'type': "number", 'to_reload': None},
                    {'fieldname': "ackTime", 'src_fieldname': "ackTime", 'type': "date", 'map_with': "{dt.datetime.fromtimestamp(int(value)/1000).strftime('%Y-%m-%d %H:%M:%S')}", 'to_reload': None},
                    {'fieldname': "locationInfo", 'src_fieldname': "locationInfo", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "userData", 'src_fieldname': "userData", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "isMaintenanceAlarm", 'src_fieldname': "isMaintenanceAlarm", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "clearTime", 'src_fieldname': "clearTime", 'type': "date", 'map_with': "{dt.datetime.fromtimestamp(int(value)/1000).strftime('%Y-%m-%d %H:%M:%S')}", 'to_reload': None},
                    {'fieldname': "isInvalidAlarm", 'src_fieldname': "isInvalidAlarm", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "additionalText", 'src_fieldname': "additionalText", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "dn", 'src_fieldname': "dn", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "siteDn", 'src_fieldname': "siteDn", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "thresholdConfig", 'src_fieldname': "thresholdConfig", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "ackUser", 'src_fieldname': "ackUser", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "moName", 'src_fieldname': "moName", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "path", 'src_fieldname': "path", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "insId", 'src_fieldname': "insId", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "clearedClass", 'src_fieldname': "clearedClass", 'type': "number", 'to_reload': None},
                    {'fieldname': "alarmValue", 'src_fieldname': "alarmValue", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "reasonId", 'src_fieldname': "reasonId", 'type': "number", 'to_reload': None},
                    {'fieldname': "probableCause", 'src_fieldname': "probableCause", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "alarmSn", 'src_fieldname': "alarmSn", 'type': "number", 'to_reload': None},
                    {'fieldname': "alarmId", 'src_fieldname': "alarmId", 'type': "number", 'to_reload': None},
                    {'fieldname': "additionalInfo", 'src_fieldname': "additionalInfo", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "alarmSource", 'src_fieldname': "alarmSource", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "alarmSeverity", 'src_fieldname': "alarmSeverity", 'type': "number", 'to_reload': None},
                    {'fieldname': "comments", 'src_fieldname': "comments", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "alarmTime", 'src_fieldname': "alarmTime", 'type': "date", 'map_with': "{dt.datetime.fromtimestamp(int(value)/1000).strftime('%Y-%m-%d %H:%M:%S')}", 'to_reload': None},
                    {'fieldname': "latestLogTime", 'src_fieldname': "latestLogTime", 'type': "date", 'map_with': "{dt.datetime.fromtimestamp(int(value)/1000).strftime('%Y-%m-%d %H:%M:%S')}", 'to_reload': None},
                    {'fieldname': "clearStatus", 'src_fieldname': "clearStatus", 'type': "number", 'to_reload': None},
                    {'fieldname': "commentUser", 'src_fieldname': "commentUser", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "alarmName", 'src_fieldname': "alarmName", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "eventType", 'src_fieldname': "eventType", 'type': "number", 'to_reload': None},
                    {'fieldname': "commentTime", 'src_fieldname': "commentTime", 'type': "number", 'to_reload': None},
                    {'fieldname': "thresholdInfo", 'src_fieldname': "thresholdInfo", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "alarmSourceDn", 'src_fieldname': "alarmSourceDn", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "ackStatus", 'src_fieldname': "ackStatus", 'type': "number", 'to_reload': None},
                    {'fieldname': "signalId", 'src_fieldname': "signalId", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "proposedRepairActions", 'src_fieldname': "proposedRepairActions", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "clearUser", 'src_fieldname': "clearUser", 'type': "varchar2", 'to_reload': None},
                ]
            },
            "4": {
                'id': '4',
                'name': 'signal_info',
                'type': 'inventory',
                'work_dir': 'openapi/neteco/nbi/v2/signal/info',
                'src_type': "paginated-api",
                'file_pattern': 'signal_info_([0-9]{8}).json',
                'file_date_format': '%Y%m%d',
                'limit_to_commit': 5000,
                'tablename': "neteco_signal_info_temp",
                'queue_id': "neteco.signal_info",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': "file",
                'exec_after_st': """BEGIN
                    MERGE INTO neteco_signal_info A
                    USING (SELECT * FROM neteco_signal_info_temp
                    WHERE RESULT_TIME = TO_DATE('{str_filedate}', 'YYYY-MM-DD HH24:MI:SS')) B
                    ON (A.signalId = B.signalId)
                    WHEN MATCHED THEN UPDATE SET
                        a.signalName = b.signalName,
                        a.signalDataType = b.signalDataType,
                        a.period = b.period,
                        a.signalAttr = b.signalAttr,
                        --a.signalId = b.signalId,
                        a.signalType = b.signalType,
                        a.precision = b.precision,
                        a.typeId = b.typeId,
                        a.signalUnit = b.signalUnit,
                        a.typeVerId = b.typeVerId,
                        a.signalEnumInfo = b.signalEnumInfo,
                        a.FECHA_ACTUALIZACION = sysdate,
                        a.ESTADO_SEG = 1
                    WHEN NOT MATCHED THEN INSERT(signalName, signalDataType, period, signalAttr,
                    signalId, signalType, precision, typeId, signalUnit, typeVerId, signalEnumInfo,
                    FECHA_INSERCION, ESTADO_SEG)
                    VALUES(b.signalName, b.signalDataType, b.period, b.signalAttr,
                    b.signalId, b.signalType, b.precision, b.typeId, b.signalUnit, b.typeVerId, b.signalEnumInfo,
                    sysdate, 1);
                    commit;

                    UPDATE neteco_signal_info SET estado_seg = 0
                    WHERE typeId NOT IN (SELECT typeId FROM neteco_signal_info_temp
                        WHERE RESULT_TIME = TO_DATE('{str_filedate}', 'YYYY-MM-DD HH24:MI:SS')
                        GROUP BY typeId
                    );
                    COMMIT;

                    DELETE FROM neteco_signal_info_temp;
                    COMMIT;
                END;""",
                'files_permission': None,
                'search_time_ago': '{"days": 2}',
                'loop_time': '{"days": 1}',
                'steps': None,
                'event_format': 'dxd',
                'm_group': 'inventory',
                'fields': [
                    {'fieldname': "result_time", 'src_fieldname': "signalName", 'type': "date", 'map_with': "{env['str_filedate']}", 'to_reload': 1},
                    {'fieldname': "signalName", 'src_fieldname': "signalName", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "signalDataType", 'src_fieldname': "signalDataType", 'type': "number", 'to_reload': None},
                    {'fieldname': "period", 'src_fieldname': "period", 'type': "number", 'to_reload': None},
                    {'fieldname': "signalAttr", 'src_fieldname': "signalAttr", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "signalId", 'src_fieldname': "signalId", 'type': "number", 'to_reload': None},
                    {'fieldname': "signalType", 'src_fieldname': "signalType", 'type': "number", 'to_reload': None},
                    {'fieldname': "precision", 'src_fieldname': "precision", 'type': "number", 'to_reload': None},
                    {'fieldname': "typeId", 'src_fieldname': "typeId", 'type': "number", 'to_reload': None},
                    {'fieldname': "signalUnit", 'src_fieldname': "signalUnit", 'type': "varchar2", 'to_reload': None},
                    {'fieldname': "typeVerId", 'src_fieldname': "typeVerId", 'type': "number", 'to_reload': None},
                    {'fieldname': "signalEnumInfo", 'src_fieldname': "signalEnumInfo", 'type': "varchar2", 'map_with': "{json.dumps(value)}", 'to_reload': None},
                ]
            }
        }