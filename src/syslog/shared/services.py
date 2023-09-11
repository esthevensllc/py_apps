import requests
import base64
from requests.auth import HTTPBasicAuth

VPNSSL_CONFIG_REPO = 'src.syslog.vpn_ssl.InMemoryVpnSslConfigRepository'
TABLE_ROTATOR = 'src.syslog.vpn_ssl.VpnSslTableRotatorFromConfig'

class SyslogAppProvider:
    def __init__(self, app_container):
        def vpn_ssl_config_repo(name):
            from src.syslog.vpn_ssl.repository import InMemoryVpnSslConfigRepository
            return InMemoryVpnSslConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(VPNSSL_CONFIG_REPO, vpn_ssl_config_repo)

        def vpn_ssl_table_rotator(name):
            from src.shared.carga.services import TableRotatorFromConfig
            repository = app_container.getInstance(VPNSSL_CONFIG_REPO)
            clickhouse = app_container.getInstance("clickhouse")
            clickhouse.useConnection("clickhouse_nce")
            return TableRotatorFromConfig(repository, clickhouse)
        app_container.bind(TABLE_ROTATOR, vpn_ssl_table_rotator)
