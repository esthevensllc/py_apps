import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

NETECO_API = 'src.neteco.shared.neteco_api'
NETECO_CONFIG_REPO = 'src.neteco.reports.InMemoryNetecoConfigRepository'
LOAD_NETECO_FROM_CONFIG = 'src.neteco.reports.LoadNetecoFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.neteco.reports.NetecoEventConsumerFromConfig'
EVENT_PRODUCER_FROM_CONFIG = 'src.neteco.reports.NetecoEventProducerFromConfig'

class NetecoAppProvider:
    def __init__(self, app_container):
        def neteco_api(self):
            return NetecoApi(app_container.getInstance("cache"))
        app_container.bind(NETECO_API, neteco_api)

        def in_memory_neteco_config_repo(name):
            from src.neteco.reports.repository import InMemoryNetecoConfigRepository
            return InMemoryNetecoConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(NETECO_CONFIG_REPO, in_memory_neteco_config_repo)
        
        def load_neteco_from_config(name):
            from src.neteco.reports.services import LoadNetecoFromConfig
            deps = app_container.getInstancesInArray(["dboracle", NETECO_CONFIG_REPO, NETECO_API, "control_carga_repo"])
            return LoadNetecoFromConfig(*deps)
        app_container.bind(LOAD_NETECO_FROM_CONFIG, load_neteco_from_config)

        def import_event_consumer_from_config(name):
            from src.neteco.reports.services import NetecoEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(NETECO_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return NetecoEventConsumerFromConfig(queue_service, app_container, repository, notification)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)
        
        def import_event_producer_from_config(name):
            from src.neteco.reports.services import NetecoEventProducerFromConfig
            deps = app_container.getInstancesInArray([NETECO_CONFIG_REPO, NETECO_API, "control_carga_repo", "queue_service"])
            return NetecoEventProducerFromConfig(*deps)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)


from src.shared.cache.domain import CacheRepository

class NetecoApi:
    def __init__(self, cache_repo: CacheRepository):
        self.cache_repo = cache_repo
        self.base_url = 'https://172.17.31.5:32102/rest'
        self.default_options = {
            "headers": {
                "openid": None
            },
            "verify": False
            # "proxies": {'http': 'http://claro-proxy:80', 'https': 'http://claro-proxy:80'}
        }
        self.default_options["headers"]["openid"] = self.get_token_from_cache()
        self.refresh_token_if_needed()

    def useConnection(self, name):
        pass

    def connect(self, name):
        pass
    
    def get(self, uri, options = {}, base_url=True):
        new_options = self.merge_options(self.default_options, options)
        return requests.get(f"{self.base_url}/{uri}", **new_options)

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

    def get_token_from_cache(self):
        token = self.cache_repo.get("netecoapi.token")
        return token

    def refresh_token_if_needed(self):
        # token = self.default_options["headers"]["openid"]
        response = requests.get(f"{self.base_url}/openapi/neteco/nbi/v2/mo", **self.default_options)
        if response.status_code == 401:
            self.get_session_token()

    def get_session_token(self):
        print("refresing token")
        body = json.dumps({"userid": "Prueba","value": "Claro2023**"})
        response = requests.put(f"{self.base_url}/openapi/sm/session", data=body, headers={"Content-Type": "application/json"}, verify=False)
        rjson = response.json()
        token =  rjson["data"]
        if token is None:
            raise Exception(rjson["description"])
        self.cache_repo.set("netecoapi.token", token)
        self.default_options["headers"]["openid"] = token
