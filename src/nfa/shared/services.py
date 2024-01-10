NFA_API = 'src.nfa.stats.NFAApi'
NFA_CONFIG_REPO = 'src.nfa.stats.InMemoryNFAConfigRepository'
LOAD_NFA_FROM_CONFIG = 'src.nfa.stats.LoadNFAFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.nfa.stats.NFAEventConsumerFromConfig'
EVENT_PRODUCER_FROM_CONFIG = 'src.nfa.stats.NFAEventProducerFromConfig'

class NFAAppProvider:
    def __init__(self, app_container):
        def nfa_api(name):
            return NFAApi()
        app_container.bind(NFA_API, nfa_api)

        def in_memory_nfa_config_repo(name):
            from src.nfa.stats.repository import InMemoryNFAConfigRepository
            return InMemoryNFAConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(NFA_CONFIG_REPO, in_memory_nfa_config_repo)

        def load_nfa_from_config(name):
            from src.nfa.stats.services import LoadNFAFromConfig
            deps = app_container.getInstancesInArray(["dboracle", NFA_CONFIG_REPO, NFA_API, "control_carga_repo"])
            return LoadNFAFromConfig(*deps)
        app_container.bind(LOAD_NFA_FROM_CONFIG, load_nfa_from_config)

        def import_event_consumer_from_config(name):
            from src.nfa.stats.services import NFAEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(NFA_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return NFAEventConsumerFromConfig(queue_service, app_container, notification, repository)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)

        def import_event_producer_from_config(name):
            from src.nfa.stats.services import NFAEventProducerFromConfig
            deps = app_container.getInstancesInArray([NFA_CONFIG_REPO, NFA_API, "control_carga_repo", "queue_service"])
            return NFAEventProducerFromConfig(*deps)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)

    
import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
import json

class NFAApi:
    def __init__(self):
        self.base_url = 'http://172.19.219.238:8981'
        self.user = 'usrcalidad'
        self.password = 'CalidAd!!1'
    
    def get(self, uri, options = {}):
        new_options = options.copy()
        new_options['verify'] = False
        new_options['auth'] = HTTPBasicAuth(self.user, self.password)
        return requests.get(f'{self.base_url}/{uri}', **new_options)

    def get_all(self, uri, options = {}):
        str_query_params = urllib.parse.urlparse(uri).query
        query_params = dict(urllib.parse.parse_qsl(str_query_params))
        skip = 20
        if query_params.get("$top") is not None:
            skip = int(query_params["$top"])
        query_params["$skip"] = skip

        base_uri = uri.split("?")[0]

        response = self.get(uri, options)
        result = response.json()
        data = result["value"]
        if result.get("value") is None:
            raise Exception(json.dumps(result))
        
        while len(result["value"]) > 0:
            query_params["$skip"] += skip
            str_query = "&".join([f"{key}={query_params[key]}" for key in query_params.keys()])

            response = self.get(f"{base_uri}?{str_query}", options)
            result = response.json()
            # print(result)
            if result.get("value") is None:
                raise Exception(json.dumps(result))
            data = data + result["value"]
        return data