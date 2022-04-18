import json

class OracleQueueService:
    def __init__(self, db):
        self.db = db

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
