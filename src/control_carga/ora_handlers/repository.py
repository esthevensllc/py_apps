class OracleHandlersRepository:
    def __init__(self, db, ch):
        self.db = db
        self.ch = ch
        self.table = "padm_carga_resumen_config"
        self.table_handler = "padm_carga_resumen_handler"

    def find_by_id(self, id):
        sql = f"SELECT id, name, query, format, n_order, status FROM {self.table} WHERE id='{id}'"
        resp = self.db.fetch(sql)
        data = []
        for row in resp:
            data.append({
                'id': row[0],
                'name': row[1],
                'query': row[2],
                'format': row[3],
                'n_order': row[4],
                'status': row[5]
            })
        if len(data) > 0:
            return data[0]
        return None

    def get_last_cargas(self, id, env={}):
        config = self.find_by_id(id)
        result = self.db.fetch(config['query'].format(**env))
        data = []
        for row in result:
            data.append({'proyecto': row[0], 'fecha': row[1]})
        return data

    def get_ora_handlers_by_proyecto(self, proyecto, format):
        result = self.db.fetch(F"""
        select proyecto, handler, norder, connection from {self.table_handler}
        where estado=1 and proyecto='{proyecto}' and format='{format}'
        order by proyecto, norder
        """)
        resp = []
        for row in result:
            resp.append({'proyecto': row[0], 'handler': row[1], 'norder': row[2], 'connection': row[3]})
        return resp

    def callproc(self, connection, connection_type, procedure, params):
        if connection_type == "oracle":
            self.db.callproc(procedure, params)
        elif connection_type == "clickhouse":
            self.ch.useConnection(connection)
            self.ch.query(procedure, params)
        else:
            raise Exception("Database type is not supported")