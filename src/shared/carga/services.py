import datetime as dt
import csv
import os
import re
import cx_Oracle
from zipfile import ZipFile
import gzip
from shutil import rmtree, copyfileobj
import stat
import json
from src.shared.config import DTFORMAT_BY_ALIAS, TDINTERVAL_BY_ALIAS

class BaseCargaFromConfig:
    def __init__(self, db, repository, sftp_service, control_carga_repo):
        self.db = db
        self.repository = repository
        self.sftp_service = sftp_service
        self.control_carga_repo = control_carga_repo
        self.base_storage_dir = None
        self.config = {}
        self.fields_config = []
        self.succesfull_state = 'CARGADO'
        self.error_state = 'ERROR'

    def execute(self, config_id, dt_fecha1, dt_fecha2):
        # dt_fecha2 = dt_fecha1 + dt.timedelta(days=1)
        # base guards
        config = self.repository.find(config_id)
        if config is None:
            raise Exception(f"La configuración '{config_id}' no existe")
        if config["status"] != 1:
            raise Exception(f"La configuración '{config_id}' no esta activa")
        if config["reload_by"] not in ("all", "file"):
            raise Exception(f"La configuración reload_by '{config['reload_by']}' no es valida")
        if config["exec_after_by"] not in (None,"all", "file"):
            raise Exception(f"La configuración exec_after_by '{config['exec_after_by']}' no es valida")
        if config["exec_after_by"] is not None and config['exec_after_st'] is None:
            raise Exception(f"La configuración exec_after_st '{config['exec_after_st']}' no es valida")
        if config.get("temp_table") is not None:
            if not config["temp_table"].endswith("temp"):
                raise Exception(f"La tabla temporal '{config['temp_table']}' no es valida")
        
        fields_config = self.repository.get_fields_by_id(config_id)
        if len(fields_config) == 0:
            raise Exception(f"La configuración '{config_id}' no tiene campos activos")

        self.config = config
        self.fields_config = fields_config

        print(config['name'])
        
        dt_fecha_recorrido = dt_fecha1
        while dt_fecha_recorrido < dt_fecha2:
            dt_next = dt_fecha_recorrido + dt.timedelta(**json.loads(config['loop_time']))
            if dt_next > dt_fecha2:
                dt_next = dt_fecha2
            self.execute_one(config_id, dt_fecha_recorrido, dt_next)
            dt_fecha_recorrido = dt_next

    def execute_one(self, config_id, dt_fecha1, dt_fecha2):
        start_time = dt.datetime.now()

        config = self.config
        fields_config = self.fields_config

        print(f"{dt_fecha1} - {dt_fecha2}")
        skip_lines= 1 if config.get("skip_lines") is None else config["skip_lines"]

        if config.get('server_id') is not None:
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
            wk_date_format = "%Y%m%d" if config.get("wk_date_format") is None else config["wk_date_format"]
            dt_fecha_recorrido = dt_fecha1
            while dt_fecha_recorrido < dt_fecha2:
                str_date = dt_fecha_recorrido.strftime(wk_date_format)
                date_work_dir = config['work_dir'].format(date=str_date)

                files_of_date = self._get_files_from_server(config, date_work_dir, dt_fecha1, dt_fecha2)
                files += files_of_date
                dt_fecha_recorrido = dt_fecha_recorrido + dt.timedelta(days=1)
        else:
            files = self._get_files_from_server(config, config['work_dir'], dt_fecha1, dt_fecha2)

        if len(files) == 0:
            raise Exception(f"No se encontro archivos para '{config['name']}' con el filtro '{config['file_pattern']}'")
        
        # main files
        files_by_parent = {}
        for row in files:
            files_by_parent[row["file"]] = None

        counter_by_files = {}
        is_succesfull = False
        error = None
        baseenvlist = {'filenames': [], 'tablename': config['tablename'], 'temp_table': config.get('temp_table')}
        envlist_by_file = {}
        try:
            # download files
            self._download_files(storage_dir, files)

            # unzip files
            file_steps = [] if config.get("steps") is None else config["steps"].split(",")
            print("steps:", file_steps)
            if "unzip" in file_steps:
                for localfile in list(files_by_parent):
                    zf = ZipFile(f'{storage_dir}/{localfile}', 'r')
                    zf.extractall(storage_dir)
                    files_by_parent[localfile] = zf.namelist()
                    zf.close()
                    os.unlink(f"{storage_dir}/{localfile}")

            if "ungzip" in file_steps:
                for localfile in list(files_by_parent):
                    subfilename = f"{localfile}".replace('.gz', '')
                    with gzip.open(f'{storage_dir}/{localfile}', 'rb') as zf, open(f'{storage_dir}/{subfilename}', 'wb') as subfile:
                        copyfileobj(zf, subfile)
                        files_by_parent[localfile] = [subfilename]
                    os.unlink(f"{storage_dir}/{localfile}")
            
            data = []
            data_by_file = {}
            for localfile in list(files_by_parent):
                date_of_file = self._get_date_from_filename(config, localfile)
                str_filedate = date_of_file.strftime('%Y-%m-%d %H:%M')+":00"
                str_filedate_day = date_of_file.strftime('%Y-%m-%d')+" 00:00:00"
                envlist = {
                    'str_filedate': str_filedate,
                    'str_filedate_day': str_filedate_day,
                    'filename': localfile
                }
                counter = 0
                data_by_file[localfile] = []
                subfiles = [localfile] if files_by_parent[localfile] is None else files_by_parent[localfile]
                for subfile in subfiles:
                    data_to_add = self._get_data_from_csv(fields_config, f"{storage_dir}/{subfile}", skip_lines, env=envlist)
                    counter = counter + self.count_data_from_source(data_to_add)
                    # data = data + data_to_add
                    data_by_file[localfile] = data_by_file[localfile] + data_to_add
                counter_by_files[localfile] = {'file': localfile, 'count': counter}
                envlist_by_file[localfile] = envlist
                baseenvlist["filenames"].append(localfile)
            
            if config["reload_by"] == "file":
                for localfile in list(files_by_parent):
                    envlist = envlist_by_file[localfile]
                    self._reload_data_by_fdate(config, fields_config, dt_fecha1, dt_fecha2, data_by_file[localfile], env=envlist)
            else:
                all_data = []
                for localfile in list(data_by_file):
                    all_data = all_data + data_by_file[localfile]
                
                self._reload_data_by_fdate(config, fields_config, dt_fecha1, dt_fecha2, all_data, env=baseenvlist)

            is_succesfull = True
        except BaseException as e:
            error = e
        except:
            is_succesfull = False

        # delete local work directory
        rmtree(storage_dir)

        end_time = dt.datetime.now()

        pattern = re.compile(config["file_pattern"])
        for row in files:
            count_of_file = 0
            if counter_by_files.get(row["file"]) is not None:
                count_of_file = counter_by_files[row["file"]]["count"]
            str_date = pattern.search(row['file']).group(1)
            date = dt.datetime.strptime(str_date, config['file_date_format'])
            date = dt.datetime.strptime(date.strftime('%Y%m%d%H%M'), '%Y%m%d%H%M')
            # file = row['file']
            self.control_carga_repo.save_carga(
                config['queue_id'],
                row['file'],
                count_of_file if is_succesfull == True else 0,
                count_of_file,
                start_time,
                end_time,
                self.succesfull_state if is_succesfull == True else self.error_state,
                '',
                date
            )

        if config['exec_after_by'] is not None and is_succesfull == True:
            if config['exec_after_by'] == "file":
                for row in files:
                    envlist = envlist_by_file[row['file']]
                    to_execute = config['exec_after_st'].format(**envlist)
                    self.db.query(to_execute)
            else:
                to_execute = config['exec_after_st'].format(**baseenvlist)
                self.db.query(to_execute)
        
        # envio de error
        if is_succesfull == False:
            if error is not None:
                raise error
            else:
                raise Exception("Ocurrio un error no identificado al realizar la carga")

    def _get_files_from_server(self, config, remote_dir, dt_fecha1, dt_fecha2):
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
                # raise Exception(f"Fallo al intentar copiar {filename} a {local_path_filename}. Tal vez es un directorio.")

    def _get_data_from_csv(self, fields_config, filename, skip_lines=0, date_of_file=None, env={}):
        data = []
        encoding = 'UTF-8' if self.config.get("file_encoding") is None else self.config["file_encoding"]
        with open(f"{filename}", newline='', encoding=encoding) as csvfile:
            file_delimiter = ',' if self.config.get("file_delimiter") is None else self.config["file_delimiter"]
            reader = csv.reader(csvfile, delimiter=file_delimiter)
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
                        if field.get('map_with') is not None:
                            value = eval(f"f\"{field['map_with']}\"")
                        if value == '':
                            value = None
                        row_to_add[field["fieldname"]] = value
                    except BaseException as e:
                        print(row)
                        print(f"line: {counter}, field: {field['fieldname']}, value: '{value}'")
                        raise e
                data.append(row_to_add)
        return data

    def count_data_from_source(self, registros):
        return len(registros)

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
                    date_format = 'YYYY-MM-DD HH24:MI:SS' if field.get("type_format") is None else field.get("type_format")
                    str_binds.append(f"TO_DATE(:{field['fieldname']}, '{date_format}')")
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
        reload_by = {}
        for field in fields_to_reload:
            if field["type"].lower() == "date":
                is_delimited = True
                str_where.append(f"TO_DATE('{str_fecha1}', 'yyyy-mm-dd hh24:mi:ss') <= {field['fieldname']} AND {field['fieldname']} < TO_DATE('{str_fecha2}', 'yyyy-mm-dd hh24:mi:ss')")
                reload_by[field['fieldname']] = [str_fecha1, str_fecha2]
            elif field["type"].lower() == "number":
                arg_value = field['reload_argument'].format(**env)
                if arg_value[0] == '[' and arg_value[-1] == "]":
                    array_values = arg_value[1:-1].split(", ")
                    str_where.append(f"{field['fieldname']} in ({','.join(array_values)})")
                else:
                    str_where.append(f"{field['fieldname']} = {field['reload_argument'].format(**env)}")
                reload_by[field['fieldname']] = arg_value
            else:
                arg_value = field['reload_argument'].format(**env)
                if arg_value[0] == '[' and arg_value[-1] == "]":
                    array_values = arg_value[1:-1].split(", ")
                    str_values = "','".join(array_values)
                    str_where.append(f"{field['fieldname']} = ('{str_values}')")
                else:
                    str_where.append(f"{field['fieldname']} = '{field['reload_argument'].format(**env)}'")
                reload_by[field['fieldname']] = arg_value

        if not is_delimited and config.get('temp_table') is None:
            raise Exception(f"La carga no esta delimitada por un campo de fecha")

        print(f"reload by {reload_by}")

        tablename = config['temp_table'] if config.get('temp_table') is not None else config['tablename']

        delete_template = f"DELETE FROM {tablename} WHERE "+(' AND '.join(str_where))
        if config.get('temp_table') is not None:
            print(f"reload temp table {tablename}")
            delete_template = f"DELETE FROM {tablename}"
        # print(delete_template)
        self.db.query(delete_template)

        insert_template, bindings = self.get_insert_template_and_bindings(tablename, fields_config)
        insert_config = {'template': insert_template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': config['limit_to_commit']}
        registros = self.db.map_data_by_bindings(registros, bindings)
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

        self.execute(config_id, fecha1, fecha2)

    def __guard(self, event):
        msg_body_keys = event['msg_body'].keys()
        if 'config_id' not in msg_body_keys or ('fec_ini' not in msg_body_keys) or ('format' not in msg_body_keys):
            raise Exception("Error no se encontro el atributo config_id, fec_ini o format")

        if type(event['msg_body']['config_id']) != type(''):
            raise Exception("El config_id deven ser una cadena")

        if event['msg_body']['format'] not in list(DTFORMAT_BY_ALIAS):
            raise Exception(f"Formato '{event['msg_body']['format']}' no valido")


class TableRotatorFromConfig:
    def __init__(self, repository, db):
        self.repository = repository
        self.db = db

    def execute(self, group_id=None):
        cargas = self.__get_configs(group_id)
        for row in cargas:
            self.__rotate_table(row)
    
    def __rotate_table(self, config):
        print(config["name"])
        # partition,daily_table,normal
        if config["table_type"] == "interval_table":
            table_step = dt.timedelta(days=1)
            now = dt.datetime.now()
            before = now - table_step
            after = now + table_step

            date_format = "%Y%m%d" if config.get("table_date_format") is None else config["table_date_format"]

            str_date = before.strftime(date_format)
            self.db.query(config["table_create_template"].format(str_date=str_date))
            print(f"creating table to {str_date}")

            str_date = now.strftime(date_format)
            self.db.query(config["table_create_template"].format(str_date=str_date))
            print(f"creating table to {str_date}")

            str_date = after.strftime(date_format)
            self.db.query(config["table_create_template"].format(str_date=str_date))
            print(f"creating table to {str_date}")

            # delete data
            date_to_delete = now - dt.timedelta(**json.loads(config["delete_data_older_than"]))
            date_to_delete = date_to_delete.strftime(date_format)
            table = config["tablename"].format(str_date=date_to_delete)
            self.db.query(f"DROP TABLE IF EXISTS {table}")
            print(f"deleting data older than or equals {date_to_delete}")
            

    def __get_configs(self, group_id=None):
        cargas = []
        if group_id == None:
            cargas = self.repository.get()
        else:
            cargas = self.repository.get_by_group_id(group_id)
        return cargas


class ApiDataPoller:
    def __init__(self, api):
        self.api = api

    def download(self, config, source_list, storage_dir):
        for src_data in source_list:
            self.download_one(config, src_data, storage_dir)
        return source_list

    def download_one(self, config, file, storage_dir):
        local_path = f"{storage_dir}/{file['file']}"
        data = api.get_all(file["url"])
        with open(local_path_filename, 'w') as content:
            content.write(json.dumps(data))

