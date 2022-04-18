from src.shared.queue.EventRemoteConnectProducer import EventRemoteConnectProducer
import datetime

class SubrackReportProducer(EventRemoteConnectProducer):
    def __init__(self, queue_service, remote_connect, control_carga):
        super().__init__(queue_service, remote_connect, control_carga)
        self.queue_id = 'u2000.subrack_rep_dia.dxd'
        self.proyect_id = 'fija.subrack_rep_dia'
        self.event_date_format = '%Y-%m-%d'
        self.time_delta = {'days': 10}
    
    def get_fecha_from_file(self, filename):
        # print(filename)
        # Board_Report_2021-12-22_04-00-09.csv
        return datetime.datetime.strptime(filename[len(filename)-23:len(filename)-13], '%Y-%m-%d')

    def get_files_between(self, fecha_ini, fecha_fin):
        server_files = self.get_files_of('/opt/oss/server/var/neftpboot/ftproot', 'Subrack_Report_')
        # server_files2 = self.get_files_of('/opt/oss/server/var/neftpboot/ftproot/{}'.format(fecha_fin.strftime('%Y%m%d')), 'alarm-log-auto-1')
        merge_files = server_files
        result = []
        for index in range(len(merge_files)):
            # datetime_file = datetime.datetime.strptime(merge_files[index]['updated'], '%Y-%m-%d %H:%M:%S')
            datetime_file = self.get_fecha_from_file(merge_files[index]['file'])
            if fecha_ini <= datetime_file and datetime_file < fecha_fin:
                result.append(merge_files[index])
        return result