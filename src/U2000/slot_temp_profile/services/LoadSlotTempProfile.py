import os
import csv
import datetime
from src.shared.config import STORAGE_DIR
from src.shared.services import AppService

class LoadSlotTempProfile(AppService):
    def __init__(self, repository, remote_connect, control_carga_repo):
        self.repository = repository
        self.remote_connect = remote_connect
        self.control_carga_repo = control_carga_repo
        self.storage_dir = STORAGE_DIR+'U2000_SLOT_TEMP/'
        self.proyect_carga = 'fija.slot_temp_15min'

    def execute(self, fecha):
        start_time = datetime.datetime.now()
        try:
            print("Carga 'Slot Temperature Profile 15min'")
            str_fecha_dir = fecha.strftime('%Y%m%d')
            str_fecha_to_filter = 'PM_IG80336_15.*'+fecha.strftime('%Y%m%d%H%M')+'.*'
            fecha2 = fecha + datetime.timedelta(minutes=15)
            work_dir = '/opt/oss/server/var/neftpboot/ftproot/{}'.format(str_fecha_dir)

            print("{} - {}".format(fecha.strftime('%Y-%m-%d %H:%M'), fecha2.strftime('%Y-%m-%d %H:%M')))
            files_to_upload = self.remote_connect.get_files(work_dir, self.storage_dir, str_fecha_to_filter)
            self.__upload_files(fecha, fecha2, self.storage_dir, files_to_upload)
            for fichero in files_to_upload:
                os.unlink(self.storage_dir+fichero['file'])
        except Exception as e:
            end_time = datetime.datetime.now()
            self.control_carga_repo.save_carga(self.proyect_carga, '', 0, 0, start_time, end_time, 'ERROR', str(e), fecha)
            raise e

    def execute_hxh(self, fecha):
        print("Carga 'Slot Temperature Profile 15min' por hora")
        str_fecha_dir = fecha.strftime('%Y%m%d')
        str_fecha_to_filter = 'PM_IG80336_15.*'+fecha.strftime('%Y%m%d%H')+'.*'
        fecha2 = fecha + datetime.timedelta(hours=1)
        work_dir = '/opt/oss/server/var/neftpboot/ftproot/{}'.format(str_fecha_dir)

        print("{} - {}".format(fecha.strftime('%Y-%m-%d %H:%M'), fecha2.strftime('%Y-%m-%d %H:%M')))
        files_to_upload = self.remote_connect.get_files(work_dir, self.storage_dir, str_fecha_to_filter)
        self.__upload_files(fecha, fecha2, self.storage_dir, files_to_upload)
        for fichero in files_to_upload:
            os.unlink(self.storage_dir+fichero['file'])

    def __upload_files(self, fecha1, fecha2, local_dir, files_to_upload):
        def insert_handler(registros_to_insert, fichero, start_time, end_time):
            self.repository.insert_from_array(registros_to_insert)
            counter = len(registros_to_insert)
            self.control_carga_repo.save_carga(self.proyect_carga, fichero['updated']+'|'+fichero['file'], counter, counter, start_time, end_time, 'CARGADO', '', fecha1)

        self.upload_files(fecha1, fecha2, local_dir, files_to_upload, self.repository.delete_where_collectiontime_between, insert_handler, 2)

    def event_handler_hxh(self, event):
        self.__guard(event)
        
        fecha = datetime.datetime.strptime(event['msg_body']['fec_ini'], '%Y-%m-%d %H')
        self.execute_hxh(fecha)

    def event_handler(self, event):
        self.__guard(event)
        fecha = datetime.datetime.strptime(event['msg_body']['fec_ini'], '%Y-%m-%d %H:%M')
        self.execute(fecha)

    def __guard(self, event):
        if 'fec_ini' not in event['msg_body'].keys():
            raise QueueBadArguments("Error no se encontro el atributo 'fec_ini'")
    