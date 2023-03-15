
import requests
import datetime as dt

class LoadPeers:
    def __init__(self, repository):
        self.repository = repository

    def execute(self):
        print("load peers from GMyD")

        response = requests.post('http://172.19.84.74:3002/peers/lista?search=todo').json()
        print(list(response))
        if response["ok"] == True:
            print(f"data: {len(response['data'])}")
            self.repository.delete_all()
            data = response["data"]
            for row in data:
                if row['FECHA_CREACION'] is not None:
                    row['FECHA_CREACION'] = dt.datetime.strptime(row['FECHA_CREACION'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')
                if row['FECHA_ACTIVACION'] is not None:
                    row['FECHA_ACTIVACION'] = dt.datetime.strptime(row['FECHA_ACTIVACION'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')
                if row['FECHA_BAJA'] is not None:
                    row['FECHA_BAJA'] = dt.datetime.strptime(row['FECHA_BAJA'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')
                if row['FECHA_ULTIMO_CAMBIO'] is not None:
                    row['FECHA_ULTIMO_CAMBIO'] = dt.datetime.strptime(row['FECHA_ULTIMO_CAMBIO'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')
            self.repository.insert_from_array(data)

            if len(data) > 0:
                print("save hist table")
                self.repository.save_hist(dt.datetime.now())
            else:
                print("hist is not saved, there is no data")

            print("reload portal Reporte licencias ISP")
            self.repository.reload_licencias_isp()
