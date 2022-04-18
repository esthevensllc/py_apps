import cx_Oracle

class DataFijaRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'PSO_DATA_FIJA_TEST'
    
    def update_ubigeos_from_array(self, registros_to_update):
        template = """UPDATE """+self.table+"""
        SET distrito = :distrito, provincia = :provincia, departamento = :departamento, ubigeo = :ubigeo
        WHERE name = :name"""
        bindings = {'distrito': cx_Oracle.STRING, 'provincia': cx_Oracle.STRING, 'departamento': cx_Oracle.STRING, 'ubigeo': cx_Oracle.STRING, 'name': cx_Oracle.STRING}
        config = {'template': template, 'bindings': bindings, 'row_type': 'object'}
        self.db.save_from_array2(config, registros_to_update)

    def get_with_geometry_where_ubigeo_is_null(self):
        sql = """select pso.name, pl.geometry from """+self.table+""" pso
        left join (
            select pl.id, pl.nombre, pl2.geometry from (
                select max(rowid) rowid_, MAX(ID) ID, NOMBRE from PSO_0DATA_19_6748_PLANOS
                WHERE ESTADO = 1 GROUP BY NOMBRE
            ) pl
            inner join PSO_0DATA_19_6748_PLANOS pl2 on pl2.rowid = pl.rowid_
        ) pl on pl.nombre = pso.name
        where pso.estado = 1 and pso.ubigeo is null"""
        new_result = []
        result = self.db.fetch(sql)
        for row in result:
            new_result.append({'name': row[0], 'geometry': row[1].read()})
        return new_result