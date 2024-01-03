import requests
from requests.auth import HTTPBasicAuth

class PMApi:
    def __init__(self):
        self.base_url = 'http://172.19.216.20:8581'
        self.user = 'usrcalidad'
        self.password = 'CalidAd!!1'
    
    def get(self, uri, options = {}):
        new_options = options.copy()
        new_options['verify'] = False
        new_options['auth'] = HTTPBasicAuth(self.user, self.password)
        return requests.get(f'{self.base_url}/{uri}', **new_options)