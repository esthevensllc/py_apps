class LoadSitiosIPT:
    def __init__(self, repository, db):
        self.repository = repository
        self.db = db

    def execute(self):
        print("load sitios IPT")
        registros = self.get_data_from_source()

        self.repository.delete_all()
        self.repository.insert_from_array(registros)
        print(f"registros: {len(registros)}")
    
    def get_data_from_source(self):
        result = self.db.fetch("""select
            id_sitio, max(codigosite) codigosite, max(nombresite) nombresite, max(latitud) latitud, max(longitud) longitud, max(origen) proveedor,
            to_char(max(on_air_site), 'yyyy-mm-dd hh24:mi:ss') on_air_site, max(departamento) departamento, max(provincia) provincia, max(distrito) distrito,
            max(case when tecnologia='4G'then '4G' end) tec4g,
            max(case when tecnologia='3G'then '3G' end) tec3g
        from SMART.V_PAP_SITIOS_CELDAS_DESEMPENO
        where origen = 'IPT'
        group by id_sitio""")
        data = []
        for row in result:
            data.append({
                'id_sitio': row[0],
                'codigosite': row[1],
                'nombresite': row[2],
                'latitud': row[3],
                'longitud': row[4],
                'proveedor': row[5],
                'on_air_site': row[6],
                'departamento': row[7],
                'provincia': row[8],
                'distrito': row[9],
                'tec4g': row[10],
                'tec3g': row[11],
            })
        return data