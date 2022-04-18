import cx_Oracle

class PSO_19_6748_6928Repository:
    def __init__(self, db):
        self.db = db
        self.table = 'PSO_0DATA_19_6748_6928_TEST'
    
    def get_lat_lon_where_flag_cobertura_is_null(self):
        sql = """select ndoc, to_number(latitud) latitud, to_number(longitud) longitud from """+self.table+"""
        where estado = 1 and to_number(latitud) is not null and to_number(longitud) is not null and flag_cobertura is null"""
        new_result = []
        result = self.db.fetch(sql)
        for row in result:
            new_result.append({'ndoc': row[0], 'latitud': row[1], 'longitud': row[2]})
        return new_result

    def update_flat_cobertura_from_array(self, registros_to_update):
        template = "UPDATE "+self.table+" SET FLAG_COBERTURA = :flag_cobertura WHERE ndoc = :ndoc"
        bindings = {'ndoc': cx_Oracle.STRING, 'flag_cobertura': cx_Oracle.NUMBER}
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 10000}
        self.db.save_from_array2(config, registros_to_update)