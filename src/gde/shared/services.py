import os
import requests
import json

GDE_API = 'src.gde.stats.GdeApi'
GDE_CONFIG_REPO = 'src.gde.stats.InMemoryGdeConfigRepository'
LOAD_GDE_FROM_CONFIG = 'src.gde.stats.LoadGdeFromConfig'
EVENT_CONSUMER_FROM_CONFIG = 'src.gde.stats.GdeEventConsumerFromConfig'
EVENT_PRODUCER_FROM_CONFIG = 'src.gde.stats.GdeEventProducerFromConfig'

class GdeAppProvider:
    def __init__(self, app_container):
        def gde_api(name):
            return GdeApi()
        app_container.bind(GDE_API, gde_api)

        def in_memory_gde_config_repo(name):
            from src.gde.alarms.repository import InMemoryGdeConfigRepository
            return InMemoryGdeConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(GDE_CONFIG_REPO, in_memory_gde_config_repo)

        def load_gde_from_config(name):
            from src.gde.alarms.services import LoadGdeFromConfig
            deps = app_container.getInstancesInArray(["dboracle", GDE_CONFIG_REPO, GDE_API, "control_carga_repo"])
            return LoadGdeFromConfig(*deps)
        app_container.bind(LOAD_GDE_FROM_CONFIG, load_gde_from_config)

        def import_event_consumer_from_config(name):
            from src.gde.alarms.services import GdeEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            repository = app_container.getInstance(GDE_CONFIG_REPO)
            notification = app_container.getInstance('notification_service')
            return GdeEventConsumerFromConfig(queue_service, app_container, notification, repository)
        app_container.bind(EVENT_CONSUMER_FROM_CONFIG, import_event_consumer_from_config)

        def import_event_producer_from_config(name):
            from src.gde.alarms.services import GdeEventProducerFromConfig
            deps = app_container.getInstancesInArray([GDE_CONFIG_REPO, GDE_API, "control_carga_repo", "queue_service"])
            return GdeEventProducerFromConfig(*deps)
        app_container.bind(EVENT_PRODUCER_FROM_CONFIG, import_event_producer_from_config)


class GdeApi:
    def __init__(self):
        self.base_url = 'https://1at0-sg-studio.teleows.com'
        self.headers = {
            "Authorization": f"Basic {os.getenv('PYAPP_GDE_TOKEN')}"
        }
        self.proxies = {'http': 'http://claro-proxy:80', 'https': 'http://claro-proxy:80'}
    
    def get(self, uri, params={}):
        return requests.get(f'{self.base_url}/{uri}', params=params, proxies=self.proxies, headers=self.headers)

    def get_all(self, uri, params={}):
        response = self.get(uri, params)
        result = response.json()
        if result.get("results") is None:
            raise Exception(json.dumps(result))
        data = result["results"]
        
        params["start"] = 0
        while result["total"] > (params["limit"] + params["start"]):
            params["start"] += params["limit"]

            response = self.get(uri, params)
            result = response.json()
            if result.get("results") is None:
                raise Exception(json.dumps(result))
            data = data + result["results"]
        return data