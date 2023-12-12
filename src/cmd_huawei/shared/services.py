import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

CMDHUAWEI_CONFIG_REPO = 'src.cmd_huawei.dump.CommandHuaweiConfigRepository'
DOWNLOAD_CMDHUAWEI_FROM_CONFIG = 'src.cmd_huawei.dump.DownloadHuaweiCommandFromConfig'
LOAD_CMDHUAWEI_FROM_CONFIG = 'src.cmd_huawei.dump.LoadCommandsFromConfig'
# EVENT_CONSUMER_FROM_CONFIG = 'src.neteco.reports.NetecoEventConsumerFromConfig'
# EVENT_PRODUCER_FROM_CONFIG = 'src.neteco.reports.NetecoEventProducerFromConfig'

class CmdHuaweiAppProvider:
    def __init__(self, app_container):

        def db_cmdhuawei_config_repo(name):
            from src.cmd_huawei.dump.repository import CommandHuaweiConfigRepository
            oracle = app_container.getInstance('dbprovider').getConnection("desarrollo")
            return CommandHuaweiConfigRepository(oracle)
        app_container.bind(CMDHUAWEI_CONFIG_REPO, db_cmdhuawei_config_repo)
        
        def download_cmdhuawei_dump_from_config(name):
            from src.cmd_huawei.dump.services import DownloadHuaweiCommandFromConfig
            control_carga = app_container.getInstance('control_carga_repo')
            oracle = app_container.getInstance('dbprovider').getConnection("desarrollo")
            return DownloadHuaweiCommandFromConfig(
                app_container.getInstance(CMDHUAWEI_CONFIG_REPO),
                control_carga,
                app_container.getInstance('cache'),
                oracle,
                app_container
            )
        app_container.bind(DOWNLOAD_CMDHUAWEI_FROM_CONFIG, download_cmdhuawei_dump_from_config)

        def load_cmdhuawei_dump_from_config(name):
            from src.cmd_huawei.dump.services import LoadHuaweiCommandFromConfig
            control_carga = app_container.getInstance('control_carga_repo')
            oracle = app_container.getInstance('dbprovider').getConnection("desarrollo")
            return LoadHuaweiCommandFromConfig(app_container.getInstance(CMDHUAWEI_CONFIG_REPO), control_carga, oracle)
        app_container.bind(LOAD_CMDHUAWEI_FROM_CONFIG, load_cmdhuawei_dump_from_config)