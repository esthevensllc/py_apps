import requests

class LoadSites:
    def __init__(self, repository):
        self.repository = repository

    def execute(self):
        print("sites")
        result = requests.get("http://172.19.84.74:3002/apis/sites")
        registros = result.json()["data"]

        self.repository.delete_all()
        self.repository.insert_from_array(registros)
        print(f"registros: {len(registros)}")