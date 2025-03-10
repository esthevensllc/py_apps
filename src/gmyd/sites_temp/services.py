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
        id_site, 
        codigo, 
        nombre, 
        direccion, 
        latitud, 
        longitud, 
        router_agregacion, 
        router_acceso, 
        to_char(fecha_creacion, 'yyyy-mm-dd hh24:mi:ss') fecha_creacion, 
        resp_creacion, 
        to_char(fecha_cambio, 'yyyy-mm-dd hh24:mi:ss') fecha_cambio, 
        resp_cambio, 
        to_char(fecha_baja, 'yyyy-mm-dd hh24:mi:ss') fecha_baja, 
        resp_baja, 
        altura_torre, 
        altura_predio, 
        altitud, 
        --id_dep, 
        --id_prov, 
        --id_dist, 
        a.id_tx, 
        a.id_integ, 
        a.id_estado, 
        id_torre, 
        a.id_tipo, 
        ccpp, 
        id_mtc, 
        prob_gub, 
        a.id_tipo_gub, 
        con_gps, 
        --departamento, 
        --provincia, 
        --distrito, 
        b.tipo tx, 
        c.tipo integracion, 
        e.tipo estado,
        --torre
        --icon
        t.tipo tipo,
        g.tipo permiso_gub
        --ubigeo
        from DBOPTDA.tbl_sites a
        left join dboptda.tbl_sites_estado e on e.id_estado = a.id_estado
        left join dboptda.tbl_sites_tipo t on t.id = a.id_tipo
        left join dboptda.tbl_sites_tipo_gubernam g on g.id = a.id_tipo_gub
        left join DBOPTDA.tbl_tipo_tx b on a.id_tx=b.id_tx
        left join DBOPTDA.tbl_tipo_integracion c on a.id_integ=c.id_integ""")
        data = []
        for row in result:
            data.append({
                'id_site': row[0],
                'codigo': row[1],
                'nombre': row[2],
                'direccion': row[3],
                'latitud': row[4],
                'longitud': row[5],
                'router_agregacion': row[6],
                'router_acceso': row[7],
                'fecha_creacion': row[8],
                'resp_creacion': row[9],
                'fecha_cambio': row[10],
                'resp_cambio': row[11],
                'fecha_baja': row[12],
                'resp_baja': row[13],
                'altura_torre': row[14],
                'altura_predio': row[15],
                'altitud': row[16],
                'id_tx': row[17],
                'id_integ': row[18],
                'id_estado': row[19],
                'id_torre': row[20],
                'id_tipo': row[21],
                'ccpp': row[22],
                'id_mtc': row[23],
                'prob_gub': row[24],
                'id_tipo_gub': row[25],
                'con_gps': row[26],
                'tx': row[27],
                'integracion': row[28],
                'estado': row[29],
                'tipo': row[30],
                'permiso_gub': row[31],
            })
        return data