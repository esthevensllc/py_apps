import os

FPING_IP_FINDER = 'src.fping.maestro.fping_finder'
FPING_IP_FINDER_PROCESS = 'src.fping.maestro.FpingIpFinderProcess'
SEND_FILE_ACTIVE_IPS = 'src.fping.maestro.SendFileActiveIps'

class FpingAppProvider:
    def __init__(self, app_container):
        def fping_ip_finder(name):
            from src.fping.maestro.services import IpInfoFinder
            return IpInfoFinder(os.getenv('PYAPP_IPINFO_BASE_URL'), os.getenv('PYAPP_IPINFO_TOKEN'))
        app_container.bind(FPING_IP_FINDER, fping_ip_finder)

        def fping_ip_finder_process(name):
            from src.fping.maestro.services import FpingIpFinderProcess
            ch = app_container.getInstance('clickhouse')
            ch.useConnection('clickhouse_nce')
            return FpingIpFinderProcess(
                app_container.getInstance('queue_service'),
                app_container.getInstance(FPING_IP_FINDER),
                ch
            )
        app_container.bind(FPING_IP_FINDER_PROCESS, fping_ip_finder_process)

        def send_file_active_ips(name):
            from src.fping.maestro.services import SendFileActiveIps
            ch = app_container.getInstance('clickhouse')
            ch.useConnection('clickhouse_nce')
            return SendFileActiveIps(ch, app_container.getInstance('sftp_service'))
        app_container.bind(SEND_FILE_ACTIVE_IPS, send_file_active_ips)
