import requests
import json
import datetime

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class ApicManagement:
    def __init__(self):
        self.base_url = 'https://172.19.208.156/api'
        self.user = 'USRRCAPIC'
        self.password = 'LS#LzxG53'
        self.token = None
        self.token_created_date = None
        self.token_expiration_date = None
        self.def_headers = {'APIC-Cookie': ''}
    
    def get(self, uri, options = {}):
        self.refresh_token_if_needed()
        # cookies = self.def_headers
        # if 'headers' in options.keys():
        #     headers = self.merge_headers(options['headers'])
        new_options = options.copy()
        new_options['cookies'] = self.def_headers
        new_options['verify'] = False
        return requests.get(f'{self.base_url}/{uri}', **new_options)
    
    def merge_headers(self, headers):
        return dict(self.def_headers, **headers)
    
    def refresh_token_if_needed(self):
        response = None
        if self.token_expiration_date is None:
            response = self.refresh_token()
        else:
            diff_date = self.token_expiration_date - datetime.datetime.now()
            if diff_date <= datetime.timedelta(seconds=20):
                response = self.refresh_token()
        
        if response is not None:
            response = response.json()
            seconds_to_refresh = response['imdata'][0]['aaaLogin']['attributes']['refreshTimeoutSeconds']
            print(f'seconds_to_refresh: {seconds_to_refresh}')
            self.token = response['imdata'][0]['aaaLogin']['attributes']['token']
            self.token_created_date = datetime.datetime.now()
            self.token_expiration_date = datetime.datetime.now() + datetime.timedelta(seconds=int(seconds_to_refresh))
            self.def_headers['APIC-Cookie'] = self.token

    def refresh_token(self):
        response = None
        request_body = {
            "aaaUser" : {
                "attributes" : {
                    "name" : self.user,
                    "pwd" : self.password
                }
            }
        }
        if self.token_expiration_date == None:
            response = requests.post(f'{self.base_url}/aaaLogin.json', data=json.dumps(request_body), verify=False)
        else:
            response = requests.post(f'{self.base_url}/aaaRefresh.json', cookies=self.def_headers, verify=False)
            if response.status_code != 200:
                response = requests.post(f'{self.base_url}/aaaLogin.json', data=json.dumps(request_body), verify=False)
        return response

