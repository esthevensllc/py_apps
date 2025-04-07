
import requests
import datetime as dt

class LoadPeers:
    def __init__(self, repository, dboptda):
        self.repository = repository
        self.dboptda = dboptda

    def execute(self):
        print("load peers from GMyD")

        # response = requests.get('http://172.19.84.74:3002/peers/lista?search=todo&estado=&capa=').json()
        # print(list(response))
        data = self.get_data()
        print(f"data: {len(data)}")
        self.repository.delete_all()
        # for row in data:
        #     if row['FECHA_CREACION'] is not None:
        #         row['FECHA_CREACION'] = dt.datetime.strptime(row['FECHA_CREACION'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')
        #     if row['FECHA_ACTIVACION'] is not None:
        #         row['FECHA_ACTIVACION'] = dt.datetime.strptime(row['FECHA_ACTIVACION'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')
        #     if row['FECHA_BAJA'] is not None:
        #         row['FECHA_BAJA'] = dt.datetime.strptime(row['FECHA_BAJA'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')
        #     if row['FECHA_ULTIMO_CAMBIO'] is not None:
        #         row['FECHA_ULTIMO_CAMBIO'] = dt.datetime.strptime(row['FECHA_ULTIMO_CAMBIO'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')
        self.repository.insert_from_array(data)

        if len(data) > 0:
            print("save hist table")
            self.repository.save_hist(dt.datetime.now())
        else:
            print("hist is not saved, there is no data")

        print("reload portal Reporte licencias ISP")
        self.repository.reload_licencias_isp()

    def get_data(self):
        result = self.dboptda.fetch("""SELECT
        IRU, TIERONE, PUERTO, BUNDEL, CAPACIDAD, TIPO_IRU, ROUTER, PAIS_DESTINO, CIUDAD_DESTINO,
        PROV_CABLE_SUBM, NAME_CABLE_SUBM, ESTADO, CAPA, TO_CHAR(FECHA_CREACION,'YYYY-MM-DD HH24:MI:SS'), TO_CHAR(FECHA_ACTIVACION, 'YYYY-MM-DD HH24:MI:SS'),
        TO_CHAR(FECHA_ULTIMO_CAMBIO, 'YYYY-MM-DD HH24:MI:SS'), TO_CHAR(FECHA_BAJA, 'YYYY-MM-DD HH24:MI:SS'), RESP_CREACION, RESP_ACTIVACION, RESP_ULTIMO_CAMBIO, RESP_BAJA
        from dboptda.view_tbl_peers""")
        new_result = []
        for row in result:
            new_result.append({
                'IRU': row[0],
                'TIERONE': row[1],
                'PUERTO': row[2],
                'BUNDEL': row[3],
                'CAPACIDAD': row[4],
                'TIPO_IRU': row[5],
                'ROUTER': row[6],
                'PAIS_DESTINO': row[7],
                'CIUDAD_DESTINO': row[8],
                'PROV_CABLE_SUBM': row[9],
                'NAME_CABLE_SUBM': row[10],
                'ESTADO': row[11],
                'CAPA': row[12],
                'FECHA_CREACION': row[13],
                'FECHA_ACTIVACION': row[14],
                'FECHA_ULTIMO_CAMBIO': row[15],
                'FECHA_BAJA': row[16],
                'RESP_CREACION': row[17],
                'RESP_ACTIVACION': row[18],
                'RESP_ULTIMO_CAMBIO': row[19],
                'RESP_BAJA': row[20],
            })
