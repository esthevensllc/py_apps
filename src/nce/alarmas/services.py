from src.shared.config import STORAGE_DIR, BASE_DIR, DTFORMAT_BY_ALIAS, TDINTERVAL_BY_ALIAS
import datetime as dt
import os
import csv
import re
import cx_Oracle
# from src.apic.shared.services import BaseApicService
from zipfile import ZipFile

class LoadNCEDataFromConfig:
    def __init__(self, db, repository, sftp_service, control_carga_repo):
        self.db = db
        self.repository = repository
        self.sftp_service = sftp_service
        self.control_carga_repo = control_carga_repo
        self.base_storage_dir = STORAGE_DIR+'NCE2'

    def execute(self, config_id, dt_fecha1, dt_fecha2):
        # config_id = '1'
        # dt_fecha1 = dt.datetime.strptime('2023-03-15 11:50', '%Y-%m-%d %H:%M')
        # dt_fecha2 = dt.datetime.strptime('2023-03-15 11:51', '%Y-%m-%d %H:%M')

        start_time = dt.datetime.now()

        # base guards
        config = self.repository.find(config_id)
        if config is None:
            raise Exception(f"La configuración '{config_id}' no existe")
        if config["status"] != 1:
            raise Exception(f"La configuración '{config_id}' no esta activa")
        fields_config = self.repository.get_fields_by_id(config_id)
        if len(fields_config) == 0:
            raise Exception(f"La configuración '{config_id}' no tiene campos activos")

        print(config['name'])
        print(f"{dt_fecha1} - {dt_fecha2}")
        skip_lines=1

        self.sftp_service.useConnection(config['server_id'])
        self.sftp_service.connect()

        # validate work dir
        if not os.path.exists(self.base_storage_dir):
            os.makedirs(self.base_storage_dir)
            if not os.path.exists(self.base_storage_dir):
                raise Exception(f"El directorio base de trabajo {self.base_storage_dir} no se pudo crear y no existe")

        storage_dir = f"{self.base_storage_dir}/{dt_fecha1.strftime('%Y%m%d%H%M')}_{start_time.strftime('%f')}"
        os.makedirs(storage_dir)
        if not os.path.exists(storage_dir):
            raise Exception(f"El directorio de trabajo {storage_dir} no se pudo crear y no existe")

        # get files
        p = re.compile(".*date.*")
        files = []
        if p.match(config['work_dir']):
            dt_fecha_recorrido = dt_fecha1
            while dt_fecha_recorrido < dt_fecha2:
                str_date = dt_fecha_recorrido.strftime("%Y%m%d")
                date_work_dir = config['work_dir'].format(date=str_date)
                # files_of_date = self.sftp_service.get_files(date_work_dir, storage_dir, config['file_pattern'])
                files_of_date = self._get_files_from_server(config, date_work_dir, storage_dir, dt_fecha1, dt_fecha2)
                files += files_of_date
                dt_fecha_recorrido = dt_fecha_recorrido + dt.timedelta(days=1)
        else:
            files = self.sftp_service.get_files(config['work_dir'], storage_dir, config['file_pattern'])

        if len(files) == 0:
            raise Exception(f"No se encontro archivos para '{config['name']}' con el filtro '{config['file_pattern']}'")
        
        # main files
        files_by_parent = {}
        for row in files:
            files_by_parent[row["file"]] = None

        # unzip files
        for localfile in files_by_parent:
            zf = ZipFile(f'{storage_dir}/{localfile}', 'r')
            zf.extractall(storage_dir)
            files_by_parent[localfile] = zf.namelist()
            zf.close()
            os.unlink(f"{storage_dir}/{localfile}")
        
        data = []
        counter_by_files = []
        for localfile in list(files_by_parent):
            date_of_file = self._get_date_from_filename(config, localfile)
            counter = 0
            subfiles = [localfile] if files_by_parent[localfile] is None else files_by_parent[localfile]
            for subfile in subfiles:
                str_filedate = date_of_file.strftime('%Y-%m-%d %H:%M')+":00"
                str_filedate_day = date_of_file.strftime('%Y-%m-%d')+" 00:00:00"
                envlist = {
                    'str_filedate': str_filedate,
                    'str_filedate_day': str_filedate_day,
                    'filename': localfile
                }
                data_to_add = self._get_data_from_csv(fields_config, f"{storage_dir}/{subfile}", skip_lines, env=envlist)
                counter += len(data_to_add)
                data = data + data_to_add
            counter_by_files.append({'file': localfile, 'count': counter})

        is_succesfull = False
        try:
            self._reload_data_by_fdate(config, fields_config, dt_fecha1, dt_fecha2, data)
            is_succesfull = True
        except BaseException as e:
            error = e
        except:
            is_succesfull = False

        for localfile in list(files_by_parent):
            subfiles = [localfile] if files_by_parent[localfile] is None else files_by_parent[localfile]
            for subfile in subfiles:
                os.unlink(f"{storage_dir}/{subfile}")
        os.rmdir(storage_dir)
        end_time = dt.datetime.now()

        pattern = re.compile(config["file_pattern"])
        for row in counter_by_files:
            str_date = pattern.search(row['file']).group(1)
            date = dt.datetime.strptime(str_date, config['file_date_format'])
            date = dt.datetime.strptime(date.strftime('%Y%m%d%H%M'), '%Y%m%d%H%M')
            # file = row['file']
            self.control_carga_repo.save_carga(
                config['queue_id'],
                row['file'],
                row['count'] if is_succesfull == True else 0,
                row['count'],
                start_time,
                end_time,
                'CARGADO' if is_succesfull == True else 'ERROR',
                '',
                date
            )
        
        # envio de error
        if is_succesfull == False:
            if error is not None:
                raise error
            else:
                raise Exception("Ocurrio un error no identificado al realizar la carga")

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        sftp = self.sftp_service.getReference()
        try:
            sftp.chdir(remote_dir)
        except Exception as e:
            print(e)
            raise Exception(f"El directorio {remote_dir} no existe")
        #files_of_date = self.sftp_service.get_files(remote_dir, storage_dir, str_pattern)
        pattern = re.compile(config['file_pattern'])
        files = self.sftp_service.get_filename_and_updated_at(remote_dir, config['file_pattern'])
        files_filtered = []
        for row in files:
            str_date = pattern.search(row['file']).group(1)
            date_of_file = dt.datetime.strptime(str_date, config['file_date_format'])
            if dt_fecha1 <= date_of_file and date_of_file < dt_fecha2:
                files_filtered.append(row)

        files_to_upload = []
        for file in files_filtered:
            filename = file['file']
            path_filename = f"{storage_dir}/{filename}"
            try:
                sftp.get(filename, path_filename)
                files_to_upload.append(file)
                #print(filename)
            except Exception as e:
                raise Exception(f"Fallo al intentar copiar {filename} a {path_filename}. Tal vez es un directorio.")
        return files_to_upload

    def _get_data_from_csv(self, fields_config, filename, skip_lines=0, date_of_file=None, env={}):
        data = []

        with open(f"{filename}", newline='', encoding='UTF-8') as csvfile:
            reader = csv.reader(csvfile)
            counter = 0 - skip_lines
            for row in reader:
                counter += 1
                if counter <=0:
                    continue
                row_to_add = {}
                for field in fields_config:
                    value = None
                    try:
                        value = row[int(field["src_fieldname"])]
                        if field['map_with'] is not None:
                            value = eval(f"f\"{field['map_with']}\"")
                        if value == '':
                            value = None
                        row_to_add[field["fieldname"]] = value
                    except BaseException as e:
                        print(f"line: {counter}, field: {field['fieldname']}, value: '{value}'")
                        raise e
                data.append(row_to_add)
        return data

    def _get_date_from_filename(self, config, file):
        pattern = re.compile(config['file_pattern'])
        str_date = pattern.search(file).group(1)
        date = dt.datetime.strptime(str_date, config['file_date_format'])
        return dt.datetime.strptime(date.strftime('%Y%m%d%H%M'), '%Y%m%d%H%M')

    def get_insert_template_and_bindings(self, table, fields_config):
        str_fields = []
        str_binds = []
        bindings = {}
        for field in fields_config:
            # field = cvffields_by_fieldconfig[csvfield]
            if field is not None:
                str_fields.append(field['fieldname'])
                cx_oracle_type = None
                if field['type'] == 'number':
                    str_binds.append(f":{field['fieldname']}")
                    cx_oracle_type = cx_Oracle.NUMBER
                elif field['type'] == 'varchar2':
                    str_binds.append(f":{field['fieldname']}")
                    cx_oracle_type = cx_Oracle.STRING
                elif field['type'] == 'date':
                    str_binds.append(f"TO_DATE(:{field['fieldname']}, 'YYYY-MM-DD HH24:MI:SS')")
                    cx_oracle_type = cx_Oracle.STRING
                else:
                    raise Exception(f"El field {field['fieldname']} tiene un tipo de dato '{field['type']}' que no existe")
                bindings[field['fieldname']] = cx_oracle_type

        template = f"INSERT INTO {table}({', '.join(str_fields)}) VALUES ({', '.join(str_binds)})"
        return template, bindings

    def _reload_data_by_fdate(self, config, fields_config, dt_fecha1, dt_fecha2, registros, env={}):
        fields_to_reload = list(filter(lambda f: f['to_reload'] is not None, fields_config))
        str_fecha1 = dt_fecha1.strftime('%Y-%m-%d %H:%M:%S')
        str_fecha2 = dt_fecha2.strftime('%Y-%m-%d %H:%M:%S')

        str_where = []
        is_delimited = False
        for field in fields_to_reload:
            if field["type"].lower() == "date":
                is_delimited = True
                str_where.append(f"TO_DATE('{str_fecha1}', 'yyyy-mm-dd hh24:mi:ss') <= {field['fieldname']} AND {field['fieldname']} < TO_DATE('{str_fecha2}', 'yyyy-mm-dd hh24:mi:ss')")
            elif field["type"].lower() == "number":
                str_where.append(f"{field['fieldname']} = {field['reload_argument'].format(**env)}")
            else:
                str_where.append(f"{field['fieldname']} = '{field['reload_argument'].format(**env)}'")

        if not is_delimited:
            raise Exception(f"La carga no esta delimitada por un campo de fecha")

        print(f"realod by ({list(map(lambda r: r['fieldname'], fields_to_reload))})")

        delete_template = f"DELETE FROM {config['tablename']} WHERE "+(' AND '.join(str_where))
        # print(delete_template)
        self.db.query(delete_template)

        insert_template, bindings = self.get_insert_template_and_bindings(config['tablename'], fields_config)
        insert_config = {'template': insert_template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': config['limit_to_commit']}
        self.db.save_from_array2(insert_config, registros)
        print(f"data: {len(registros)}")

    def event_handler(self, event):
        self.__guard(event)
        date_format = DTFORMAT_BY_ALIAS[event['msg_body']['format']]
        queue_id = event['queue_id']
        config_id = event['msg_body']['config_id']
        fecha1 = dt.datetime.strptime(event['msg_body']['fec_ini'], date_format)
        fecha2 = None
        if 'fec_fin' in event['msg_body'].keys():
            fecha2 = dt.datetime.strptime(event['msg_body']['fec_fin'], date_format)
        else:
            fecha2 = fecha1 + dt.timedelta(**TDINTERVAL_BY_ALIAS[event['msg_body']['format']])

        self.execute(config_id, fecha1, fecha2)

    def __guard(self, event):
        msg_body_keys = event['msg_body'].keys()
        if 'config_id' not in msg_body_keys or ('fec_ini' not in msg_body_keys) or ('format' not in msg_body_keys):
            raise Exception("Error no se encontro el atributo 'mediciones', 'fec_ini' o 'format'")

        if type(event['msg_body']['config_id']) != type(''):
            raise Exception("El config_id deven ser una cadena")

        if event['msg_body']['format'] not in list(DTFORMAT_BY_ALIAS):
            raise Exception(f"Formato '{event['msg_body']['format']}' no valido")


import json

class NCEEventProducer:
    def __init__(self, repository, sftp_service, control_carga_repo, queue_service):
        self.repository = repository
        self.sftp_service = sftp_service
        self.control_carga_repo = control_carga_repo
        self.queue_service = queue_service
        self.since = dt.datetime.now()
        self.time_ago_delta = {'days': 2}
        self.time_ago = self.since - dt.timedelta(**self.time_ago_delta)
    
    def execute(self):
        nce_cargas = self.repository.get()
        for row in nce_cargas:
            self._produce_events_to(row)

    def _produce_events_to(self, config):
        self.dt_fecha2 = dt.datetime.now()
        self.dt_fecha1 = self.since - dt.timedelta(**self.time_ago_delta)
        print(f"[{config['name']}]: {self.since} - {self.time_ago}")

        self.sftp_service.useConnection(config['server_id'])
        self.sftp_service.connect()

        p = re.compile(".*date.*")
        files = []
        if p.match(config['work_dir']):
            dt_fecha_recorrido = self.dt_fecha1
            while dt_fecha_recorrido < self.dt_fecha2:
                str_date = dt_fecha_recorrido.strftime("%Y%m%d")
                date_work_dir = config['work_dir'].format(date=str_date)
                files_of_date = self._get_files_from_server(config, date_work_dir, None, self.dt_fecha1, self.dt_fecha2)
                files += files_of_date
                dt_fecha_recorrido = dt_fecha_recorrido + dt.timedelta(days=1)
        else:
            files = self.sftp_service.get_files(config['work_dir'], None, config['file_pattern'])

        # add file date
        pattern = re.compile(config['file_pattern'])
        for index in range(len(files)):
            str_date = pattern.search(files[index]['file']).group(1)
            files[index]['filedate'] = dt.datetime.strptime(str_date, config['file_date_format'])

        controlfiles_by_filename = self._get_controlfiles_by_filename(config["queue_id"], self.dt_fecha1, self.dt_fecha2)

        print(f"server_files: {len(files)}")
        print(f"control_files: {len(controlfiles_by_filename)}")
        events = self._get_event_to_insert(config, files, controlfiles_by_filename)
        print(f"new events: {len(events)}")

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        sftp = self.sftp_service.getReference()
        try:
            sftp.chdir(remote_dir)
        except Exception as e:
            print(e)
            raise Exception(f"El directorio {remote_dir} no existe")
        
        pattern = re.compile(config['file_pattern'])
        files = self.sftp_service.get_filename_and_updated_at(remote_dir, config['file_pattern'])
        files_filtered = []
        for row in files:
            str_date = pattern.search(row['file']).group(1)
            date_of_file = dt.datetime.strptime(str_date, config['file_date_format'])
            if dt_fecha1 <= date_of_file and date_of_file < dt_fecha2:
                files_filtered.append(row)

        return files_filtered

    def _get_controlfiles_by_filename(self, queue_id, dt_fecha1, dt_fecha2):
        files_of_control = self.control_carga_repo.getOfProyectWhereFechaArchivo(queue_id, dt_fecha1, dt_fecha2)
        files_by_filename = {}
        for file in files_of_control:
            files_by_filename[file["archivo"]] = file
        return files_by_filename

    def _get_event_to_insert(self, config, server_files, control_files_by_filename):
        events = []
        for row in server_files:
            str_filedate = row['filedate'].strftime('%Y-%m-%d %H:%M')
            event_inserted = self.queue_service.findByQueueIdAndEstadoAndMsg(config["queue_id"], 0, f"%{str_filedate}%")

            if control_files_by_filename.get(row['file']) is None:
                if event_inserted is None:
                    events.append({'file': row['file'], 'filedate': str_filedate})
                    self.create_event(config["queue_id"], row['filedate'])
            else:
                cfile = control_files_by_filename[row['file']]
                if cfile['estado'].upper() != 'CARGADO':
                    if event_inserted is None:
                        events.append({'file': row['file'], 'filedate': str_filedate})
                        self.create_event(config["queue_id"], row['filedate'])
        return events

    def create_event(self, queue_id, filedate):
        msg_body = json.dumps({'fec_ini': filedate.strftime('%Y-%m-%d %H:%M'), 'format': 'mxm'})
        self.queue_service.createEvent({'queue_id': queue_id, 'msg_body': msg_body})



from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.nce.shared.services import (LOAD_NCE_FROM_CONFIG)

class NCEEventConsumerFromConfig(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, repository, notification_service):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.1
        self.repository = repository
        self.medicion_by_queue = {}
        self.loop = False

        self.nce_configs = {}
        nce_cargas = self.repository.get()
        for row in nce_cargas:
            self.nce_configs[row["queue_id"]] = row

        def map_event(event):
            event['msg_body']['config_id'] = self.nce_configs[event['queue_id']]["id"]
            return event

        for row in nce_cargas:
            queue_id = row["queue_id"]
            self.queue_handlers[queue_id] = {'handler': LOAD_NCE_FROM_CONFIG, 'callback': lambda s, e: s.event_handler(map_event(e))}
            # self.medicion_by_queue[queue_id] = med_gran

        self.queue_ids = list(self.queue_handlers)



    