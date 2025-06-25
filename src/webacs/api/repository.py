from src.shared.carga.repository import InMemoryConfigRepository

class InMemoryWebacsConfigRepository(InMemoryConfigRepository):
    def __init__(self):
        self.config_by_id = {
            '1': {
                'id': '1',
                'name': 'alarms',
                'type': 'alarm',
                'server_id': None,
                'work_dir': "",
                'src_uri': "webacs/api/v4/data/Alarms.json?.full=true",
                'file_pattern': 'alarms_([0-9]{12}).json',
                'file_date_format': '%Y%m%d%H%M',
                'chunk_limit': 1000,
                'tablename': "wifi_alarms_temp",
                'queue_id': "webacs.alarms",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': None,
                'exec_after_st': """BEGIN
                    PK_ALARM_WIFI_CISCO.SP_ALARM_WIFI_CISCO(TO_DATE('{str_file_date}', 'YYYYMMDDHH24MI'));
                    
                    DELETE FROM WIFI_ALARMS_TEMP
                    WHERE RESULT_TIME = TO_DATE('{str_file_date}', 'YYYYMMDDHH24MI');
                    COMMIT;

                    DELETE FROM wifi_alarms_annotation_temp
                    WHERE RESULT_TIME = TO_DATE('{str_file_date}', 'YYYYMMDDHH24MI');
                    COMMIT;
                END;""",
                'files_permission': None,
                'search_time_ago': '{"minutes": 1}',
                'loop_time': '{"minutes": 1}',
                'steps': None,
                'event_format': 'mxm',
                "msg_send_filename": True,
                "msg_send_granularity": True,
                'm_group': 'alarms',
                'fields': [
                    {'fieldname': "displayName", 'src_fieldname': "@displayName", 'type': "varchar2"},
                    {'fieldname': "id", 'src_fieldname': "@id", 'type': "number"},
                    {'fieldname': "uuid", 'src_fieldname': "@uuid", 'type': "varchar2"},
                    {'fieldname': "acknowledgementStatus", 'src_fieldname': "acknowledgementStatus", 'type': "number"},
                    {'fieldname': "alarmFoundAt", 'src_fieldname': "alarmFoundAt", 'type': "date"},
                    {'fieldname': "alarmId", 'src_fieldname': "alarmId", 'type': "number"},
                    {'fieldname': "category_ordinal", 'src_fieldname': "category_ordinal", 'type': "number"},
                    {'fieldname': "category_value", 'src_fieldname': "category_value", 'type': "varchar2"},
                    {'fieldname': "condition_ordinal", 'src_fieldname': "condition_ordinal", 'type': "number"},
                    {'fieldname': "condition_value", 'src_fieldname': "condition_value", 'type': "varchar2"},
                    {'fieldname': "deviceName", 'src_fieldname': "deviceName", 'type': "varchar2"},
                    {'fieldname': "deviceTimestamp", 'src_fieldname': "deviceTimestamp", 'type': "date"},
                    {'fieldname': "lastUpdatedAt", 'src_fieldname': "lastUpdatedAt", 'type': "date"},
                    {'fieldname': "message", 'src_fieldname': "message", 'type': "varchar2"},
                    {'fieldname': "nttyaddrss7_address", 'src_fieldname': "nttyaddrss7_address_address", 'type': "varchar2"},
                    {'fieldname': "owner", 'src_fieldname': "owner", 'type': "varchar2"},
                    {'fieldname': "severity", 'src_fieldname': "severity", 'type': "varchar2"},
                    {'fieldname': "source", 'src_fieldname': "source", 'type': "varchar2"},
                    {'fieldname': "timeStamp", 'src_fieldname': "timeStamp", 'type': "date"},
                    {'fieldname': "wirelessSpecificAlarmId", 'src_fieldname': "wirelessSpecificAlarmId", 'type': "varchar2"},
                    {'fieldname': "src_filter_by", 'src_fieldname': "src_filter_by", 'type': "varchar2"},
                    {'fieldname': "result_time", 'src_fieldname': "result_time", 'type': "date", 'to_reload': 1, 'reload_argument': '{file_date}'},
                ],
                'sub_config': [
                    {
                        'tablename': "wifi_alarms_annotation_temp",
                        'chunk_limit': 5000,
                        'field_array': 'annotations',
                        'fields': [
                            {'fieldname': "alarm_id", 'src_fieldname': "alarm_id", 'type': "date"},
                            {'fieldname': "creation_timestamp", 'src_fieldname': "creationTimestamp", 'type': "varchar2"},
                            {'fieldname': "creator_id", 'src_fieldname': "creatorId", 'type': "number"},
                            {'fieldname': "note_text", 'src_fieldname': "noteText", 'type': "number"},
                            {'fieldname': "result_time", 'src_fieldname': "result_time", 'type': "date", 'to_reload': 1, 'reload_argument': '{file_date}'},
                        ]
                    },
                ]
            },
            '2': {
                'id': '2',
                'name': 'alarms_active',
                'type': None,
                'server_id': None,
                'work_dir': "",
                'src_uri': "webacs/api/v4/data/Alarms.json?.full=true&severity=ne(CLEARED)&acknowledgementStatus=false",
                'file_pattern': 'alarms_active_([0-9]{12}).json',
                'file_date_format': '%Y%m%d%H%M',
                'chunk_limit': 1000,
                'tablename': "wifi_alarms_activo_temp",
                'queue_id': "webacs.alarms_active",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': None,
                'exec_after_st': """BEGIN
                    PK_ALARM_WIFI_CISCO.SP_ALARM_ACTIVO_WIFI_CISCO(TO_DATE('{str_file_date}', 'YYYYMMDDHH24MI'));
                    
                    DELETE FROM wifi_alarms_activo_temp
                    WHERE RESULT_TIME = TO_DATE('{str_file_date}', 'YYYYMMDDHH24MI');
                    COMMIT;

                    DELETE FROM wifi_alarms_activo_annotation
                    WHERE RESULT_TIME != TO_DATE('{str_file_date}', 'YYYYMMDDHH24MI');
                    COMMIT;
                END;""",
                'files_permission': None,
                'search_time_ago': '{"minutes": 1}',
                'loop_time': '{"minutes": 1}',
                'steps': None,
                'event_format': 'mxm',
                "msg_send_filename": True,
                "msg_send_granularity": True,
                'm_group': 'alarms_active',
                'fields': [
                    {'fieldname': "displayName", 'src_fieldname': "@displayName", 'type': "varchar2"},
                    {'fieldname': "id", 'src_fieldname': "@id", 'type': "number"},
                    {'fieldname': "uuid", 'src_fieldname': "@uuid", 'type': "varchar2"},
                    {'fieldname': "acknowledgementStatus", 'src_fieldname': "acknowledgementStatus", 'type': "number"},
                    {'fieldname': "alarmFoundAt", 'src_fieldname': "alarmFoundAt", 'type': "date"},
                    {'fieldname': "alarmId", 'src_fieldname': "alarmId", 'type': "number"},
                    {'fieldname': "category_ordinal", 'src_fieldname': "category_ordinal", 'type': "number"},
                    {'fieldname': "category_value", 'src_fieldname': "category_value", 'type': "varchar2"},
                    {'fieldname': "condition_ordinal", 'src_fieldname': "condition_ordinal", 'type': "number"},
                    {'fieldname': "condition_value", 'src_fieldname': "condition_value", 'type': "varchar2"},
                    {'fieldname': "deviceName", 'src_fieldname': "deviceName", 'type': "varchar2"},
                    {'fieldname': "deviceTimestamp", 'src_fieldname': "deviceTimestamp", 'type': "date"},
                    {'fieldname': "lastUpdatedAt", 'src_fieldname': "lastUpdatedAt", 'type': "date"},
                    {'fieldname': "message", 'src_fieldname': "message", 'type': "varchar2"},
                    {'fieldname': "nttyaddrss7_address", 'src_fieldname': "nttyaddrss7_address_address", 'type': "varchar2"},
                    {'fieldname': "owner", 'src_fieldname': "owner", 'type': "varchar2"},
                    {'fieldname': "severity", 'src_fieldname': "severity", 'type': "varchar2"},
                    {'fieldname': "source", 'src_fieldname': "source", 'type': "varchar2"},
                    {'fieldname': "timeStamp", 'src_fieldname': "timeStamp", 'type': "date"},
                    {'fieldname': "wirelessSpecificAlarmId", 'src_fieldname': "wirelessSpecificAlarmId", 'type': "varchar2"},
                    {'fieldname': "src_filter_by", 'src_fieldname': "src_filter_by", 'type': "varchar2"},
                    {'fieldname': "result_time", 'src_fieldname': "result_time", 'type': "date", 'to_reload': 1, 'reload_argument': '{file_date}'},
                ],
                'sub_config': [
                    {
                        'tablename': "wifi_alarms_activo_annotation",
                        'chunk_limit': 5000,
                        'field_array': 'annotations',
                        'fields': [
                            {'fieldname': "alarm_id", 'src_fieldname': "alarm_id", 'type': "date"},
                            {'fieldname': "creation_timestamp", 'src_fieldname': "creationTimestamp", 'type': "varchar2"},
                            {'fieldname': "creator_id", 'src_fieldname': "creatorId", 'type': "number"},
                            {'fieldname': "note_text", 'src_fieldname': "noteText", 'type': "number"},
                            {'fieldname': "result_time", 'src_fieldname': "result_time", 'type': "date", 'to_reload': 1, 'reload_argument': '{file_date}'},
                        ]
                    },
                ]
            },
            '3': {
                'id': '3',
                'name': 'clients',
                'type': None,
                'server_id': None,
                'work_dir': "",
                'src_uri': "webacs/api/v4/data/Clients.json?.full=true",
                'file_pattern': 'clients_([0-9]{12}).json',
                'file_date_format': '%Y%m%d%H%M',
                'chunk_limit': 1000,
                'tablename': "wlc_client_temp",
                'queue_id': "webacs.clients",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': None,
                'exec_after_st': """BEGIN
                    PK_ALARM_WIFI_CISCO.SP_CLIENTS(TO_DATE('{str_file_date}', 'YYYYMMDDHH24MI'));
                    
                    DELETE FROM wlc_client_temp
                    WHERE RESULT_TIME != TO_DATE('{str_file_date}', 'YYYYMMDDHH24MI');
                    COMMIT;
                END;""",
                'files_permission': None,
                'search_time_ago': '{"minutes": 10}',
                'loop_time': '{"minutes": 10}',
                'steps': None,
                'event_format': 'mxm',
                "msg_send_filename": True,
                "msg_send_granularity": True,
                'm_group': 'clients',
                'fields': [
                    {'fieldname': "displayName", 'src_fieldname': "@displayName", 'type': "varchar2"},
                    {'fieldname': "id", 'src_fieldname': "@id", 'type': "number"},
                    {'fieldname': "uuid", 'src_fieldname': "@uuid", 'type': "varchar2"},
                    {'fieldname': "apMacAddress_octets", 'src_fieldname': "apMacAddress_octets", 'type': "varchar2"},
                    {'fieldname': "associationTime", 'src_fieldname': "associationTime", 'type': "date"},
                    {'fieldname': "clientInterface", 'src_fieldname': "clientInterface", 'type': "varchar2"},
                    {'fieldname': "connectionType", 'src_fieldname': "connectionType", 'type': "varchar2"},
                    {'fieldname': "deviceIpAddress_address", 'src_fieldname': "deviceIpAddress_address", 'type': "varchar2"},
                    {'fieldname': "deviceName", 'src_fieldname': "deviceName", 'type': "varchar2"},
                    {'fieldname': "deviceType", 'src_fieldname': "deviceType", 'type': "varchar2"},
                    {'fieldname': "hostname", 'src_fieldname': "hostname", 'type': "varchar2"},
                    {'fieldname': "ipAddress_address", 'src_fieldname': "ipAddress_address", 'type': "varchar2"},
                    {'fieldname': "location", 'src_fieldname': "location", 'type': "varchar2"},
                    {'fieldname': "macAddress_octets", 'src_fieldname': "macAddress_octets", 'type': "varchar2"},
                    {'fieldname': "protocol", 'src_fieldname': "protocol", 'type': "varchar2"},
                    {'fieldname': "securityPolicyStatus", 'src_fieldname': "securityPolicyStatus", 'type': "varchar2"},
                    {'fieldname': "ssid", 'src_fieldname': "ssid", 'type': "varchar2"},
                    {'fieldname': "status", 'src_fieldname': "status", 'type': "varchar2"},
                    {'fieldname': "updateTime", 'src_fieldname': "updateTime", 'type': "date"},
                    {'fieldname': "userName", 'src_fieldname': "userName", 'type': "varchar2"},
                    {'fieldname': "vendor", 'src_fieldname': "vendor", 'type': "varchar2"},
                    {'fieldname': "vlan", 'src_fieldname': "vlan", 'type': "varchar2"},
                    {'fieldname': "vlanId", 'src_fieldname': "vlanId", 'type': "number"},
                    {'fieldname': "result_time", 'src_fieldname': "result_time", 'type': "date", 'to_reload': 1, 'reload_argument': '{file_date}'},
                ]
            },
            '4': {
                'id': '4',
                'name': 'AccessPointDetails',
                'type': None,
                'server_id': None,
                'work_dir': "",
                'src_uri': "webacs/api/v4/data/AccessPointDetails.json?.full=true",
                'file_pattern': 'AccessPointDetails_([0-9]{12}).json',
                'file_date_format': '%Y%m%d%H%M',
                'chunk_limit': 1000,
                'tablename': "WLC_ACCESSPOINTDETAIL_TEMP",
                'queue_id': "webacs.accesspointdetail",
                'status': 1,
                'reload_by': "file",
                'exec_after_by': None,
                'exec_after_st': """BEGIN
                    PK_ALARM_WIFI_CISCO.SP_ACCESSPOINTDETAIL(TO_DATE('{str_file_date}', 'YYYYMMDDHH24MI'));

                    DELETE FROM WLC_ACCESSPOINTDETAIL_TEMP
                    WHERE RESULT_TIME != TO_DATE('{str_file_date}', 'YYYYMMDDHH24MI');
                    COMMIT;

                    DELETE FROM WLC_ACCESSPOINT_CDPNEIGHBOR_TEMP
                    WHERE RESULT_TIME != TO_DATE('{str_file_date}', 'YYYYMMDDHH24MI');
                    COMMIT;

                    DELETE FROM WLC_ACCESSPOINT_reapApVlanAclMapping_temp
                    WHERE RESULT_TIME != TO_DATE('{str_file_date}', 'YYYYMMDDHH24MI');
                    COMMIT;

                    DELETE FROM WLC_ACCESSPOINT_WLANPROFILE_TEMP
                    WHERE RESULT_TIME != TO_DATE('{str_file_date}', 'YYYYMMDDHH24MI');
                    COMMIT;

                    DELETE FROM WLC_ACCESSPOINT_WLANVLANMAPPING_TEMP
                    WHERE RESULT_TIME != TO_DATE('{str_file_date}', 'YYYYMMDDHH24MI');
                    COMMIT;
                END;""",
                'files_permission': None,
                'search_time_ago': '{"minutes": 10}',
                'loop_time': '{"minutes": 10}',
                'steps': None,
                'event_format': 'mxm',
                "msg_send_filename": True,
                "msg_send_granularity": True,
                'm_group': 'accesspointdetail',
                'fields': [
                    {'fieldname': "displayName", 'src_fieldname': "@displayName", 'type': "varchar2"},
                    {'fieldname': "id", 'src_fieldname': "@id", 'type': "varchar2"},
                    {'fieldname': "uuid", 'src_fieldname': "@uuid", 'type': "varchar2"},
                    {'fieldname': "adminStatus", 'src_fieldname': "adminStatus", 'type': "varchar2"},
                    {'fieldname': "apType", 'src_fieldname': "apType", 'type': "varchar2"},
                    {'fieldname': "autoAP_description", 'src_fieldname': "autonomousAP_description", 'type': "varchar2"},
                    {'fieldname': "autoAP_reachable", 'src_fieldname': "autonomousAP_reachable", 'type': "number"},
                    {'fieldname': "autoAP_sysLocation", 'src_fieldname': "autonomousAP_sysLocation", 'type': "varchar2"},
                    {'fieldname': "autoAP_sysObjectId", 'src_fieldname': "autonomousAP_sysObjectId", 'type': "varchar2"},
                    {'fieldname': "autoAP_wgbStatus", 'src_fieldname': "autonomousAP_wgbStatus", 'type': "number"},
                    {'fieldname': "clientCount", 'src_fieldname': "clientCount", 'type': "number"},
                    {'fieldname': "clientCount_2_4GHz", 'src_fieldname': "clientCount_2_4GHz", 'type': "number"},
                    {'fieldname': "clientCount_5GHz", 'src_fieldname': "clientCount_5GHz", 'type': "number"},
                    {'fieldname': "XCoordinate", 'src_fieldname': "coordinates_XCoordinate", 'type': "number"},
                    {'fieldname': "YCoordinate", 'src_fieldname': "coordinates_YCoordinate", 'type': "number"},
                    {'fieldname': "ZCoordinate", 'src_fieldname': "coordinates_ZCoordinate", 'type': "number"},
                    {'fieldname': "ethernetMac_octets", 'src_fieldname': "ethernetMac_octets", 'type': "varchar2"},
                    {'fieldname': "ipAddress_address", 'src_fieldname': "ipAddress_address", 'type': "varchar2"},
                    {'fieldname': "locationHierarchy", 'src_fieldname': "locationHierarchy", 'type': "varchar2"},
                    {'fieldname': "macAddress_octets", 'src_fieldname': "macAddress_octets", 'type': "varchar2"},
                    {'fieldname': "mapLocation", 'src_fieldname': "mapLocation", 'type': "varchar2"},
                    {'fieldname': "model", 'src_fieldname': "model", 'type': "varchar2"},
                    {'fieldname': "name", 'src_fieldname': "name", 'type': "varchar2"},
                    {'fieldname': "reachabilityStatus", 'src_fieldname': "reachabilityStatus", 'type': "varchar2"},
                    {'fieldname': "serialNumber", 'src_fieldname': "serialNumber", 'type': "varchar2"},
                    {'fieldname': "serviceDomainId", 'src_fieldname': "serviceDomainId", 'type': "number"},
                    {'fieldname': "softwareVersion", 'src_fieldname': "softwareVersion", 'type': "varchar2"},
                    {'fieldname': "status", 'src_fieldname': "status", 'type': "varchar2"},
                    {'fieldname': "type", 'src_fieldname': "type", 'type': "varchar2"},
                    {'fieldname': "ApInfo_WIPSEnabled", 'src_fieldname': "unifiedApInfo_WIPSEnabled", 'type': "varchar2"},
                    {'fieldname': "ApInfo_apCertType", 'src_fieldname': "unifiedApInfo_apCertType", 'type': "number"},
                    {'fieldname': "ApInfo_apGroupName", 'src_fieldname': "unifiedApInfo_apGroupName", 'type': "varchar2"},
                    {'fieldname': "ApInfo_apMode", 'src_fieldname': "unifiedApInfo_apMode", 'type': "varchar2"},
                    {'fieldname': "ApInfo_apStaticEnabled", 'src_fieldname': "unifiedApInfo_apStaticEnabled", 'type': "number"},
                    {'fieldname': "ApInfo_bootVersion", 'src_fieldname': "unifiedApInfo_bootVersion", 'type': "varchar2"},
                    {'fieldname': "ApInfo_capwapJoinTakenTime", 'src_fieldname': "unifiedApInfo_capwapJoinTakenTime", 'type': "number"},
                    {'fieldname': "ApInfo_capwapUpTime", 'src_fieldname': "unifiedApInfo_capwapUpTime", 'type': "number"},
                    {'fieldname': "ApInfo_controllerIpAddress", 'src_fieldname': "unifiedApInfo_controllerIpAddress", 'type': "varchar2"},
                    {'fieldname': "ApInfo_controllerName", 'src_fieldname': "unifiedApInfo_controllerName", 'type': "varchar2"},
                    {'fieldname': "ApInfo_contryCode", 'src_fieldname': "unifiedApInfo_contryCode", 'type': "varchar2"},
                    {'fieldname': "ApInfo_encryptionEnabled", 'src_fieldname': "unifiedApInfo_encryptionEnabled", 'type': "varchar2"},
                    {'fieldname': "ApInfo_flexConnectGroupName", 'src_fieldname': "unifiedApInfo_flexConnectGroupName", 'type': "varchar2"},
                    {'fieldname': "ApInfo_flexConnectMode", 'src_fieldname': "unifiedApInfo_flexConnectMode", 'type': "varchar2"},
                    {'fieldname': "ApInfo_iosVersion", 'src_fieldname': "unifiedApInfo_iosVersion", 'type': "varchar2"},
                    {'fieldname': "ApInfo_lastAssociatedTime", 'src_fieldname': "unifiedApInfo_lastAssociatedTime", 'type': "date"},
                    {'fieldname': "ApInfo_lastDissociatedTime", 'src_fieldname': "unifiedApInfo_lastDissociatedTime", 'type': "date"},
                    {'fieldname': "ApInfo_linkLatencyEnabled", 'src_fieldname': "unifiedApInfo_linkLatencyEnabled", 'type': "varchar2"},
                    {'fieldname': "ApInfo_lradMeshNode_meshRole", 'src_fieldname': "unifiedApInfo_lradMeshNode_meshRole", 'type': "varchar2"},
                    {'fieldname': "ApInfo_maintenanceMode", 'src_fieldname': "unifiedApInfo_maintenanceMode", 'type': "varchar2"},
                    {'fieldname': "ApInfo_poeStatusEnum", 'src_fieldname': "unifiedApInfo_poeStatusEnum", 'type': "varchar2"},
                    {'fieldname': "ApInfo_portNumber", 'src_fieldname': "unifiedApInfo_portNumber", 'type': "number"},
                    {'fieldname': "ApInfo_powerInjectorState", 'src_fieldname': "unifiedApInfo_powerInjectorState", 'type': "number"},
                    {'fieldname': "ApInfo_preStandardState", 'src_fieldname': "unifiedApInfo_preStandardState", 'type': "number"},
                    {'fieldname': "ApInfo_primaryMwar", 'src_fieldname': "unifiedApInfo_primaryMwar", 'type': "varchar2"},
                    {'fieldname': "ApInfo_rogueDetectionEnabled", 'src_fieldname': "unifiedApInfo_rogueDetectionEnabled", 'type': "varchar2"},
                    {'fieldname': "ApInfo_secondaryMwar", 'src_fieldname': "unifiedApInfo_secondaryMwar", 'type': "varchar2"},
                    {'fieldname': "ApInfo_sshEnabled", 'src_fieldname': "unifiedApInfo_sshEnabled", 'type': "varchar2"},
                    {'fieldname': "ApInfo_statisticsTimer", 'src_fieldname': "unifiedApInfo_statisticsTimer", 'type': "number"},
                    {'fieldname': "ApInfo_tagInfo_policyTagName", 'src_fieldname': "unifiedApInfo_tagInfo_policyTagName", 'type': "varchar2"},
                    {'fieldname': "ApInfo_tagInfo_rfTagName", 'src_fieldname': "unifiedApInfo_tagInfo_rfTagName", 'type': "varchar2"},
                    {'fieldname': "ApInfo_tagInfo_siteTagName", 'src_fieldname': "unifiedApInfo_tagInfo_siteTagName", 'type': "varchar2"},
                    {'fieldname': "ApInfo_tagInfo_tagSource", 'src_fieldname': "unifiedApInfo_tagInfo_tagSource", 'type': "varchar2"},
                    {'fieldname': "ApInfo_telnetEnabled", 'src_fieldname': "unifiedApInfo_telnetEnabled", 'type': "varchar2"},
                    {'fieldname': "ApInfo_tertiaryMwar", 'src_fieldname': "unifiedApInfo_tertiaryMwar", 'type': "varchar2"},
                    {'fieldname': "ApInfo_vlanEnabled", 'src_fieldname': "unifiedApInfo_vlanEnabled", 'type': "varchar2"},
                    {'fieldname': "ApInfo_vlanNativeId", 'src_fieldname': "unifiedApInfo_vlanNativeId", 'type': "varchar2"},
                    {'fieldname': "upTime", 'src_fieldname': "upTime", 'type': "number"},
                    {'fieldname': "result_time", 'src_fieldname': "result_time", 'type': "date", 'to_reload': 1, 'reload_argument': '{file_date}'},
                ],
                'sub_config': [
                    {
                        'tablename': "WLC_ACCESSPOINT_CDPNEIGHBOR_TEMP",
                        'chunk_limit': 5000,
                        'field_array': 'cdpNeighbors_cdpNeighbor',
                        'fields': [
                            {'fieldname': "accesspoint_id", 'src_fieldname': "parent_id", 'type': "number"},
                            {'fieldname': "capabilities", 'src_fieldname': "capabilities", 'type': "varchar2"},
                            {'fieldname': "duplex", 'src_fieldname': "duplex", 'type': "varchar2"},
                            {'fieldname': "interfaceSpeed", 'src_fieldname': "interfaceSpeed", 'type': "varchar2"},
                            {'fieldname': "localPort", 'src_fieldname': "localPort", 'type': "varchar2"},
                            {'fieldname': "address", 'src_fieldname': "neighborIpAddress_address", 'type': "varchar2"},
                            {'fieldname': "neighborName", 'src_fieldname': "neighborName", 'type': "varchar2"},
                            {'fieldname': "neighborPort", 'src_fieldname': "neighborPort", 'type': "varchar2"},
                            {'fieldname': "platform", 'src_fieldname': "platform", 'type': "varchar2"},
                            {'fieldname': "result_time", 'src_fieldname': "result_time", 'type': "date", 'to_reload': 1, 'reload_argument': '{file_date}'},
                        ]
                    },
                    {
                        'tablename': "WLC_ACCESSPOINT_reapApVlanAclMapping_temp",
                        'chunk_limit': 5000,
                        'field_array': 'reapApVlanAclMappings_reapApVlanAclMapping',
                        'fields': [
                            {'fieldname': "accesspoint_id", 'src_fieldname': "parent_id", 'type': "number"},
                            {'fieldname': "reapEgressAcl", 'src_fieldname': "reapEgressAcl", 'type': "varchar2"},
                            {'fieldname': "reapIngressAcl", 'src_fieldname': "reapIngressAcl", 'type': "varchar2"},
                            {'fieldname': "reapVlanId", 'src_fieldname': "reapVlanId", 'type': "number"},
                            {'fieldname': "result_time", 'src_fieldname': "result_time", 'type': "date", 'to_reload': 1, 'reload_argument': '{file_date}'},
                        ]
                    },
                    {
                        'tablename': "WLC_ACCESSPOINT_WLANPROFILE_TEMP",
                        'chunk_limit': 5000,
                        'field_array': 'unifiedApInfo_wlanProfiles_wlanProfile',
                        'fields': [
                            {'fieldname': "accesspoint_id", 'src_fieldname': "parent_id", 'type': "number"},
                            {'fieldname': "broadcastSsidEnabled", 'src_fieldname': "broadcastSsidEnabled", 'type': "number"},
                            {'fieldname': "profileName", 'src_fieldname': "profileName", 'type': "varchar2"},
                            {'fieldname': "ssid", 'src_fieldname': "ssid", 'type': "varchar2"},
                            {'fieldname': "result_time", 'src_fieldname': "result_time", 'type': "date", 'to_reload': 1, 'reload_argument': '{file_date}'},
                        ]
                    },
                    {
                        'tablename': "WLC_ACCESSPOINT_WLANVLANMAPPING_TEMP",
                        'chunk_limit': 5000,
                        'field_array': 'unifiedApInfo_wlanVlanMappings_wlanVlanMapping',
                        'fields': [
                            {'fieldname': "accesspoint_id", 'src_fieldname': "parent_id", 'type': "number"},
                            {'fieldname': "ssid", 'src_fieldname': "ssid", 'type': "varchar2"},
                            {'fieldname': "vlanId", 'src_fieldname': "vlanId", 'type': "number"},
                            {'fieldname': "wlanId", 'src_fieldname': "wlanId", 'type': "number"},
                            {'fieldname': "result_time", 'src_fieldname': "result_time", 'type': "date", 'to_reload': 1, 'reload_argument': '{file_date}'},
                        ]
                    },
                ]
            }
        }