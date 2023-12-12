import cx_Oracle

class CommandHuaweiConfigRepository:
    def __init__(self, db):
        self.db = db
        self.query = """SELECT
        etiqueta,
        descripcion,
        tipo_elemento,
        flujo,
        estado,
        case
        when tipo_elemento is null then etiqueta
        else etiqueta || '_' || tipo_elemento
        end command,
        nvl(chunk_limit, 10000) chunk_limit
        FROM dump_comando_huawei where estado=1"""

    def get(self):
        result = self.db.fetch(self.query)
        return self.map_result(result)

    def get_by_group(self, group_id):
        result = self.db.fetch(f"{self.query} and flujo = :group_id", {'group_id': group_id})
        return self.map_result(result)

    def map_result(self, result):
        data = []
        for row in result:
            obj = {
                "id": row[5],
                "tag": row[0],
                "description": row[1],
                "element_type": row[2],
                "flujo": row[3],
                "status": row[4],
                "command": row[5],
                "chunk_limit": row[6]
            }
            data.append(obj)
        return data
