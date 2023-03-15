import cx_Oracle

class InterfaceStatsRepository:
    def __init__(self, db):
        self.db = db
        #self.table = 'SAN_EQUIPMENT_INTERFACE_STATS'
        self.table = 'SAN_EQUIPMENT_INTERFACE_STATS_LOG'

    def delete_where_collectiontime_between(self, fecha1, fecha2):
        str_fecha1 = fecha1.strftime('%Y%m%d%H%M%S')
        str_fecha2 = fecha2.strftime('%Y%m%d%H%M%S')
        sql = f"DELETE FROM {self.table} WHERE timeCaptured>=TO_DATE('{str_fecha1}', 'YYYYMMDDHH24MISS') and timeCaptured<=TO_DATE('{str_fecha2}', 'YYYYMMDDHH24MISS')"
        self.db.query(sql)

    def __insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(receivedOctets, receivedOctetsPeriodic, receivedUnicastPackets, receivedUnicastPacketsPeriodic, receivedPacketsDiscarded, receivedPacketsDiscardedPeriodic, receivedBadPackets, receivedBadPacketsPeriodic, receivedUnknownProtocolPackets, receivedUnknownProtocolPacketsPeriodic, transmittedOctets, transmittedOctetsPeriodic, transmittedUnicastPackets, transmittedUnicastPacketsPeriodic, outboundPacketsDiscarded, outboundPacketsDiscardedPeriodic, outboundBadPackets, outboundBadPacketsPeriodic, timeCaptured, periodicTime, monitoredObjectClass, monitoredObjectPointer, alarmedObjectClass, alarmedObjectPointer, logRecordClass, displayedName, monitoredObjectSiteId, monitoredObjectSiteName, suspect, createdOnPollType, updatedOnPollType, historyCreated, timeLogged, deploymentState, objectFullName, name, selfAlarmed) VALUES (:receivedOctets, :receivedOctetsPeriodic, :receivedUnicastPackets, :receivedUnicastPacketsPeriodic, :receivedPacketsDiscarded, :receivedPacketsDiscardedPeriodic, :receivedBadPackets, :receivedBadPacketsPeriodic, :receivedUnknownPP, :receivedUnknownPPPer, :transmittedOctets, :transmittedOctetsPeriodic, :transmittedUnicastPackets, :transmittedUnicastPacketsPeriodic, :outboundPacketsDiscarded, :outboundPacketsDiscardedPeriodic, :outboundBadPackets, :outboundBadPacketsPeriodic, TO_DATE(:timeCaptured, 'YYYY-MM-DD HH24:MI:SS'), :periodicTime, :monitoredObjectClass, :monitoredObjectPointer, :alarmedObjectClass, :alarmedObjectPointer, :logRecordClass, :displayedName, :monitoredObjectSiteId, :monitoredObjectSiteName, :suspect, :createdOnPollType, :updatedOnPollType, :historyCreated, :timeLogged, :deploymentState, :objectFullName, :name, :selfAlarmed)"
        bindings = {
            'receivedOctets': cx_Oracle.NUMBER,
            'receivedOctetsPeriodic': cx_Oracle.NUMBER,
            'receivedUnicastPackets': cx_Oracle.NUMBER,
            'receivedUnicastPacketsPeriodic': cx_Oracle.NUMBER,
            'receivedPacketsDiscarded': cx_Oracle.NUMBER,
            'receivedPacketsDiscardedPeriodic': cx_Oracle.NUMBER,
            'receivedBadPackets': cx_Oracle.NUMBER,
            'receivedBadPacketsPeriodic': cx_Oracle.NUMBER,
            'receivedUnknownProtocolPackets': cx_Oracle.NUMBER,
            'receivedUnknownProtocolPacketsPeriodic': cx_Oracle.NUMBER,
            'transmittedOctets': cx_Oracle.NUMBER,
            'transmittedOctetsPeriodic': cx_Oracle.NUMBER,
            'transmittedUnicastPackets': cx_Oracle.NUMBER,
            'transmittedUnicastPacketsPeriodic': cx_Oracle.NUMBER,
            'outboundPacketsDiscarded': cx_Oracle.NUMBER,
            'outboundPacketsDiscardedPeriodic': cx_Oracle.NUMBER,
            'outboundBadPackets': cx_Oracle.NUMBER,
            'outboundBadPacketsPeriodic': cx_Oracle.NUMBER,
            'timeCaptured': cx_Oracle.STRING,
            'periodicTime': cx_Oracle.STRING,
            'monitoredObjectClass': cx_Oracle.STRING,
            'monitoredObjectPointer': cx_Oracle.STRING,
            'alarmedObjectClass': cx_Oracle.STRING,
            'alarmedObjectPointer': cx_Oracle.STRING,
            'logRecordClass': cx_Oracle.STRING,
            'displayedName': cx_Oracle.STRING,
            'monitoredObjectSiteId': cx_Oracle.STRING,
            'monitoredObjectSiteName': cx_Oracle.STRING,
            'suspect': cx_Oracle.STRING,
            'createdOnPollType': cx_Oracle.STRING,
            'updatedOnPollType': cx_Oracle.STRING,
            'historyCreated': cx_Oracle.STRING,
            'timeLogged': cx_Oracle.NUMBER,
            'deploymentState': cx_Oracle.NUMBER,
            'objectFullName': cx_Oracle.STRING,
            'name': cx_Oracle.STRING,
            'selfAlarmed': cx_Oracle.STRING
        }
        map_keys = {
            'receivedUnknownProtocolPackets': 'receivedUnknownPP',
            'receivedUnknownProtocolPacketsPeriodic': 'receivedUnknownPPPer'
        }

        registros_to_insert = self.db.map_data_by_bindings(registros_to_insert, bindings, map_keys)

        bindings.pop('receivedUnknownProtocolPackets')
        bindings.pop('receivedUnknownProtocolPacketsPeriodic')
        bindings['receivedUnknownPP'] = cx_Oracle.NUMBER
        bindings['receivedUnknownPPPer'] = cx_Oracle.NUMBER

        #str_fields = ','.join(list(binds_part))
        #str_bind_fields = ','.join(list(map(lambda f:  f":{f}" if map_keys.get(f) is None else f":{map_keys.get(f)}", list(binds_part))))
        #template = f"INSERT INTO {self.table}({str_fields}) VALUES ({str_bind_fields})"
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 1}
        
        self.db.save_from_array2(config, registros_to_insert)

    def insert_from_array(self, registros_to_insert):
        template = f"INSERT INTO {self.table}(receivedOctets, receivedOctetsPeriodic, receivedUnicastPackets, receivedUnicastPacketsPeriodic, receivedPacketsDiscarded, receivedPacketsDiscardedPeriodic, receivedBadPackets, receivedBadPacketsPeriodic, receivedUnknownProtocolPackets, receivedUnknownProtocolPacketsPeriodic, transmittedOctets, transmittedOctetsPeriodic, transmittedUnicastPackets, transmittedUnicastPacketsPeriodic, outboundPacketsDiscarded, outboundPacketsDiscardedPeriodic, outboundBadPackets, outboundBadPacketsPeriodic, timeCaptured, periodicTime, timeLogged, monitoredObjectClass, monitoredObjectPointer, displayedName, monitoredObjectSiteId, monitoredObjectSiteName, suspect, createdOnPollType, updatedOnPollType, deploymentState, objectFullName, name, selfAlarmed) VALUES (:receivedOctets, :receivedOctetsPeriodic, :receivedUnicastPackets, :receivedUnicastPacketsPeriodic, :receivedPacketsDiscarded, :receivedPacketsDiscardedPeriodic, :receivedBadPackets, :receivedBadPacketsPeriodic, :receivedUnknownProtocolPackets, :receivedUnknownProtocolPP, :transmittedOctets, :transmittedOctetsPeriodic, :transmittedUnicastPackets, :transmittedUnicastPacketsPeriodic, :outboundPacketsDiscarded, :outboundPacketsDiscardedPeriodic, :outboundBadPackets, :outboundBadPacketsPeriodic, TO_DATE(:timeCaptured, 'YYYY-MM-DD HH24:MI:SS'), :periodicTime, TO_DATE(:timeLogged, 'YYYY-MM-DD HH24:MI:SS'), :monitoredObjectClass, :monitoredObjectPointer, :displayedName, :monitoredObjectSiteId, :monitoredObjectSiteName, :suspect, :createdOnPollType, :updatedOnPollType, :deploymentState, :objectFullName, :name, :selfAlarmed)"
        bindings = {
            'receivedOctets': cx_Oracle.NUMBER,
            'receivedOctetsPeriodic': cx_Oracle.NUMBER,
            'receivedUnicastPackets': cx_Oracle.NUMBER,
            'receivedUnicastPacketsPeriodic': cx_Oracle.NUMBER,
            'receivedPacketsDiscarded': cx_Oracle.NUMBER,
            'receivedPacketsDiscardedPeriodic': cx_Oracle.NUMBER,
            'receivedBadPackets': cx_Oracle.NUMBER,
            'receivedBadPacketsPeriodic': cx_Oracle.NUMBER,
            'receivedUnknownProtocolPackets': cx_Oracle.NUMBER,
            'receivedUnknownProtocolPP': cx_Oracle.NUMBER,
            'transmittedOctets': cx_Oracle.NUMBER,
            'transmittedOctetsPeriodic': cx_Oracle.NUMBER,
            'transmittedUnicastPackets': cx_Oracle.NUMBER,
            'transmittedUnicastPacketsPeriodic': cx_Oracle.NUMBER,
            'outboundPacketsDiscarded': cx_Oracle.NUMBER,
            'outboundPacketsDiscardedPeriodic': cx_Oracle.NUMBER,
            'outboundBadPackets': cx_Oracle.NUMBER,
            'outboundBadPacketsPeriodic': cx_Oracle.NUMBER,
            'timeCaptured': cx_Oracle.STRING,
            'periodicTime': cx_Oracle.STRING,
            'timeLogged': cx_Oracle.STRING,
            'monitoredObjectClass': cx_Oracle.STRING,
            'monitoredObjectPointer': cx_Oracle.STRING,
            'displayedName': cx_Oracle.STRING,
            'monitoredObjectSiteId': cx_Oracle.STRING,
            'monitoredObjectSiteName': cx_Oracle.STRING,
            'suspect': cx_Oracle.STRING,
            'createdOnPollType': cx_Oracle.STRING,
            'updatedOnPollType': cx_Oracle.STRING,
            'deploymentState': cx_Oracle.STRING,
            'objectFullName': cx_Oracle.STRING,
            'name': cx_Oracle.STRING,
            'selfAlarmed': cx_Oracle.STRING
        }
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 1000}
        self.db.save_from_array2(config, registros_to_insert)

