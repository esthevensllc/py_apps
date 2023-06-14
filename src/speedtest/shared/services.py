import requests
import base64
from requests.auth import HTTPBasicAuth

SPEEDTEST_API = 'src.speedtest.reports.SpeedTestApi'
SPEEDTEST_CONFIG_REPO = 'src.speedtest.reports.InMemorySpeedTestConfigRepository'
LOAD_SPEEDTEST_FROM_CONFIG = 'src.speedtest.reports.LoadSeedTestFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.speedtest.reports.SpeedTestEventConsumerFromConfig'
EVENT_PRODUCER_FROM_CONFIG = 'src.speedtest.reports.SpeedTestEventProducerFromConfig'

class SpeedTestAppProvider:
    def __init__(self, app_container):
        def speedtest_api(name):
            return SpeedTestApi()
        app_container.bind(SPEEDTEST_API, speedtest_api)
        
        def speedtest_config_repo(name):
            from src.speedtest.reports.repository import InMemorySpeedTestConfigRepository
            return InMemorySpeedTestConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(SPEEDTEST_CONFIG_REPO, speedtest_config_repo)
        
        def load_speedtest_from_config(name):
            from src.speedtest.reports.services import LoadSeedTestFromConfig
            deps = app_container.getInstancesInArray(["dboracle", SPEEDTEST_CONFIG_REPO, SPEEDTEST_API, "control_carga_repo"])
            return LoadSeedTestFromConfig(*deps)
        app_container.bind(LOAD_SPEEDTEST_FROM_CONFIG, load_speedtest_from_config)

        def import_event_consumer_from_config(name):
            from src.speedtest.reports.services import SpeedTestEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            notification = app_container.getInstance('notification_service')
            repository = app_container.getInstance(SPEEDTEST_CONFIG_REPO)
            return SpeedTestEventConsumerFromConfig(queue_service, app_container, notification, repository)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)

        def import_event_producer_from_config(name):
            from src.speedtest.reports.services import SeedTestEventProducerFromConfig
            deps = app_container.getInstancesInArray([SPEEDTEST_CONFIG_REPO, SPEEDTEST_API, "control_carga_repo", "queue_service"])
            return SeedTestEventProducerFromConfig(*deps)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)


class SpeedTestApi:
    def __init__(self):
        self.base_url = 'https://intelligence.speedtest.net'
        self.api_key = '3a3aa5c0-2a04-46a5-9b23-0e897c0a8dad'
        self.api_secret = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.ImNjNDAxZmEzLTA0OTgtNDNkMC04ODgyLWVhY2FhMDExMjY1OCI.6E1zi3lYXj9MsfAzGLkrKeMygHAnOyiU5FiuD_1Y9-U'
        login_credentials = f"{self.api_key}:{self.api_secret}"
        base64_api_key = base64.b64encode(login_credentials.encode('utf-8')).decode('ascii')
        self.default_options = {
            "headers": {
                "Authorization": f"Basic {base64_api_key}"
            },
            "proxies": {'http': 'http://claro-proxy:80', 'https': 'http://claro-proxy:80'}
        }

    def useConnection(self, name):
        pass

    def connect(self, name):
        pass
    
    def get(self, uri, options = {}, base_url=True):
        new_options = self.merge_options(self.default_options, options)
        url = uri
        if base_url:
            url = f"{self.base_url}/{url}"
        return requests.get(url, **new_options)

    def merge_options(self, default_options, options):
        new_options = default_options.copy()
        for key in options.keys():
            if new_options.get(key) is None:
                new_options[key] = options[key]
            else:
                if type(new_options[key]) == type({}):
                    for sub_key in options[key].keys():
                        new_options[key][sub_key] = options[key][sub_key]
        return new_options