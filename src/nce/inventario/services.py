from src.shared.config import STORAGE_DIR, BASE_DIR, DTFORMAT_BY_ALIAS, TDINTERVAL_BY_ALIAS
import os
import re
import csv
import json
import stat
import datetime as dt
from shutil import rmtree
import cx_Oracle

from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.nce.shared.services import (LOAD_NCE_INVENTARIO_FROM_CONFIG)

class LoadNCEInventarioFromConfig:
    def __init__(self, db, repository, sftp_service, control_carga_repo):
        self.db = db
        self.repository = repository
        self.sftp_service = sftp_service
        self.control_carga_repo = control_carga_repo
        self.base_storage_dir = STORAGE_DIR+'nce_inventario'

    def execute(self, config_id, dt_fecha):
        dt_fecha.replace(hour=0, minute=0, second=0)
        start_time = dt.datetime.now()

        # base guards
        config = self.repository.find(config_id)
        if config is None:
            raise Exception(f"La configuración '{config_id}' no existe")
        if config["status"] != 1:
            raise Exception(f"La configuración '{config_id}' no esta activa")
        # if config["reload_by"] not in ("all", "file"):
        # raise Exception(f"La configuración reload_by '{config['reload_by']}' no es valida")

        print(config["name"])
        
        fields_config = self.repository.get_fields_by_id(config_id)
        if len(fields_config) == 0:
            raise Exception(f"La configuración '{config_id}' no tiene campos activos")

        self.sftp_service.useConnection(config['server_id'])
        self.sftp_service.connect()
        
        # validate work dir
        if not os.path.exists(self.base_storage_dir):
            os.makedirs(self.base_storage_dir)
            if not os.path.exists(self.base_storage_dir):
                raise Exception(f"El directorio base de trabajo {self.base_storage_dir} no se pudo crear y no existe")
        
        storage_dir = f"{self.base_storage_dir}/{dt_fecha.strftime('%Y%m%d')}_{start_time.strftime('%f')}"
        os.makedirs(storage_dir)
        if not os.path.exists(storage_dir):
            raise Exception(f"El directorio de trabajo {storage_dir} no se pudo crear y no existe")

        files = self._get_files_from_server(config, config["work_dir"], dt_fecha)

        counter_by_files = {}
        is_succesfull = False
        error = None

        try:
            if len(files) == 0:
                raise Exception("No se encontraron archivos para procesar")
            self._download_files(storage_dir, files)
            data = []
            for row in files:
                data_of_csv = self._get_data_from_csv(f"{storage_dir}/{row['file']}", skip_lines=10)
                data = data + data_of_csv
                counter_by_files[row['file']] = len(data_of_csv)

            self.load_table(config['tablename'], fields_config, data)

            if config["exec_after_st"] is not None:
                envlist = dict(**config)
                envlist["str_filedate"] = dt_fecha.strftime("%Y-%m-%d %H:%M:%S")
                to_execute = config['exec_after_st'].format(**envlist)
                self.db.callproc(to_execute, {})
                print(to_execute)

            is_succesfull = True
        except BaseException as e:
            error = e
        except:
            error = Exception("Ocurrio un error no identificado al realizar la carga")
        
        rmtree(storage_dir)
        end_time = dt.datetime.now()

        print(counter_by_files)
        for row in files:
            count_of_file = counter_by_files.get(row['file'])
            if count_of_file is None:
                count_of_file = 0
            self.control_carga_repo.save_carga(
                config['queue_id'],
                row['file'],
                count_of_file if is_succesfull == True else 0,
                count_of_file,
                start_time,
                end_time,
                'CARGADO' if is_succesfull == True else 'ERROR',
                str(error) if error is not None else None,
                dt_fecha
            )

        if is_succesfull == False:
            raise error

    def _get_files_from_server(self, config, remote_dir, dt_fecha):
        pattern = re.compile(config['file_pattern'])
        files = self.sftp_service.get_filename_and_updated_at(config['work_dir'], config['file_pattern'])
        files_filtered = []
        for row in files:
            str_date = pattern.search(row['file']).group(1)
            date_of_file = dt.datetime.strptime(str_date, config['file_date_format'])
            if dt_fecha == date_of_file:
                files_filtered.append(row)
        return files_filtered


    def _download_files(self, storage_dir, files_filtered):
        sftp = self.sftp_service.getReference()
        for file in files_filtered:
            filename = file['file']
            local_path_filename = f"{storage_dir}/{filename}"
            try:
                sftp.get(f"{file['path']}/{filename}", local_path_filename)
                #print(filename)
            except Exception as e:
                raise e

    def _get_data_from_csv(self, filename, skip_lines=0):
        with open(filename, mode="r", encoding='UTF-8') as csv_file:
            loaded_csv = csv.reader(csv_file, delimiter=",")
            final_data=[]
    
            for row in loaded_csv:
                final_data.append(row) 
            del final_data[0:skip_lines]
            return final_data
        return []

    def load_table(self, table, fields_config, data):
        query = f'DELETE FROM {table}_TEMP'
        self.db.query(query)
        
        template, bindings = self.get_insert_template_and_bindings(f"{table}_TEMP", fields_config)

        insert_config = {
            'template': template,
            'bindings': bindings,
            'row_type': 'array',
            'limit_to_commit': 10000
        }
        self.db.save_from_array2(insert_config, data)

        unique_fields = list(filter(lambda r: r["is_unique"] == 1, fields_config))
        not_unique_fields = list(filter(lambda r: r["is_unique"] != 1, fields_config))

        str_pk_fields = " AND ".join(list(map(lambda r: f"A.{r['fieldname']} = B.{r['fieldname']}", unique_fields)))
        str_update_fields = ", ".join(list(map(lambda r: f"A.{r['fieldname']} = B.{r['fieldname']}", not_unique_fields)))
        str_all_fields = ", ".join(list(map(lambda r: r['fieldname'], fields_config)))
        str_all_fields_bind = ", ".join(list(map(lambda r: f"b.{r['fieldname']}", fields_config)))

        sql_merge = f"""MERGE INTO {table} A
        USING (
            SELECT * FROM {table}_TEMP
        ) B ON ({str_pk_fields})
        WHEN MATCHED THEN UPDATE SET
            {str_update_fields},
            A.FECHA_ACTUALIZACION = TRUNC(SYSDATE, 'DD'),
            A.ESTADO_SEG = 1
        WHEN NOT MATCHED THEN INSERT({str_all_fields}, fecha_insercion, estado_seg)
            VALUES ({str_all_fields_bind}, TRUNC(SYSDATE, 'DD'), 1)
        """
        print(sql_merge)

        self.db.query(f"""BEGIN
            UPDATE {table} SET ESTADO_SEG = 0;
            COMMIT;

            {sql_merge};
            COMMIT;
        END;""")

    def get_insert_template_and_bindings(self, table, fields_config):
        str_fields = []
        str_binds = []
        bindings = []
        for field in fields_config:
            # field = cvffields_by_fieldconfig[csvfield]
            if field is not None:
                str_fields.append(field['fieldname'])
                cx_oracle_type = None
                if field['type'] == 'number':
                    str_binds.append(f":{field['src_fieldname']}")
                    cx_oracle_type = cx_Oracle.NUMBER
                elif field['type'] == 'varchar2':
                    str_binds.append(f":{field['src_fieldname']}")
                    cx_oracle_type = cx_Oracle.STRING
                elif field['type'] == 'date':
                    str_binds.append(f"TO_DATE(:{field['src_fieldname']}, 'YYYY-MM-DD HH24:MI:SS')")
                    cx_oracle_type = cx_Oracle.STRING
                else:
                    raise Exception(f"El field {field['fieldname']} tiene un tipo de dato '{field['type']}' que no existe")
                bindings.append(cx_oracle_type)

        template = f"INSERT INTO {table}({', '.join(str_fields)}) VALUES ({', '.join(str_binds)})"
        return template, bindings

    def event_handler(self, event):
        self.__guard(event)
        config_id = event['msg_body']['config_id']
        fecha = dt.datetime.strptime(event['msg_body']['fec_ini'], DTFORMAT_BY_ALIAS["dxd"])
        self.execute(config_id, fecha)

    def __guard(self, event):
        msg_body_keys = event['msg_body'].keys()
        if 'config_id' not in msg_body_keys or ('fec_ini' not in msg_body_keys):
            raise Exception("Error no se encontro el atributo 'fec_ini' o 'format'")

            

class NCEInventarioEventProducer:
    def __init__(self, repository, sftp_service, control_carga_repo, queue_service):
        self.repository = repository
        self.sftp_service = sftp_service
        self.control_carga_repo = control_carga_repo
        self.queue_service = queue_service
        self.time_ago_delta = {}
    
    def execute(self):
        nce_cargas = self.repository.get()
        if len(nce_cargas) == 0:
            raise Exception(f"No existen cargas")

        for row in nce_cargas:
            self._produce_events_to(row)
            print("")

    def _produce_events_to(self, config):
        self.time_ago_delta = json.loads(config["search_time_ago"])
        self.dt_fecha2 = dt.datetime.now()
        self.dt_fecha1 = self.dt_fecha2 - dt.timedelta(**self.time_ago_delta)
        print(f"[{config['name']}]: {self.dt_fecha2.strftime('%Y-%m-%d %H:%M:%S')} - {self.dt_fecha1.strftime('%Y-%m-%d %H:%M:%S')}")

        self.sftp_service.useConnection(config['server_id'])
        self.sftp_service.connect()

        p = re.compile(".*date.*")
        files = []
        files = self._get_files_from_server(config, config["work_dir"], None, self.dt_fecha1, self.dt_fecha2)

        # filter files whithout permission
        files = self._get_files_with_access(files, config['files_permission'])

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

    def _get_files_with_access(self, files, files_permission):
        files_filtered = []
        pattern = re.compile("\-r..r..r..")
        if files_permission == "owner":
            pattern = re.compile("\-r........")
        elif files_permission == "group":
            pattern = re.compile("\-r..r.....")

        print("files_filtered")
        for row in files:
            filemode = stat.filemode(row["st_mode"])
            if pattern.match(filemode) is not None:
                files_filtered.append(row)
            else:
                print({"file": row["file"], "filemode": filemode})
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
            str_filedate = row['filedate'].strftime('%Y-%m-%d')
            event_inserted = self.queue_service.findByQueueIdAndEstadoAndMsg(config["queue_id"], 0, f"%{str_filedate}%")

            if control_files_by_filename.get(row['file']) is None:
                if event_inserted is None:
                    events.append({'file': row['file'], 'filedate': str_filedate})
                    self.create_event(config["queue_id"], row['filedate'])
                    # print({'file': row['file'], 'filedate': str_filedate})
            else:
                cfile = control_files_by_filename[row['file']]
                if cfile['estado'].upper() != 'CARGADO':
                    if event_inserted is None:
                        events.append({'file': row['file'], 'filedate': str_filedate})
                        self.create_event(config["queue_id"], row['filedate'])
                        # print({'file': row['file'], 'filedate': str_filedate})
        return events

    def create_event(self, queue_id, filedate):
        msg_body = json.dumps({'fec_ini': filedate.strftime('%Y-%m-%d')})
        self.queue_service.createEvent({'queue_id': queue_id, 'msg_body': msg_body})


class NCEInventarioEventConsumerFromConfig(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, repository, notification_service):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.1
        self.repository = repository
        self.loop = False
        self.nce_configs = {}

    def execute(self):
        nce_cargas = self.repository.get()
        if len(nce_cargas) == 0:
            raise Exception(f"No existen cargas")
        
        for row in nce_cargas:
            self.nce_configs[row["queue_id"]] = row

        def map_event(event):
            event['msg_body']['config_id'] = self.nce_configs[event['queue_id']]["id"]
            return event

        for row in nce_cargas:
            queue_id = row["queue_id"]
            self.queue_handlers[queue_id] = {'handler': LOAD_NCE_INVENTARIO_FROM_CONFIG, 'callback': lambda s, e: s.event_handler(map_event(e))}

        self.queue_ids = list(self.queue_handlers)

        super().execute()
