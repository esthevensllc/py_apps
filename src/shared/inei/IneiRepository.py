class IneiRepository:
    def __init__(self, db):
        self.db = db
    
    def get_ubigeos_with_poligono(self):
        sql = """select ubigeo, polygono, ubg.nombre_dpto, ubg.nombre_prov, ubg.nombre_dist,
        ubg.ubigeo_dpto, ubg.ubigeo_prov, ubg.ubigeo_dist
        from cvm_mtv_kml_inei inei
        inner join geo_data_inei ubg on ubg.ubigeo_dist = inei.ubigeo 
        where ubigeo is not null and polygono is not null"""

        new_result = []
        result = self.db.fetch(sql)
        for row in result:
            new_result.append({'ubigeo': row[0], 'polygono': row[1].read(), 'departamento': row[2], 'provincia': row[3], 'distrito': row[4], 'ubigeo_dpto': row[5], 'ubigeo_prov': row[6], 'ubigeo_dist': row[7]})
        return new_result
