from shutil import rmtree
import socket
import pandas as pd
import cx_Oracle
import json
import subprocess
from lxml import etree
import gzip
import shutil
import os
# import xml.etree.ElementTree as ET
import datetime as dt
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.shared.config import STORAGE_DIR, STORAGE_TEMP_DIR, DTFORMAT_BY_ALIAS
from src.shared.services import SimplePaginator, TempDataManager
from src.shared.cache.domain import CacheRepository

class LoadHuaweiCommandFromConfig:
    def __init__(self, repo, control_carga_repo, cache: CacheRepository, db, app_container):
        self.repo = repo
        self.control_carga_repo = control_carga_repo
        self.cache = cache
        self.db = db
        self.base_storage_dir = f"{STORAGE_DIR}command_huawei"
        self.sftp_list = {
            'xmlhuawei2_01': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            'xmlhuawei2_02': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            'xmlhuawei2_03': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            'xmlhuawei2_04': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            'xmlhuawei2_05': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            'xmlhuawei2_06': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            'xmlhuawei2_07': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            'xmlhuawei2_08': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            'xmlhuawei2_09': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            'xmlhuawei2_10': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            'xmlhuawei2_11': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            'xmlhuawei2_12': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            # 'xmlhuawei2_13': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            'xmlhuawei2_14': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            'xmlhuawei2_15': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            'xmlhuawei2_16': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            'xmlhuawei2_17': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
            'xmlhuawei2_18': {'path': '/export/home/sysm/opt/oss/server/var/fileint/cm/GExport/'},
        }
        self.sftp_service = {}
        self.files_by_server = {}
        self.max_workers = 10
        self.max_finder_workers = 40
        self.command_by_key = {}
        self.object_xml_finder = ObjectXmlFinder()
        self.object_xml_parser = ObjectXmlParser()
        self.cmd_table_creator = CommandTableCreator(db)
        for server_id in self.sftp_list.keys():
            sftp_service = app_container.getInstance('sftp_service', True)
            sftp_service.useConnection(server_id)
            sftp_service.connect()
            self.sftp_service[server_id] = sftp_service


    def execute(self, dt_fecha1=None, dt_fecha2=None):
        if dt_fecha1 is None:
            dt_fecha1 = (dt.datetime.now() - dt.timedelta(days=0)).replace(hour=0, minute=0, second=0)
            dt_fecha2 = (dt.datetime.now() + dt.timedelta(days=1)).replace(hour=0, minute=0, second=0)
        if type(dt_fecha1) == type(""):
            dt_fecha1 = dt.datetime.strptime(dt_fecha1, "%Y-%m-%d")
            dt_fecha2 = dt_fecha1 + dt.timedelta(days=1)
        self.create_workdir(dt_fecha1)
        # self.storage_dir = f"{self.base_storage_dir}/202311131236709806"

        commands = self.repo.get()
        self.command_by_key = {}
        for row in commands:
            key = row["command"]
            self.command_by_key[key] = row

        config = {
            "file_pattern": "GExport_.+_([0-9]{14}).+.gz",
            "file_date_format": "%Y%m%d%H%M%S",
            "type": "GEXPORT"
        }

        if self.max_workers > 1:
            xml_generated = self.xml_dir_was_generated(dt_fecha1)
            if not xml_generated:
                print("downloading files")
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = []
                    for server_id in self.sftp_list.keys():
                        futures.append(executor.submit(self.pull_files_from_server, config, dt_fecha1, dt_fecha2, server_id))
                    for future in as_completed(futures):
                        print(future.result())

                print("ungzip files")
                os.makedirs(f"{self.storage_dir}/xml")
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = []
                    for server_id in self.sftp_list.keys():
                        self.files_by_server[server_id] = [{"file": file} for file in os.listdir(f"{self.storage_dir}/{server_id}")]
                        futures.append(executor.submit(self.extract_files_worker, self.storage_dir, self.files_by_server[server_id], server_id))
                    for future in as_completed(futures):
                        print(future.result())
                self.set_dir_generated(self.storage_dir)
            else:
                print("xml already downloaded")

            self.create_cmd_workdir(commands)
            print("extract commands")
            xml_files = [{"file": file} for file in os.listdir(f"{self.storage_dir}/xml")]
            # importerExecutor = ThreadPoolExecutor(max_workers=2)
            importerFutures = []
            with ThreadPoolExecutor(max_workers=self.max_finder_workers) as executor:
                for cmd in commands:
                    control_files = self.control_carga_repo.getOfProyectWhereFechaArchivo(f"cmd_huawei.{cmd['command']}", dt_fecha1, dt_fecha2)
                    if len(control_files) > 0:
                        print(f"{cmd['command']}: is already loaded")
                        continue
                    start_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    futures = []
                    for file in xml_files:
                        futures.append(executor.submit(self.extract_commands_from_xml_worker, cmd["command"], self.storage_dir, file["file"]))
                    for future in as_completed(futures):
                        pass
                    end_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"{cmd['command']}: [{start_time} , {end_time}]")
                    
                    xml_path = f"{self.storage_dir}/{cmd['command']}"
                    xml_files_command = os.listdir(xml_path)
                    # importerFutures.append(importerExecutor.submit()
                    self.xml_to_json_worker(dt_fecha1, config["type"], cmd["command"], self.storage_dir, xml_files_command)

            # print("commands loaded")
            # for future in as_completed(importerFutures):
            # print(future.result())
            rmtree(self.storage_dir)
            self.set_dir_generated(None)


    def create_workdir(self, fecha):
        start_time = dt.datetime.now()
        # validate work dir
        if not os.path.exists(self.base_storage_dir):
            os.makedirs(self.base_storage_dir)
            if not os.path.exists(self.base_storage_dir):
                raise Exception(f"El directorio base de trabajo {self.base_storage_dir} no se pudo crear y no existe")

        self.storage_dir = f"{self.base_storage_dir}/{fecha.strftime('%Y%m%d')}"
        if not self.xml_dir_was_generated(fecha):
            if os.path.exists(self.storage_dir):
                rmtree(self.storage_dir)
            os.makedirs(self.storage_dir)
            for server_id in self.sftp_list.keys():
                os.makedirs(f"{self.storage_dir}/{server_id}")

    def xml_dir_was_generated(self, fecha):
        hostname = socket.gethostname()
        return self.cache.get(f"command_huawei_xml_{hostname}_generated", False) == self.storage_dir

    def set_dir_generated(self, storage_dir):
        hostname = socket.gethostname()
        self.cache.set(f"command_huawei_xml_{hostname}_generated", storage_dir)

    def create_cmd_workdir(self, commands):
        for cmd in commands:
            if os.path.exists(f"{self.storage_dir}/{cmd['command']}"):
                rmtree(f"{self.storage_dir}/{cmd['command']}")
            os.makedirs(f"{self.storage_dir}/{cmd['command']}")

    def pull_files_from_server(self, config, dt_fecha1, dt_fecha2, server_id):
        start_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        files = self._get_files_from_server(config, self.sftp_list[server_id]["path"], dt_fecha1, dt_fecha2, server_id)
        end_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._download_files(f"{self.storage_dir}/{server_id}", files, server_id)
        end_time2 = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.files_by_server[server_id] = files
        return f"{server_id}: {len(files)} - get[{start_time} , {end_time}] download[{end_time} , {end_time2}]"

    def extract_files_worker(self, storage_dir, files, server_id):
        start_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.extract_files(storage_dir, files, server_id)
        end_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"{server_id}: {len(files)} - get[{start_time} , {end_time}]"

    def extract_commands_from_xml_worker(self, command, storage_dir, xmlfile):
        start_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        xml_file = f"{storage_dir}/xml/{xmlfile}"
        out_xml_file = f"{storage_dir}/{command}/{xmlfile}"
        self.object_xml_finder.execute(command, xml_file, out_xml_file)
        end_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"[{start_time} , {end_time}]: {xmlfile}"

    def xml_to_json_worker(self, fecha, type, command, storage_dir, files):
        print("xml_to_json_worker")
        json_file = f"{storage_dir}/{command}".replace(".xml", "")+".json"
        start_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        count = 0
        
        pattern = re.compile(f"{command}.+\.json")
        json_files = list(filter(lambda f: pattern.match(f) is not None, os.listdir(storage_dir)))
        for jsonfile in json_files:
            os.unlink(jsonfile)

        chunk_limit = self.command_by_key[command]["chunk_limit"]
        temp_data_manager = TempDataManager(limit=chunk_limit, path=STORAGE_TEMP_DIR, filename=command)
        for filename in files:
            one_result = self.object_xml_parser.execute(f"{storage_dir}/{command}", filename)
            for row in one_result:
                temp_data_manager.add(row)
            one_result = []
        
        rmtree(f"{storage_dir}/{command}")
        print("load_json_worker")
        self.load_json_worker(fecha, temp_data_manager, type, command)
        end_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"[{start_time} , {end_time}]: {command} parsed {count} objects"

    def load_json_worker(self, fecha, temp_data_manager: TempDataManager, type, command):
        start_time = dt.datetime.now()
        tablename = f"{type}_{command}"
        all_data_count = temp_data_manager.count()
        data_count = 0
        has_error = False
        error = None
        try:
            self.db.query(F"""BEGIN
                EXECUTE IMMEDIATE 'DELETE FROM {tablename}';
                COMMIT;
            EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE != -942 THEN RAISE; END IF;
            END;""")
            for chunk_data in temp_data_manager.get():
                dataframe = pd.json_normalize(chunk_data)
                dataframe = dataframe.fillna("")
                result_data = dataframe.values.tolist()
                fields = list(dataframe.columns)
                dataframe = None
                chunk_data = []

                self.cmd_table_creator.execute(type, command, fields)

                str_fields = '","'.join(fields)
                str_fields = f'"{str_fields}"'.upper()
                str_binds = ", ".join([f":{index}" for index in range(len(fields))])
                bindings = [cx_Oracle.STRING for field in fields]
                load_config = {
                    'template': f"INSERT INTO {tablename}({str_fields}) values ({str_binds})",
                    'bindings': bindings,
                    'row_type': 'array',
                    'limit_to_commit': 10000
                }
                self.db.save_from_array2(load_config, result_data)
                data_count += len(result_data)
                result_data = []
        except BaseException as e:
            has_error = True
            error = e
        
        end_time = dt.datetime.now()
        self.control_carga_repo.save_carga(
            f"cmd_huawei.{command}",
            f"{command}_{fecha.strftime('%Y-%m-%d')}.json",
            data_count,
            all_data_count,
            start_time,
            end_time,
            'CARGADO' if has_error == False else "ERROR",
            '' if has_error == False else str(error),
            fecha
        )
        if has_error == True:
            raise error

    def _get_files_from_server(self, config, remote_dir, dt_fecha1, dt_fecha2, server_id):
        sftp = self.sftp_service[server_id].getReference()
        try:
            sftp.chdir(remote_dir)
        except Exception as e:
            print(e)
            raise Exception(f"El directorio {remote_dir} no existe")
        pattern = re.compile(config['file_pattern'])
        files = self.sftp_service[server_id].get_filename_and_updated_at(remote_dir, config['file_pattern'])
        files_filtered = []
        for row in files:
            str_date = pattern.search(row['file']).group(1)
            date_of_file = dt.datetime.strptime(str_date, config['file_date_format'])
            if dt_fecha1 <= date_of_file and date_of_file < dt_fecha2:
                files_filtered.append(row)
        return files_filtered

    def _download_files(self, storage_dir, files, server_id):
        sftp = self.sftp_service[server_id].getReference()
        for file in files:
            filename = file['file'] 
            try:
                sftp.get(f"{file['path']}/{filename}", f"{storage_dir}/{filename}")
            except Exception as e:
                raise e

    def extract_files(self, storage_dir, files, server_id):
        for file in files:
            filename = file['file']
            gzip_file = f"{storage_dir}/{server_id}/{file['file']}"
            xml_file = f"{storage_dir}/xml/{file['file']}".replace('.gz', '')

            with gzip.open(gzip_file, 'rb') as f_in, open(xml_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.unlink(gzip_file)
        os.rmdir(f"{storage_dir}/{server_id}")


class ObjectXmlFinder:

    def execute(self, class_pattern, xmlfilepath, outputfilepath):
        """context = etree.iterparse(xmlfilepath, events=('start', 'end'))
        class_parent = ""
        child = []
        level = 0
        for event, element in context:
            pattern_match = False
            if event == "start":
                level = level+1
            elif event == "end":
                level = level-1
            if element.tag == "class":
                class_parent = element.get('name')
                pattern_match = class_pattern.match(class_parent)

            if pattern_match == False and level >= 4:
                element.clear()
            elif event == 'start' and element.tag == 'object' and pattern_match == True:
                child.append(etree.tostring(element, encoding="unicode"))
        
        output_file = open(outputfilepath, 'w', encoding="utf-8")
        output_file.write("".join(child))
        output_file.close()"""
        
        # xmlfilepath = xmlfilepath.replace("/", "\\")
        # outputfilepath = outputfilepath.replace("/", "\\")
        result = ""
        if "_" in class_pattern:
            result = subprocess.run(f"sed -n \"/<class name=.{class_pattern}.*>/,/class>/p\" \"{xmlfilepath}\" > \"{outputfilepath}\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            result = subprocess.run(f"sed -n \"/<class name=.{class_pattern}.>/,/class>/p\" \"{xmlfilepath}\" > \"{outputfilepath}\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise Exception(result.stderr.decode('utf-8'))

class ObjectXmlParser:
    def execute(self, xml_dir, xmlfilename):
        xmlpath = f"{xml_dir}/{xmlfilename}"
        validation = False
        with open(xmlpath, 'r') as xmlfile_reader:
            for line in xmlfile_reader:
                validation = True
                break
        if validation == False:
            os.unlink(xmlpath)
            return []

        tree = etree.parse(xmlpath)
        root = tree.getroot()
        objects = []
        str_date = dt.datetime.now().strftime("%d/%m/%Y %H")
        for object in root:
            json_object = {"archivo": xmlfilename, "fecha_actualizacion": str_date}
            for parameter in object:
                json_object[parameter.get("name")] = parameter.get("value")
            objects.append(json_object)
        return objects

class CommandTableCreator:
    def __init__(self, db):
        self.db = db

    def execute(self, type, command, fields):
        tablename = f"{type}_{command}".upper()
        query = f"""DECLARE
            V_TABLENAME VARCHAR2(250) := '{tablename}';
            V_EXISTS NUMBER;
        BEGIN
            SELECT COUNT(*) INTO V_EXISTS FROM USER_TABLES
            WHERE table_name = V_TABLENAME;

            IF V_EXISTS = 0 THEN
                EXECUTE IMMEDIATE 'create table '|| V_TABLENAME ||'(archivo varchar2(3000), fecha_actualizacion varchar2(50))';
            END IF;
        END;"""
        self.db.query(query)

        fields_to_load = [(tablename, field) for field in fields]
        insert_config = {
            'template': "INSERT INTO dump_columnas_faltantes(NOMBRE_TABLA, COLUMNA) values (:1, :2)",
            'bindings': [cx_Oracle.STRING, cx_Oracle.STRING],
            'row_type': 'array',
            'limit_to_commit': 200
        }
        self.db.query(f"DELETE FROM dump_columnas_faltantes WHERE NOMBRE_TABLA = '{tablename}'")
        self.db.save_from_array2(insert_config, fields_to_load)

        query = f"""declare
            cadena_sql varchar2(1000);
            cant_col number;
            cursor c_columns is
            select distinct nombre_tabla, columna from dump_columnas_faltantes where nombre_tabla = '{tablename}';
        begin
            for temp in c_columns loop
                select count(1) into cant_col from user_tab_cols
                where upper(table_name) = upper(temp.nombre_tabla)
                and upper(column_name) = upper(temp.columna);

                if cant_col = 0 then
                    cadena_sql:='alter table ' || upper(temp.nombre_tabla) || ' add ("' || upper(temp.columna) || '" varchar2(3000))';
                    EXECUTE IMMEDIATE cadena_sql;
                end if;
            end loop;
        end;"""
        self.db.query(query)
