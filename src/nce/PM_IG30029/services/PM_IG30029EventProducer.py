from src.shared.queue.EventRemoteConnectProducer import EventRemoteConnectProducer
import datetime
import json

class PM_IG30029EventProducer(EventRemoteConnectProducer):
    def __init__(self, queue_service, remote_connect, control_carga):
        super().__init__(queue_service, remote_connect, control_carga)
        self.queue_id = 'nce.pm_ig30029_15_min'
        self.proyect_id = 'nce.pm_ig30029_15_min'
        self.event_date_format = '%Y-%m-%d %H:%M'
        self.time_delta = {'days': 1}

    def create_event(self, queue_id, fecha_file):
        #msg_body = '{"fec_ini": "'+ fecha_file.strftime(self.event_date_format) +'"}'
        msg_body = json.dumps({'fec_ini': fecha_file.strftime(self.event_date_format), 'format': 'mxm'})
        self.queue_service.createEvent({'queue_id': queue_id, 'msg_body': msg_body})

    def get_fecha_from_file(self, filename):
        # PM_IG30029_15_YYYYMMDDHH24MI_01
        return datetime.datetime.strptime(filename[14:26], '%Y%m%d%H%M')

    def get_files_between(self, fecha_ini, fecha_fin):
        base_remote_dir = f"/hfs_public/nbi/text/pfm_output"
        filter_pattern = 'PM_IG30029_15_.*.csv'
        server_files = []
        try:
            files1 = self.remote_connect.get_filename_and_updated_at(f"{base_remote_dir}/{fecha_fin.strftime('%Y%m%d')}", filter_pattern, cache=True)
            server_files = server_files + files1
            files2 = self.remote_connect.get_filename_and_updated_at(f"{base_remote_dir}/{fecha_ini.strftime('%Y%m%d')}", filter_pattern, cache=True)
            server_files = server_files + files2
        except:
            print(e)
        result = []
        for row in server_files:
            datetime_file = self.get_fecha_from_file(row['file'])
            if fecha_ini <= datetime_file and datetime_file < fecha_fin:
                result.append(row)
        return result