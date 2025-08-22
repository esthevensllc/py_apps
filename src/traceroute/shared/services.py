SPEEDTEST_API = 'src.traceroute.anomalias.SendTracerouteFileActiveIps'

class TracerouteAppProvider:
    def __init__(self, app_container):
        def send_traceroute_file_active_ips(name):
            from src.traceroute.anomalias.services import SendTracerouteFileActiveIps
            deps = app_container.getInstancesInArray(["dbprovider", "sftp_service"])
            deps[0] = deps[0].getConnection("clickhouse_nce")
            return SendTracerouteFileActiveIps(*deps)
        app_container.bind(SPEEDTEST_API, send_traceroute_file_active_ips)
