import json

class OracleQueueService:
    def __init__(self, db):
        self.db = db

    def find_config_by_id(self, id):
        query = f"SELECT ID, DESCRIPCION, GROUP_ID, ESTADO, NOTIFY_ERROR_TO FROM PADM_QUEUE_CONFIG WHERE ID = '{id}'"
        result = self.db.fetch(query)
        for row in result:
            notify_error_to = row[4].split(',') if row[4] is not None else None
            return {'id': row[0], 'descripcion': row[1], 'group_id': row[2], 'estado': row[3], 'notify_error_to': notify_error_to}
        return None

    def get_configs_by_group_id(self, group_id):
        query = f"SELECT ID, DESCRIPCION, GROUP_ID, ESTADO, NOTIFY_ERROR_TO FROM PADM_QUEUE_CONFIG WHERE GROUP_ID = '{group_id}'"
        result = self.db.fetch(query)
        queue_configs = []
        for row in result:
            notify_error_to = row[4].split(',') if row[4] is not None else None
            queue_configs.append({'id': row[0], 'descripcion': row[1], 'group_id': row[2], 'estado': row[3], 'notify_error_to': notify_error_to})
        return queue_configs

    def getLastEventOf(self, queue_ids):
        str_params = "','".join([str(i) for i in queue_ids])
        sql = """select ID, QUEUE_ID, MSG_BODY, PRIORIDAD, ESTADO, FECHA_REGISTRO from padm_queue_events
        where estado=0 and queue_id in ('{}')
        order by prioridad desc, fecha_registro asc fetch first 1 rows only""".format(str_params)
        result = self.db.fetch(sql)
        # print(sql)
        # print(result)
        for index in range(len(result)):
            row = result[index]
            msg_body = json.loads(row[2].read())
            self.db.save(f"UPDATE padm_queue_events SET ESTADO = 2, FECHA_INI_EXEC = SYSDATE WHERE ID = :id", {"id": row[0]})
            return {'id': row[0],'queue_id':  row[1],'msg_body': msg_body,'prioridad': row[3],'estado': row[4],'fecha_registro': row[5]}
        return None
    
    def updateResultOfEvent(self, data):
        # sql = """UPDATE padm_queue_events SET ESTADO='{estado}', FECHA_INI_EXEC=TO_DATE('{fecha_ini_exec}', 'dd/mm/yyyy hh24:mi:ss'), FECHA_FIN_EXEC = TO_DATE('{fecha_fin_exec}', 'dd/mm/yyyy hh24:mi:ss'), MESSAGE = '{message}'
        # WHERE ID='{id}'""".format(**data)
        template = """UPDATE padm_queue_events SET ESTADO=:estado, FECHA_INI_EXEC=TO_DATE(:fecha_ini_exec, 'dd/mm/yyyy hh24:mi:ss'), FECHA_FIN_EXEC = TO_DATE(:fecha_fin_exec, 'dd/mm/yyyy hh24:mi:ss'), MESSAGE = :message
        WHERE ID=:id"""
        self.db.save(template, data, 'object')

    def findByQueueIdAndEstadoAndMsg(self, queue_id, estado, msg_body):
        sql = """select ID, QUEUE_ID, MSG_BODY, PRIORIDAD, ESTADO, FECHA_REGISTRO from padm_queue_events
        where estado={} and queue_id = '{}' and msg_body like '{}'
        order by prioridad desc, fecha_registro asc fetch first 1 rows only""".format(estado, queue_id, msg_body)
        result = self.db.fetch(sql)
        # print(sql)
        # print(result)
        for index in range(len(result)):
            row = result[index]
            msg_body = json.loads(row[2].read())
            return {'id': row[0],'queue_id':  row[1],'msg_body': msg_body,'prioridad': row[3],'estado': row[4],'fecha_registro': row[5]}
        return None

    def createEvent(self, data):
        if 'prioridad' not in data.keys():
            data['prioridad'] = 0
        template = "insert into padm_queue_events(queue_id, msg_body, prioridad, fecha_REGISTRO) VALUES (:queue_id, :msg_body, :prioridad, SYSDATE)"
        self.db.save(template, data, 'object')

    def find_by_queue_id_and_estado(self, queue_id, estados: list):
        str_binds_estados = ", ".join([f":estado_{index}" for index in range(len(estados))])
        bind_values = {'queue_id': queue_id}
        for index in range(len(estados)):
            bind_values[f'estado_{index}'] = estados[index]
        
        sql = f"""select ID, QUEUE_ID, MSG_BODY, PRIORIDAD, ESTADO, FECHA_REGISTRO from padm_queue_events
        where estado in ({str_binds_estados}) and queue_id = :queue_id
        order by prioridad desc, fecha_registro asc"""
        result = self.db.fetch(sql, bind_values)
        
        for index in range(len(result)):
            row = result[index]
            msg_body = json.loads(row[2].read())
            result[index] = {'id': row[0],'queue_id':  row[1],'msg_body': msg_body,'prioridad': row[3],'estado': row[4],'fecha_registro': row[5]}
        return result
