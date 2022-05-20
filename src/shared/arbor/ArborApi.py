import requests
import datetime

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class ArborApi:
    def __init__(self):
        self.base_url = 'https://172.19.216.87'
        self.user = 'C16343 '
        self.password = 'Claro2022**'
        self.token = None
        self.token_created_date = None
        self.token_expiration_date = None
        self.auth_sessionid = '4d6be8aa4a3766db8ebb3ca912b97669'
        self.auth_auth_tkt = 'NTJmN2Q0MjVhZDY5ZjUyMjVjMThjODczMzY2ZDJmMTU2ZDE3MjE1NDI3ZWIxNmY0MGVmZTY3Mjg1YmMxYjJiNzYyMzFlNmRlQzE2MzE5IWNvbmZfc2hvdyxzcF9hbGVydHMsc3BfYmxhY2tob2xlLHNwX2ZvcmVuc2ljcyxzcF9tYW5hZ2VkX29iamVjdHNfdmlldyxzcF9yZXBvcnRzX2VkaXQsc3BfcmVwb3J0c192aWV3LHNwX3N0YXR1cyxzcF90bXNfbWl0aWdhdGlvbixzcF90cmFmZmljLHNwX3RyYWZmaWNfdmlld19hcyFzeXN0ZW1fdXNlcg%3D%3D'
        self.auth_token = '23JwtWgNiPWsNvg0U2HYSAmPcn66f0FJUvFxsTQR'
        #self.def_headers = {'Content-Type': 'application/json', 'Cookie': f"SESSIONID={self.auth_sessionid}; auth_tkt={self.auth_auth_tkt};"}
        self.def_headers = {'Content-Type': 'application/json', 'X-Arbux-APIToken': self.auth_token}
    
    def get(self, uri, options = {}):
        #self.refresh_token_if_needed()
        cookies = self.def_headers
        if 'headers' in options.keys():
            headers = self.merge_headers(options['headers'])
        new_options = options.copy()
        new_options['headers'] = self.def_headers
        new_options['verify'] = False
        return requests.get(f'{self.base_url}/{uri}', **new_options)

    def post(self, uri, options = {}):
        #self.refresh_token_if_needed()
        cookies = self.def_headers
        if 'headers' in options.keys():
            headers = self.merge_headers(options['headers'])
        new_options = options.copy()
        new_options['headers'] = self.def_headers
        new_options['verify'] = False
        return requests.post(f'{self.base_url}/{uri}', **new_options)
    
    def merge_headers(self, headers):
        return dict(self.def_headers, **headers)
    
    def refresh_token_if_needed(self):
        response = None
        if self.token_expiration_date is None:
            response = self.refresh_token()
        else:
            diff_date = self.token_expiration_date - datetime.datetime.now()
            if diff_date.days < 0 or diff_date.seconds <= 3:
                response = self.refresh_token()
        
        if response is not None:
            # response = response.json()
            # print(response.json())
            # print(response.headers)
            new_cookie = response.headers['Set-Cookie'].split('; ')
            self.auth_auth_tkt = new_cookie[0].replace('auth_tkt=', '')
            # self.token = response['imdata'][0]['aaaLogin']['attributes']['token']
            self.token_created_date = datetime.datetime.now()
            self.token_expiration_date = datetime.datetime.now() + datetime.timedelta(seconds=30)
            self.def_headers['Cookie'] = f"SESSIONID={self.auth_sessionid}; auth_tkt={self.auth_auth_tkt};"

    def refresh_token(self):
        print("refresh token")
        response = requests.get(f'{self.base_url}/system/refresh_session', headers=self.def_headers, verify=False)
        return response