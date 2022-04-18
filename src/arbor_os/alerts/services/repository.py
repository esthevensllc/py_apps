from re import template
import cx_Oracle

class AlertRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'arbor_alert'

    def delete_where_collectiontime_between(self, fecha1, fecha2):
        sql = "DELETE FROM "+self.table+" WHERE start_time>=TO_DATE('{}', 'YYYYMMDDHH24MI') and start_time<TO_DATE('{}', 'YYYYMMDDHH24MI')".format(fecha1.strftime('%Y%m%d%H%M'), fecha2.strftime('%Y%m%d%H%M'))
        self.db.query(sql)

    def insert_from_array(self, registros_to_insert):
        template = "INSERT INTO "+self.table+"(id, alert_class, alert_type, classification, importance, ongoing, start_time, stop_time, bgp_aspath, bgp_bgp_prefix, bgp_local_prefix, bgp_new_aspath, bgp_new_nexthop, bgp_old_aspath, bgp_old_nexthop, bgp_trap_type, bgp_updates, cloudsignal_fault_description, data_bgp_session_name, dos_countries, dos_destination_mac_address, dos_direction, dos_dot1q_vlan_id, dos_fast_detected, dos_host_address, dos_impact_boundary, dos_impact_bps, dos_impact_pps, dos_ip_version, dos_misuse_types, dos_protocols, dos_severity_percent, dos_severity_threshold, dos_severity_unit, smart_thresh_alert_view, smart_thresh_name, smart_thresh_observed, smart_thresh_threshold, smart_thresh_unit, tms_description, tms_dst_address, tms_expected, tms_mean, tms_name, system_error_description, system_error_entity_count, system_error_entity_limit, system_error_entity_type, system_error_type, system_error_threshold, system_error_value, system_event_username, system_event_version, traffic_interface_gid, traffic_interface_name, traffic_interface_speed, traffic_threshold, traffic_type, traffic_unit, traffic_usage, application_id, config_change_host_id, device_id, fingerprint_id, global_detection_settings_id, managed_object_id, mitigation_id, router_id, service_id, traffic_id, moved_mitigation_id, src_group_id, dest_group_id, source_ip_addresses_id) VALUES (:id, :alert_class, :alert_type, :classification, :importance, :ongoing, TO_DATE(:start_time, 'YYYY-MM-DD HH24:MI:SS'), TO_DATE(:stop_time, 'YYYY-MM-DD HH24:MI:SS'), :bgp_aspath, :bgp_bgp_prefix, :bgp_local_prefix, :bgp_new_aspath, :bgp_new_nexthop, :bgp_old_aspath, :bgp_old_nexthop, :bgp_trap_type, :bgp_updates, :cloudsignal_fault_description, :data_bgp_session_name, :dos_countries, :dos_destination_mac_address, :dos_direction, :dos_dot1q_vlan_id, :dos_fast_detected, :dos_host_address, :dos_impact_boundary, :dos_impact_bps, :dos_impact_pps, :dos_ip_version, :dos_misuse_types, :dos_protocols, :dos_severity_percent, :dos_severity_threshold, :dos_severity_unit, :smart_thresh_alert_view, :smart_thresh_name, :smart_thresh_observed, :smart_thresh_threshold, :smart_thresh_unit, :tms_description, :tms_dst_address, :tms_expected, :tms_mean, :tms_name, :system_error_description, :system_error_entity_count, :system_error_entity_limit, :system_error_entity_type, :system_error_type, :system_error_threshold, :system_error_value, :system_event_username, :system_event_version, :traffic_interface_gid, :traffic_interface_name, :traffic_interface_speed, :traffic_threshold, :traffic_type, :traffic_unit, :traffic_usage, :application_id, :config_change_host_id, :device_id, :fingerprint_id, :global_detection_settings_id, :managed_object_id, :mitigation_id, :router_id, :service_id, :traffic_id, :moved_mitigation_id, :src_group_id, :dest_group_id, :source_ip_addresses_id)"
        bindings = {
            'id': cx_Oracle.STRING,
            'alert_class': cx_Oracle.STRING,
            'alert_type': cx_Oracle.STRING,
            'classification': cx_Oracle.STRING,
            'importance': cx_Oracle.NUMBER,
            'ongoing': cx_Oracle.NUMBER,
            'start_time': cx_Oracle.STRING,
            'stop_time': cx_Oracle.STRING,
            'bgp_aspath': cx_Oracle.STRING,
            'bgp_bgp_prefix': cx_Oracle.STRING,
            'bgp_local_prefix': cx_Oracle.STRING,
            'bgp_new_aspath': cx_Oracle.STRING,
            'bgp_new_nexthop': cx_Oracle.STRING,
            'bgp_old_aspath': cx_Oracle.STRING,
            'bgp_old_nexthop': cx_Oracle.STRING,
            'bgp_trap_type': cx_Oracle.STRING,
            'bgp_updates': cx_Oracle.NUMBER,
            'cloudsignal_fault_description': cx_Oracle.STRING,
            'data_bgp_session_name': cx_Oracle.STRING,
            'dos_countries': cx_Oracle.STRING,
            'dos_destination_mac_address': cx_Oracle.STRING,
            'dos_direction': cx_Oracle.STRING,
            'dos_dot1q_vlan_id': cx_Oracle.NUMBER,
            'dos_fast_detected': cx_Oracle.NUMBER,
            'dos_host_address': cx_Oracle.STRING,
            'dos_impact_boundary': cx_Oracle.STRING,
            'dos_impact_bps': cx_Oracle.NUMBER,
            'dos_impact_pps': cx_Oracle.NUMBER,
            'dos_ip_version': cx_Oracle.NUMBER,
            'dos_misuse_types': cx_Oracle.STRING,
            'dos_protocols': cx_Oracle.STRING,
            'dos_severity_percent': cx_Oracle.NUMBER,
            'dos_severity_threshold': cx_Oracle.NUMBER,
            'dos_severity_unit': cx_Oracle.STRING,
            'smart_thresh_alert_view': cx_Oracle.STRING,
            'smart_thresh_name': cx_Oracle.STRING,
            'smart_thresh_observed': cx_Oracle.NUMBER,
            'smart_thresh_threshold': cx_Oracle.NUMBER,
            'smart_thresh_unit': cx_Oracle.STRING,
            'tms_description': cx_Oracle.STRING,
            'tms_dst_address': cx_Oracle.STRING,
            'tms_expected': cx_Oracle.NUMBER,
            'tms_mean': cx_Oracle.NUMBER,
            'tms_name': cx_Oracle.STRING,
            'system_error_description': cx_Oracle.STRING,
            'system_error_entity_count': cx_Oracle.NUMBER,
            'system_error_entity_limit': cx_Oracle.NUMBER,
            'system_error_entity_type': cx_Oracle.STRING,
            'system_error_type': cx_Oracle.STRING,
            'system_error_threshold': cx_Oracle.NUMBER,
            'system_error_value': cx_Oracle.NUMBER,
            'system_event_username': cx_Oracle.STRING,
            'system_event_version': cx_Oracle.STRING,
            'traffic_interface_gid': cx_Oracle.NUMBER,
            'traffic_interface_name': cx_Oracle.STRING,
            'traffic_interface_speed': cx_Oracle.NUMBER,
            'traffic_threshold': cx_Oracle.NUMBER,
            'traffic_type': cx_Oracle.STRING,
            'traffic_unit': cx_Oracle.STRING,
            'traffic_usage': cx_Oracle.NUMBER,
            'application_id': cx_Oracle.STRING,
            'config_change_host_id': cx_Oracle.STRING,
            'device_id': cx_Oracle.STRING,
            'fingerprint_id': cx_Oracle.STRING,
            'global_detection_settings_id': cx_Oracle.STRING,
            'managed_object_id': cx_Oracle.STRING,
            'mitigation_id': cx_Oracle.STRING,
            'router_id': cx_Oracle.STRING,
            'service_id': cx_Oracle.STRING,
            'traffic_id': cx_Oracle.STRING,
            'moved_mitigation_id': cx_Oracle.STRING,
            'src_group_id': cx_Oracle.STRING,
            'dest_group_id': cx_Oracle.STRING,
            'source_ip_addresses_id': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)

class AlertSrcprefixes:
    def __init__(self, db):
        self.db = db
        self.table = 'arbor_alert_srcprefixes'

    def delete_where_alerts_id(self, alerts_id):
        mapped_id = list(map(lambda v: {'alert_id': v}, alerts_id))
        template = f'DELETE FROM {self.table} WHERE ALERT_ID = :alert_id'
        bindings = {'alert_id': cx_Oracle.STRING}
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, mapped_id)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(ID, ALERT_ID, AVG_VALUE, NAME, CURRENT_VALUE, MAX_VALUE, PCT95_VALUE, STEP, TIMESERIES, TIMESERIES_START, UNIT, RANKING) VALUES (:id, :alert_id, :avg_value, :name, :current_value, :max_value, :pct95_value, :step, :timeseries, TO_DATE(:timeseries_start, 'YYYY-MM-DD HH24:MI:SS'), :unit, :ranking)"

        bindings = {
            'id': cx_Oracle.STRING,
            'alert_id': cx_Oracle.STRING,
            'avg_value': cx_Oracle.NUMBER,
            'name': cx_Oracle.STRING,
            'current_value': cx_Oracle.NUMBER,
            'max_value': cx_Oracle.NUMBER,
            'pct95_value': cx_Oracle.NUMBER,
            'step': cx_Oracle.NUMBER,
            'timeseries': cx_Oracle.STRING,
            'timeseries_start': cx_Oracle.STRING,
            'unit': cx_Oracle.STRING,
            'ranking': cx_Oracle.NUMBER
        }

        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)

class AlertCountryRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'arbor_alert_country'

    def delete_where_alerts_id(self, alerts_id):
        mapped_id = list(map(lambda v: {'alert_id': v}, alerts_id))
        template = f'DELETE FROM {self.table} WHERE ALERT_ID = :alert_id'
        bindings = {'alert_id': cx_Oracle.STRING}
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, mapped_id)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(ID, ALERT_ID, AVG_VALUE, COUNTRY_CODE, NAME, CURRENT_VALUE, MAX_VALUE, PCT95_VALUE, STEP, TIMESERIES, TIMESERIES_START, UNIT, ranking) VALUES (:id, :alert_id, :avg_value, :country_code, :name, :current_value, :max_value, :pct95_value, :step, :timeseries, TO_DATE(:timeseries_start, 'YYYY-MM-DD HH24:MI:SS'), :unit, :ranking)"

        bindings = {
            'id': cx_Oracle.STRING,
            'alert_id': cx_Oracle.STRING,
            'avg_value': cx_Oracle.NUMBER,
            'country_code': cx_Oracle.STRING,
            'name': cx_Oracle.STRING,
            'current_value': cx_Oracle.NUMBER,
            'max_value': cx_Oracle.NUMBER,
            'pct95_value': cx_Oracle.NUMBER,
            'step': cx_Oracle.NUMBER,
            'timeseries': cx_Oracle.STRING,
            'timeseries_start': cx_Oracle.STRING,
            'unit': cx_Oracle.STRING,
            'ranking': cx_Oracle.NUMBER
        }

        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)

class AlertPatternRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'arbor_alert_pattern'

    def delete_where_alerts_id(self, alerts_id):
        mapped_id = list(map(lambda v: {'alert_id': v}, alerts_id))
        template = f'DELETE FROM {self.table} WHERE ALERT_ID = :alert_id'
        bindings = {'alert_id': cx_Oracle.STRING}
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, mapped_id)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(ID, ALERT_ID, ROUTER, PROTOCOL, TIMESERIES_START, ALL_TCP_FLAGS, TIMESERIES_END, STEP, DST_PORT_RANGE_HIGH, DST_PORT_RANGE_LOW, DST_PREFIX, SRC_PORT_RANGE_HIGH, SRC_PORT_RANGE_LOW, TRAFFIC_DATA_CURRENT, TRAFFIC_DATA_MAX, TRAFFIC_DATA_PCT95, TRAFFIC_DATA_AVG, SRC_PREFIX, UNIT, RANKING) VALUES (:id, :alert_id, :router, :protocol, to_date(:timeseries_start, 'yyyy-mm-dd hh24:mi:ss'), :all_tcp_flags, to_date(:timeseries_end, 'yyyy-mm-dd hh24:mi:ss'), :step, :dst_port_range_high, :dst_port_range_low, :dst_prefix, :src_port_range_high, :src_port_range_low, :traffic_data_current, :traffic_data_max, :traffic_data_pct95, :traffic_data_avg, :src_prefix, :unit, :ranking)"

        bindings = {
            'id': cx_Oracle.STRING,
            'alert_id': cx_Oracle.STRING,
            'router': cx_Oracle.STRING,
            'protocol': cx_Oracle.STRING,
            'timeseries_start': cx_Oracle.STRING,
            'all_tcp_flags': cx_Oracle.STRING,
            'timeseries_end': cx_Oracle.STRING,
            'step': cx_Oracle.NUMBER,
            'dst_port_range_high': cx_Oracle.NUMBER,
            'dst_port_range_low': cx_Oracle.NUMBER,
            'dst_prefix': cx_Oracle.STRING,
            'src_port_range_high': cx_Oracle.NUMBER,
            'src_port_range_low': cx_Oracle.NUMBER,
            'traffic_data_current': cx_Oracle.NUMBER,
            'traffic_data_max': cx_Oracle.NUMBER,
            'traffic_data_pct95': cx_Oracle.NUMBER,
            'traffic_data_avg': cx_Oracle.NUMBER,
            'src_prefix': cx_Oracle.STRING,
            'unit': cx_Oracle.STRING,
            'ranking': cx_Oracle.NUMBER
        }

        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 50000}
        self.db.save_from_array2(config, registros_to_insert)