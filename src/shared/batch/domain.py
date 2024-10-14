from src.shared.config import DTFORMAT_BY_ALIAS, TDINTERVAL_BY_ALIAS
import datetime as dt
import os
import uuid

class ItemReader:
    def start(self):
        pass
    def read(self):
        pass
    def end(self):
        pass

class ItemProcessor:
    def start(self, context):
        pass
    def process(self, items):
        pass

class ItemWriter:
    def start(self, context):
        pass

    def write(self, items):
        pass

    def complete(self):
        pass

    def error(self, e):
        pass


class DataChunkStep:
    def __init__(self, reader: ItemReader, processor: ItemProcessor, writer: ItemWriter):
        self.reader = reader
        self.processor = processor
        self.writer = writer

    def execute(self, context):
        self.context = context
        try:
            self.reader.start(context)
            self.processor.start(context)
            self.writer.start(context)
            chunk_data = []
            while chunk_data is not None:
                chunk_data = self.reader.read()
                if chunk_data is not None:
                    chunk_data = self.processor.process(chunk_data)
                    self.writer.write(chunk_data)
            self.reader.end()
            self.writer.complete()
        except BaseException as e:
            self.reader.end()
            self.writer.error(e)
            raise e
        return context


class WorkingDirectoryCreator:
    def create(self, wk_path):
        if not os.path.exists(wk_path):
            os.makedirs(wk_path)

        storage_dir = f"{wk_path}/{uuid.uuid4()}"

        os.makedirs(storage_dir)
        if not os.path.exists(storage_dir):
            raise Exception(f"El directorio de trabajo {storage_dir} no se pudo crear y no existe")
        return storage_dir


class EventMapper:
    def execute(self, event):
        self.__guard(event)
        date_format = DTFORMAT_BY_ALIAS[event['msg_body']['format']]
        queue_id = event['queue_id']
        config_id = event['msg_body']['config_id']
        fecha1 = dt.datetime.strptime(event['msg_body']['fec_ini'], date_format)
        fecha2 = None
        if 'fec_fin' in event['msg_body'].keys():
            fecha2 = dt.datetime.strptime(event['msg_body']['fec_fin'], date_format)
        else:
            interval = TDINTERVAL_BY_ALIAS[event['msg_body']['format']]
            granularity = event['msg_body'].get("granularity")
            if granularity is not None:
                if event['msg_body']['format'] == "mxm":
                    interval["minutes"] = granularity
                elif event['msg_body']['format'] == "hxh":
                    interval["hours"] = granularity
                elif event['msg_body']['format'] == "dxd":
                    interval["days"] = granularity
            fecha2 = fecha1 + dt.timedelta(**interval)

        return {'config_id': config_id, 'fecha_ini': fecha1, 'fecha_fin': fecha2, 'filename': event['msg_body'].get('filename')}

    def __guard(self, event):
        msg_body_keys = event['msg_body'].keys()
        if 'config_id' not in msg_body_keys or ('fec_ini' not in msg_body_keys) or ('format' not in msg_body_keys):
            raise Exception("Error no se encontro el atributo config_id, fec_ini o format")

        if type(event['msg_body']['config_id']) != type(''):
            raise Exception("El config_id deven ser una cadena")

        if event['msg_body']['format'] not in list(DTFORMAT_BY_ALIAS):
            raise Exception(f"Formato '{event['msg_body']['format']}' no valido")