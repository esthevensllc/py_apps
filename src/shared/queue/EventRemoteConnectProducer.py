import time
import datetime

class EventRemoteConnectProducer:
    def __init__(self, queue_service, remote_connect, control_carga):
        self.queue_service = queue_service
        self.remote_connect = remote_connect
        self.control_carga = control_carga
        self.queue_hxh_ids = []
        self.queue_dxd_ids = []
        self.queue_id = 'u2000.alarm_5min.hxh'
        self.proyect_id = 'fija.alarm_5min'
        self.event_date_format = '%Y-%m-%d %H:%M'
        self.time_delta = {'days': 1}
        self.loop = True
    
    def execute(self):
        # print(self.remote_connect.exec_command("ls /opt/oss/server/var/neftpboot/ftproot"))
        # print(self.remote_connect.ssh_connections)
        while True:
            fecha_fin = datetime.datetime.now()
            fecha_ini = fecha_fin - datetime.timedelta(**self.time_delta)
            server_files = self.get_files_between(fecha_ini, fecha_fin)
            uploaded_files = self.control_carga.getOfProyectWhereFechaArchivo(self.proyect_id, fecha_ini, fecha_fin)
            # print([fecha_ini, fecha_fin])
            print("Producer {}  ({} - {})".format(self.queue_id, fecha_ini.strftime('%Y-%m-%d %H:%M:%S'), fecha_fin.strftime('%Y-%m-%d %H:%M:%S')))
            print(len(server_files))
            print(len(uploaded_files))

            range_server_files = range(len(server_files))
            counter_no_valid = 0
            for index in range_server_files:
                validated = False
                server_file = server_files[index]
                # carga_finded = None
                for index2 in range(len(uploaded_files)):
                    if server_files[index]['file'] == uploaded_files[index2]['archivo']:
                        if server_files[index]['updated'] == uploaded_files[index2]['archivo_updated'] and uploaded_files[index2]['estado'] == 'CARGADO':
                            validated = True
                        else:
                            validated = False
                            # print([uploaded_files['file'], uploaded_files[index2]['archivo'], uploaded_files[index2]['estado']])
                            # print([uploaded_files['updated'], uploaded_files[index2]['archivo_updated']])
                
                if validated == False:
                    # make event
                    fecha_file = self.get_fecha_from_file(server_files[index]['file'])
                    eventGenerated = self.queue_service.findByQueueIdAndEstadoAndMsg(self.queue_id, 0, '%{}%'.format(fecha_file.strftime(self.event_date_format)))
                    # print("validando")
                    # print(eventGenerated)
                    if eventGenerated == None:
                        # validated = False
                        counter_no_valid = counter_no_valid + 1
                        print(server_files[index])
                        # msg_body = '{"fec_ini": "'+ fecha_file.strftime(self.event_date_format) +'"}'
                        # self.queue_service.createEvent({'queue_id': self.queue_id, 'msg_body': msg_body})
                        self.create_event(self.queue_id, fecha_file)
                        # else:
                        # validated = True
                        # print(server_files[index])
            print('counter_no_valid: {}'.format(counter_no_valid))
            if self.loop:
                time.sleep(60)
            else:
                break

    def get_fecha_from_file(self, filename):
        # print(filename)
        return datetime.datetime.strptime(filename[0:12], '%Y%m%d%H%M')

    def get_files_between(self, fecha_ini, fecha_fin):
        server_files = self.get_files_of('/opt/oss/server/var/neftpboot/ftproot/20220119', 'alarm-log-auto-1')
        return server_files

    def create_event(self, queue_id, fecha_file):
        msg_body = '{"fec_ini": "'+ fecha_file.strftime(self.event_date_format) +'"}'
        self.queue_service.createEvent({'queue_id': queue_id, 'msg_body': msg_body})

    def get_files_of(self, work_dir, inicial_proyecto):
        # --time-style=long-iso
        command = "ls \""+work_dir+"\" -lt --time-style=\"+%Y-%m-%d %H:%M:%S\" | grep \""+inicial_proyecto+"\" | awk '{print $6, $7, $8}'"
        # resp = self.remote_connect.exec_command(command)
        # "ls /opt/oss/server/var/neftpboot/ftproot -lt --time-style=long-iso | grep Board | awk '{print $6\"_\" $7, $8}'""ls /opt/oss/server/var/neftpboot/ftproot -lt --time-style=long-iso | grep Board | awk '{print $6\"_\" $7, $8}'"
        resp = self.remote_connect.exec_command(command)
        # print('len')
        # print(resp[0])
        archivos = []
        range_files = range(len(resp))
        for index in range_files:
            try:
                archivos.append({'updated': resp[index][0:19], 'file': resp[index][20:len(resp[index])].replace("\n", "")})
            except:
                print(resp[index])
                print(e)
        return archivos
        
    
    def execute_hxh(self):
        while True:
            fecha_ini = datetime.datetime.now() - datetime.timedelta(hours=2)
            str_fecha = fecha_ini.strftime('%Y-%m-%d %H')
            for queue_id in self.queue_hxh_ids:
                event = {'queue_id': queue_id, 'msg_body': '{"fec_ini": "'+str_fecha+'"}'}
                self.queue_service.createEvent(event)
                print(event)
            time.sleep(60*5)
    
    def execute_dxd(self):
        while True:
            fecha_ini = datetime.datetime.now() - datetime.timedelta(hours=2)
            str_fecha = fecha_ini.strftime('%Y-%m-%d %H')
            for queue_id in self.queue_hxh_ids:
                event = {'queue_id': queue_id, 'msg_body': '{"fec_ini": "'+str_fecha+'"}'}
                self.queue_service.createEvent(event)
                print(event)
            time.sleep(60*60)
            


