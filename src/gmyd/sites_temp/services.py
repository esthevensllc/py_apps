import requests

class LoadSites:
    def __init__(self, repository, dboptda):
        self.repository = repository
        self.dboptda = dboptda

    def execute(self):
        print("sites")
        # result = requests.get("http://172.19.84.74:3002/apis/sites")
        # registros = result.json()["data"]
        # self.oracledb.useConnection("DBOPTDA")
        registros = self.get_data_from_oracle()
        # self.oracledb.useConnection()

        self.repository.delete_all()
        self.repository.insert_from_array(registros)
        print(f"registros: {len(registros)}")
    
    def get_data_from_oracle(self):
        # self.oracledb.useConnection("DBOPTDA")
        result = self.dboptda.fetch("""select
        a.codigo, a.nombre, a.router_acceso, b.tipo tx, c.tipo tipo_integracion from DBOPTDA.tbl_sites a
        left join DBOPTDA.tbl_tipo_tx b on a.id_tx=b.id_tx
        left join DBOPTDA.tbl_tipo_integracion c on a.id_integ=c.id_integ""")
        data = []
        for row in result:
            data.append({
                'CODIGO': row[0],
                'NOMBRE': row[1],
                'ROUTER_ACCESO': row[2],
                'TX': row[3],
                'INTEGRACION': row[4]
            })
        return data