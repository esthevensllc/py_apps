from src.shared.queue.EventRemoteConnectProducer import EventRemoteConnectProducer
import datetime

class U2000SlotTempProfileProducer(EventRemoteConnectProducer):
    def __init__(self, queue_service, remote_connect, control_carga):
        super().__init__(queue_service, remote_connect, control_carga)
        self.queue_id = 'fija.slot_temp_15min'
        self.proyect_id = 'fija.slot_temp_15min'
        self.event_date_format = '%Y-%m-%d %H:%M'
        self.time_delta = {'days': 1}

    def get_fecha_from_file(self, filename):
        # PM_IG80336_15_202112220130_01.csv
        return datetime.datetime.strptime(filename[len(filename)-19:len(filename)-7], '%Y%m%d%H%M')

    def get_files_between(self, fecha_ini, fecha_fin):
        server_files = self.get_files_of('/opt/oss/server/var/neftpboot/ftproot/{}'.format(fecha_ini.strftime('%Y%m%d')), 'PM_IG80336_15')
        server_files2 = self.get_files_of('/opt/oss/server/var/neftpboot/ftproot/{}'.format(fecha_fin.strftime('%Y%m%d')), 'PM_IG80336_15')
        merge_files = server_files + server_files2
        result = []
        for index in range(len(merge_files)):
            # datetime_file = datetime.datetime.strptime(merge_files[index]['updated'], '%Y-%m-%d %H:%M:%S')
            datetime_file = self.get_fecha_from_file(merge_files[index]['file'])
            if fecha_ini <= datetime_file and datetime_file < fecha_fin:
                result.append(merge_files[index])
        return result