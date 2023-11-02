from src.shared.queue.EventRemoteConnectProducer import EventRemoteConnectProducer
import datetime
import json

class BaseGenericEventProducer(EventRemoteConnectProducer):
    def __init__(self, queue_service, remote_connect, control_carga):
        super().__init__(queue_service, remote_connect, control_carga)
        self.queue_id = ''
        self.proyect_id = ''
        self.event_date_format = '%Y-%m-%d %H:%M'
        self.time_delta = {'hours': 20}
        self.loop = False
        self.medicion_gran = ''

    def set_config(self, queue_id, proyect_id, medicion_gran):
        self.queue_id = queue_id
        self.proyect_id = proyect_id
        self.medicion_gran = medicion_gran

    def create_event(self, queue_id, fecha_file):
        msg_body = json.dumps({'fec_ini': fecha_file.strftime(self.event_date_format), 'format': 'mxm'})
        self.queue_service.createEvent({'queue_id': queue_id, 'msg_body': msg_body})

    def get_fecha_from_file(self, filename):
        # PM_IG64_15_YYYYMMDDHH24MI_01
        return datetime.datetime.strptime(filename.split('_')[3], '%Y%m%d%H%M')

    def get_files_between(self, fecha_ini, fecha_fin):
        base_remote_dir = f"/hfs_public/nbi/text/pfm_output"
        filter_pattern = f'{self.medicion_gran}_.*.csv'
        server_files = []
        fecha_recorrido = fecha_ini
        while fecha_recorrido.strftime('%Y%m%d') <= fecha_fin.strftime('%Y%m%d'):
            try:
                files1 = self.remote_connect.get_filename_and_updated_at(f"{base_remote_dir}/{fecha_recorrido.strftime('%Y%m%d')}", filter_pattern, cache=True)
                server_files = server_files + files1
            except BaseException as e:
                print(e)
            fecha_recorrido = fecha_recorrido + datetime.timedelta(days=1)
        
        result = []
        for row in server_files:
            datetime_file = self.get_fecha_from_file(row['file'])
            if fecha_ini <= datetime_file and datetime_file < fecha_fin:
                result.append(row)
        return result