import datetime as dt
import re
import csv
import cx_Oracle
from src.shared.config import STORAGE_DIR
from src.shared.carga.services import BaseCargaFromConfig

from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.speedtest.shared.services import LOAD_SPEEDTEST_FROM_CONFIG
from src.shared.services import TempDataManager

class SpeedTestProcessor:
    def process(self, config, sources):
        for index in range(len(sources)):
            sources[index] = self.process_one(sources[index], config)
        return sources

    def process_one(self, source, config):
        envlist = {
            'str_filedate': source['str_filedate'],
            'str_filedate_day': source['str_filedate_day'],
            'filename': source['filename'],
            'filepath': source['filepath'],
        }
        temp_manager = self.map_temp_manager(source['filepath'], config, env=envlist)
        new_source = source.copy()
        new_source["temp_manager"] = [temp_manager]
        return new_source

    def map_temp_manager(self, filepath, config, env):
        temp_data = TempDataManager(config["limit_to_commit"], filepath.replace(".csv","").replace(".zip",""))
        skip_lines = 1 if config.get("skip_lines") is None else config["skip_lines"]
        file_delimiter = ',' if config.get("file_delimiter") is None else config["file_delimiter"]
        with open(filepath, newline='', encoding='UTF-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=file_delimiter)
            counter = 0
            for index in range(skip_lines):
                next(reader)
            for row in reader:
                counter += 1
                mapped_row = []
                for field in config["fields"]:
                    try:
                        value = row[int(field["src_fieldname"])]
                        if field.get('map_with') is not None:
                            value = eval(f"f\"{field['map_with']}\"")
                        if value == '':
                            value = None
                        mapped_row.append(value)
                    except BaseException as e:
                        print(row)
                        print(f"line: {counter}, field: {field['fieldname']}, value: '{value}'")
                        raise e
                temp_data.add(mapped_row)
        return temp_data


class LoadSeedTestFromConfig(BaseCargaFromConfig):
    def __init__(self, db, ch_db, repository, sftp_service, control_carga_repo):
        super().__init__(db, repository, sftp_service, control_carga_repo)
        self.ch_db = ch_db
        self.speedtest_api = sftp_service
        self.base_storage_dir = f"{STORAGE_DIR}speedtest"
        self.speedtest_processor = SpeedTestProcessor()

    def _get_files_from_server(self, config, remote_dir, dt_fecha1, dt_fecha2):
        result = self.speedtest_api.get(config["work_dir"])
        result = result.json()
        files = []
        pattern = re.compile(config['file_pattern'])
        for row in result:
            name = row["name"]
            if config.get("file_date_added_from_mtime") == True:
                filename_parts = row["name"].split(".")
                strfiledate = dt.datetime.fromtimestamp(row["mtime"]/1000).strftime(config['file_date_format'])
                name = f"{filename_parts[0]}_{strfiledate}.{filename_parts[1]}"
            if pattern.match(name) is not None:
                files.append({
                    'file': name,
                    'path': config["work_dir"],
                    'url': row["url"]
                })
        
        files_filtered = []
        for row in files:
            str_date = pattern.search(row['file']).group(1)
            date_of_file = dt.datetime.strptime(str_date, config['file_date_format'])
            if dt_fecha1 <= date_of_file and date_of_file < dt_fecha2:
                files_filtered.append(row)
        
        for row in files_filtered:
            print(row["file"])
        return files_filtered

    def _download_files(self, storage_dir, files_filtered):
        for file in files_filtered:
            filename = file['file']
            local_path_filename = f"{storage_dir}/{filename}"
            try:
                response = self.speedtest_api.get(file['url'], base_url=False)
                with open(local_path_filename, 'wb') as content:
                    content.write(response.content)
            except Exception as e:
                raise e

    def _get_data_from_csv(self, fields_config, filename, skip_lines=0, date_of_file=None, env={}):
        self.config["fields"] = fields_config
        env['filepath'] = filename
        source = self.speedtest_processor.process_one(env, self.config)
        return source["temp_manager"]

    def count_data_from_source(self, registros):
        print("count:", registros[0].count())
        return registros[0].count()

    def get_insert_template_and_bindings(self, table, fields_config):
        if self.config.get("db_product_name") == "clickhouse":
            datatypes_by_db = {"number": "decimal", "int": "int", "varchar2": "string", "date": "datetime"}
            bindings = []
            for field in fields_config:
                if field['type'] not in ('number','varchar2','date'):
                    raise Exception(f"El field {field['fieldname']} tiene un tipo de dato '{field['type']}' que no existe")
                bindings.append({"type": datatypes_by_db[field['type']], "name": field['fieldname']})
            return table, bindings
        else:
            str_fields = []
            str_binds = []
            bindings = []
            counter = 0
            for field in fields_config:
                if field is not None:
                    counter += 1
                    str_fields.append(field['fieldname'])
                    cx_oracle_type = None
                    if field['type'] == 'number':
                        str_binds.append(f":{counter}")
                        cx_oracle_type = cx_Oracle.NUMBER
                    elif field['type'] == 'varchar2':
                        str_binds.append(f":{counter}")
                        cx_oracle_type = cx_Oracle.STRING
                    elif field['type'] == 'date':
                        date_format = 'YYYY-MM-DD HH24:MI:SS' if field.get("type_format") is None else field.get("type_format")
                        str_binds.append(f"TO_DATE(:{counter}, '{date_format}')")
                        cx_oracle_type = cx_Oracle.STRING
                    else:
                        raise Exception(f"El field {field['fieldname']} tiene un tipo de dato '{field['type']}' que no existe")
                    bindings.append(cx_oracle_type)

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
                if config.get("db_product_name") == "clickhouse":
                    str_where.append(f"toDateTime('{str_fecha1}') <= {field['fieldname']} AND {field['fieldname']} < toDateTime('{str_fecha2}')")
                else:
                    str_where.append(f"to_date('{str_fecha1}', 'yyyy-mm-dd hh24:mi:ss') <= {field['fieldname']} AND {field['fieldname']} < to_date('{str_fecha2}', 'yyyy-mm-dd hh24:mi:ss')")
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
        if config.get("db_product_name") == "clickhouse":
            delete_template = f"ALTER TABLE {tablename} DELETE WHERE "+(' AND '.join(str_where))
        if config.get('temp_table') is not None:
            print(f"reload temp table {tablename}")
            delete_template = f"DELETE FROM {tablename}"
            if config.get("db_product_name") == "clickhouse":
                delete_template = f"ALTER TABLE {tablename} DELETE WHERE 1=1"
        # print(delete_template)
        counter = 0
        if config.get("db_product_name") == "clickhouse":
            if config.get('reload_validation', False):
                query_validation = f"SELECT count(*) as counter from {tablename} where "+(' AND '.join(str_where))
                validation = self.ch_db.fetch(query_validation)
                if validation[0][0] > 0:
                    self.ch_db.query(delete_template)
            else:
                self.ch_db.query(delete_template)
            insert_template, bindings = self.get_insert_template_and_bindings(tablename, fields_config)
            insert_config = {'template': insert_template, 'bindings': bindings, 'row_type': 'array', 'limit_to_commit': config['limit_to_commit']}
            for temp_manager in registros:
                counter += temp_manager.count()
                for chunk_data in temp_manager.get():
                    chunk_data = self.ch_db.map_data_by_bindings(chunk_data, bindings)
                    self.ch_db.insert(insert_config, chunk_data)
        else:
            if config.get('reload_validation', False):
                query_validation = f"SELECT count(*) as counter from {tablename} where "+(' AND '.join(str_where))
                validation = self.db.fetch(query_validation)
                if validation[0][0] > 0:
                    self.db.query(delete_template)
            else:
                self.ch_db.query(delete_template)
            insert_template, bindings = self.get_insert_template_and_bindings(tablename, fields_config)
            insert_config = {'template': insert_template, 'bindings': bindings, 'row_type': 'array', 'limit_to_commit': config['limit_to_commit']}
            for temp_manager in registros:
                counter += temp_manager.count()
                for chunk_data in temp_manager.get():
                    chunk_data = self.db.map_data_by_bindings(chunk_data, bindings)
                    self.db.save_from_array2(insert_config, chunk_data)
        print(f"data: {counter}")


class SeedTestEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, repository, sftp_service, control_carga_repo, queue_service):
        super().__init__(sftp_service, control_carga_repo, queue_service)
        self.repository = repository
        self.speedtest_api = sftp_service

    def get_cargas_config(self, group_id=None):
        return self.repository.get()

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        result = self.speedtest_api.get(config["work_dir"])
        result = result.json()
        files = []
        pattern = re.compile(config['file_pattern'])
        for row in result:
            name = row["name"]
            if config.get("file_date_added_from_mtime") == True:
                filename_parts = row["name"].split(".")
                strfiledate = dt.datetime.fromtimestamp(row["mtime"]/1000).strftime(config['file_date_format'])
                name = f"{filename_parts[0]}_{strfiledate}.{filename_parts[1]}"
            if pattern.match(name) is not None:
                files.append({
                    'file': name,
                    'path': config["work_dir"],
                    'url': row["url"]
                })
        
        files_filtered = []
        for row in files:
            str_date = pattern.search(row['file']).group(1)
            date_of_file = dt.datetime.strptime(str_date, config['file_date_format'])
            if dt_fecha1 <= date_of_file and date_of_file < dt_fecha2:
                files_filtered.append(row)
        return files_filtered


class SpeedTestEventConsumerFromConfig(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service, repository):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.1
        self.repository = repository
        self.loop = False
        self.config_by_queueid = {}

    def execute(self, group_id=None):
        cargas = []
        if group_id == None:
            cargas = self.repository.get()
        else:
            cargas = self.repository.get_by_group_id(group_id)

        if len(cargas) == 0:
            raise Exception(f"No existen cargas")
        
        for row in cargas:
            self.config_by_queueid[row["queue_id"]] = row

        def map_event(event):
            event['msg_body']['config_id'] = self.config_by_queueid[event['queue_id']]["id"]
            return event

        for row in cargas:
            queue_id = row["queue_id"]
            self.queue_handlers[queue_id] = {'handler': LOAD_SPEEDTEST_FROM_CONFIG, 'callback': lambda s, e: s.event_handler(map_event(e))}

        self.queue_ids = list(self.queue_handlers)
        super().execute()
