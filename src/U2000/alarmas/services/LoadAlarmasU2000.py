import os
import csv
import datetime
from src.shared.config import STORAGE_DIR
import pytz

class LoadAlarmasU2000:
    def __init__(self, repository, remote_connect, control_carga_repo):
        self.repository = repository
        self.remote_connect = remote_connect
        self.control_carga_repo = control_carga_repo
        self.storage_dir = STORAGE_DIR+'U2000/'
        self.proyect_carga = 'fija.alarm_5min'
        self.tzone = pytz.timezone("America/Lima")
    
    def execute(self, fecha):
        print("Carga Alarmas")
        str_fecha = fecha.strftime('%Y%m%d%H%M')

        sftp = self.remote_connect.getReference().open_sftp()
        work_dir = '/opt/oss/server/var/neftpboot/ftproot/{}'.format(fecha.strftime('%Y%m%d'))
        try:
            sftp.chdir(work_dir)
            archivos = sftp.listdir(work_dir)
        except Exception as e:
            raise Exception("El direcotrio {} no existe".format(work_dir))
        # archivos = sftp.listdir_attr('/opt/oss/server/var/neftpboot/ftproot/20220113')
        archivos = self.get_files_of(work_dir, 'alarm-log-auto-1')
        files_to_upload = []
        for archivo in archivos:
            # if re.search("202201130000*alarm-log-auto-1", archivo):
            if str_fecha in archivo['file'] and 'alarm-log-auto-1' in archivo['file']:
                try:
                    sftp.get(archivo['file'], self.storage_dir+archivo['file'])
                    files_to_upload.append(archivo)
                    print(archivo)
                except Exception as e:
                    print("Fallo al intentar copiar {} a {}. Tal vez es un directorio.".format(archivo['file'], self.storage_dir+archivo['file']))
        sftp.close()

        # with os.scandir(self.storage_dir) as ficheros:
        for fichero in files_to_upload:
            # if str_fecha in fichero.name:
            # print(fichero.name)
            start_time = datetime.datetime.now()
            with open(self.storage_dir+fichero['file'], newline='') as csvfile:
                counter = 0
                # reader = csv.DictReader(csvfile)
                reader = csv.reader(csvfile)
                
                registros_to_insert = []
                counter = -1
                for row in reader:
                    counter = counter + 1
                    if counter == 0:
                        continue
                    row.append(str_fecha)
                    if (not row[12] is None) and (row[12] != ''):
                        row[12] = self.get_strlocaltime_from_strgmt(row[12])
                    if (not row[14] is None) and (row[14] != ''):
                        row[14] = self.get_strlocaltime_from_strgmt(row[14])
                    if (not row[28] is None) and (row[28] != ''):
                        row[28] = self.get_strlocaltime_from_strgmt(row[28])
                    registros_to_insert.append(row)
                
                print(counter)
                end_time = datetime.datetime.now()
                self.repository.delete_where_collectiontime(fecha)
                self.repository.insert_from_list(registros_to_insert)
                self.control_carga_repo.save_carga(self.proyect_carga, fichero['updated']+'|'+fichero['file'], counter, counter, start_time, end_time, 'CARGADO', '', fecha)
        
        for fichero in files_to_upload:
            os.unlink(self.storage_dir+fichero['file'])

    def get_strlocaltime_from_strgmt(self, str_gmt_date):
        # 2022/1/12 23:55:08 GMT-05:00
        # tzone = pytz.timezone("America/Lima")
        fecha = datetime.datetime.strptime(str_gmt_date, '%Y/%m/%d %H:%M:%S %Z%z')
        str_localdate = fecha.replace(tzinfo=pytz.utc).astimezone(self.tzone).strftime('%Y/%m/%d %H:%M:%S')
        return str_localdate
        
    def execute_hxh(self, fecha):
        print("Carga Alarmas por hora")
        str_fecha_dir = fecha.strftime('%Y%m%d')
        str_fecha_to_filter = fecha.strftime('%Y%m%d%H')
        fecha2 = fecha + datetime.timedelta(hours=1)
        # inicia carga
        print("{} - {}".format(fecha.strftime('%Y-%m-%d %H:%M'), fecha2.strftime('%Y-%m-%d %H:%M')))
        files_to_upload = self.__get_files_to_upload(str_fecha_to_filter, str_fecha_dir)
        self.__upload_files(fecha, fecha2, files_to_upload)
        for fichero in files_to_upload:
            os.unlink(self.storage_dir+fichero)
    
    def __get_files_to_upload(self, str_fecha_to_filter, str_fecha_dir):
        sftp = self.remote_connect.getReference().open_sftp()
        work_dir = '/opt/oss/server/var/neftpboot/ftproot/{}'.format(str_fecha_dir)
        try:
            sftp.chdir(work_dir)
            archivos = sftp.listdir(work_dir)
        except Exception as e:
            raise Exception("El directorio {} no existe".format(work_dir))
        # archivos = sftp.listdir_attr('/opt/oss/server/var/neftpboot/ftproot/20220113')
        files_to_upload = []
        for archivo in archivos:
            # if re.search("202201130000*alarm-log-auto-1", archivo):
            if str_fecha_to_filter in archivo and 'alarm-log-auto-1' in archivo:
                try:
                    sftp.get(archivo, self.storage_dir+archivo)
                    files_to_upload.append(archivo)
                    print(archivo)
                except Exception as e:
                    print("Fallo al intentar copiar {} a {}. Tal vez es un directorio.".format(archivo, self.storage_dir+archivo))
        sftp.close()
        return files_to_upload

    def __upload_files(self, fecha1, fecha2, files_to_upload):
        if len(files_to_upload) == 0:
            raise Exception("No hay archivos para procesar")
        # no incluye la ultima fecha
        self.repository.delete_where_collectiontime_between(fecha1, fecha2)
        main_counter = 0
        for fichero in files_to_upload:
            # if str_fecha in fichero.name:
            # print(fichero.name)
            with open(self.storage_dir+fichero, newline='') as csvfile:
                # reader = csv.DictReader(csvfile)
                reader = csv.reader(csvfile)
                
                registros_to_insert = []
                counter = -1
                for row in reader:
                    counter = counter + 1
                    if counter == 0:
                        continue
                    main_counter = main_counter + 1

                    # etrae collectiontime del nombre del archivo
                    row.append(fichero[0:12])
                    if not row[12] is None:
                        row[12] = row[12][0: len(row[12])-9 ]
                    if not row[14] is None:
                        row[14] = row[14][0: len(row[14])-9 ]
                    if not row[28] is None:
                        row[28] = row[28][0: len(row[28])-9 ]
                    registros_to_insert.append(row)
                
                self.repository.insert_from_list(registros_to_insert)
        print("{} registros insertados".format(main_counter))
    
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



"""with open(STORAGE_DIR+'files/carga_u2000/20220113000009-alarm-log-auto-1.csv', newline='') as csvfile:
    counter = 0
    # reader = csv.DictReader(csvfile)
    reader = csv.reader(csvfile)
    
    registros_to_insert = []
    counter = 0
    for row in reader:
        if counter == 0:
            continue
        registros_to_insert.append(row)
        # counter
    
    # print(registros_to_insert[0])
    self.repository.insert_from_list(registros_to_insert)
"""
                


