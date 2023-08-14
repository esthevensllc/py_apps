import requests
import json
import datetime

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class SanApi:
    def __init__(self):
        self.base_url = 'https://172.19.147.69:8443/xmlapi'
        #self.user = 'USRRCAPIC'
        #self.password = 'LS#LzxG53'
        #self.token = None
        #self.token_created_date = None
        #self.token_expiration_date = None
        self.def_headers = {'Content-Type': 'application/xml'}
        self.connections = {
            'default': {'base_url': "https://172.19.147.69:8443/xmlapi"},
            'sam_5620': {'base_url': "http://10.140.255.1:8080/xmlapi"},
        }
        self.use('default')

    def use(self, name):
        if self.connections.get(name) is None:
            raise Exception(f"La configuracion '{name}' no existe")
        
        self.base_url = self.connections[name]['base_url']
    
    def invoke(self, options = {}):
        headers = self.def_headers
        if 'headers' in options.keys():
            headers = self.__merge_headers(options['headers'])
        new_options = options.copy()
        new_options['headers'] = headers
        new_options['verify'] = False
        return requests.post(f'{self.base_url}/invoke', **new_options)

    def __merge_headers(self, headers):
        return dict(self.def_headers, **headers)