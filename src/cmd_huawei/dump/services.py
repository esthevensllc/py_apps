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
from concurrent.futures import ThreadPoolExecutor
from src.shared.config import STORAGE_DIR, DTFORMAT_BY_ALIAS
from src.shared.services import SimplePaginator

class LoadHuaweiCommandFromConfig:
    def __init__(self, repo, db, app_container):
        self.repo = repo
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
        self.max_workers = 4
        self.max_finder_workers = 200
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
            dt_fecha1 = (dt.datetime.now() - dt.timedelta(days=1)).replace(hour=0, minute=0, second=0)
            dt_fecha2 = dt.datetime.now().replace(hour=0, minute=0, second=0)
        self.create_workdir()
        # self.storage_dir = f"{self.base_storage_dir}/202311131236709806"

        commands = self.repo.get()
        commands_by_flujo = {}
        for row in commands:
            key = row["flujo"]
            if commands_by_flujo.get(key) is None:
                commands_by_flujo[key] = []
            commands_by_flujo[key].append(row)

        config = {
            "file_pattern": "GExport_.+_([0-9]{14}).+.gz",
            "file_date_format": "%Y%m%d%H%M%S",
            "type": "GEXPORT"
        }

        if self.max_workers > 1:
            executor = ThreadPoolExecutor(max_workers=self.max_workers)
            paginator = SimplePaginator(list(self.sftp_list.keys()), self.max_workers)
            page = 1
            num_pages = paginator.get_num_pages()
            server_errors = 0
            while page <= num_pages:
                servers_to_process = paginator.get_page(page)
                executor_by_server = {}
                for server_id in servers_to_process:
                    executor_by_server[server_id] = executor.submit(self.pull_files_from_server, config, dt_fecha1, dt_fecha2, server_id)
                #print(page)
                error = None
                for server_id in servers_to_process:
                    print(executor_by_server[server_id].result())
                    result = executor_by_server[server_id].result()
                    if type(result) != type(""):
                        server_errors += 1
                        error = result
                page = page + 1
            print("ungzip files")
            os.makedirs(f"{self.storage_dir}/xml")
            page = 1
            server_errors = 0
            while page <= num_pages:
                servers_to_process = paginator.get_page(page)
                executor_by_server = {}
                for server_id in servers_to_process:
                    self.files_by_server[server_id] = [{"file": file} for file in os.listdir(f"{self.storage_dir}/{server_id}")]
                    executor_by_server[server_id] = executor.submit(self.extract_files_worker, self.storage_dir, self.files_by_server[server_id], server_id)
                error = None
                for server_id in servers_to_process:
                    print(executor_by_server[server_id].result())
                    result = executor_by_server[server_id].result()
                    if type(result) != type(""):
                        server_errors += 1
                        error = result
                page = page + 1

            self.create_cmd_workdir(commands)
            print("extract commands")
            xml_files = [{"file": file} for file in os.listdir(f"{self.storage_dir}/xml")]
            executor = ThreadPoolExecutor(max_workers=self.max_finder_workers)
            paginator = SimplePaginator(xml_files, self.max_finder_workers)
            num_pages = paginator.get_num_pages()
            
            for cmd in commands:
                page = 1
                executor_by_cmd = {}
                start_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                while page <= num_pages:
                    to_process = paginator.get_page(page)
                    for file in to_process:
                        executor_by_cmd[file["file"]] = executor.submit(self.extract_commands_from_xml_worker, cmd["command"], self.storage_dir, file["file"])
                    for file in to_process:
                        result_out = executor_by_cmd[file["file"]].result()
                        # print()
                    print(f"complete {page}")
                    executor_by_cmd = {}
                    page = page + 1
                end_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"{cmd['command']}: [{start_time} , {end_time}]")
            
            pritn("xml to json")
            executor = ThreadPoolExecutor(max_workers=1)
            wait_for=[]
            for flujo in commands_by_flujo.keys():
                commands_flujo = commands_by_flujo[flujo]
                contador = 0
                for cmd in commands_flujo:
                    contador = contador + 1
                    lista_columnas_archivo = []
                    lista_colum_unicas = []
                    lista_Data_Comando = []
                    
                    print(cmd["command"])
                    xml_path = f"{self.storage_dir}/{cmd['command']}"
                    xml_files = os.listdir(xml_path)
                    # for filename in xml_files:
                    wait_for.append(executor.submit(self.xml_to_json_worker, cmd["command"], self.storage_dir, xml_files))

                    for process in wait_for:
                        print(process.result())
                    wait_for=[]

            print("loading files")
            for cmd in commands:
                self.load_json_worker(self.storage_dir, config["type"], cmd["command"])


    def create_workdir(self):
        start_time = dt.datetime.now()
        # validate work dir
        if not os.path.exists(self.base_storage_dir):
            os.makedirs(self.base_storage_dir)
            if not os.path.exists(self.base_storage_dir):
                raise Exception(f"El directorio base de trabajo {self.base_storage_dir} no se pudo crear y no existe")

        self.storage_dir = f"{self.base_storage_dir}/{start_time.strftime('%Y%m%d%H%M%f')}"
        os.makedirs(self.storage_dir)
        if not os.path.exists(self.storage_dir):
            raise Exception(f"El directorio de trabajo {self.storage_dir} no se pudo crear y no existe")

        for server_id in self.sftp_list.keys():
            os.makedirs(f"{self.storage_dir}/{server_id}")

    def create_cmd_workdir(self, commands):
        for cmd in commands:
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

    def xml_to_json_worker(self, command, storage_dir, files):
        start_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        result = []
        for filename in files:
            one_result = self.object_xml_parser.execute(f"{storage_dir}/{command}", filename)
            result = result + one_result
            one_result = []
        
        df = pd.json_normalize(result)
        df = df.fillna("")
        result = df.values.tolist()
        fields = list(df.columns)
        count = len(result)
        os.rmdir(f"{storage_dir}/{command}")

        json_file = f"{storage_dir}/{command}".replace(".xml", "")+".json"
        with open(f"{json_file}", "w") as file:
            json.dump({"fields": fields, "data": result}, file, indent=2)
        
        result = []
        end_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"[{start_time} , {end_time}]: {command} parsed {count} objects"

    def load_json_worker(self, storage_dir, type, command):
        with open(f"{storage_dir}/{command}.json", "r") as file:
            command_data = json.loads(file.read())

            self.cmd_table_creator.execute(type, command, command_data["fields"])

            tablename = f"{type}_{command}"
            str_fields = ",".join(command_data["fields"])
            str_binds = ", ".join([f":{index}" for index in range(len(command_data["fields"]))])
            bindings = [cx_Oracle.STRING for field in command_data["fields"]]
            config = {
                'template': f"INSERT INTO {tablename}({str_fields}) values ({str_binds})",
                'bindings': bindings,
                'row_type': 'array',
                'limit_to_commit': 10000
            }
            self.db.query(f"DELETE FROM {tablename}")
            self.db.save_from_array2(config, command_data["data"])
            command_data = {}
        # os.unlink(f"{storage_dir}/{command}.json")

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
            result = subprocess.run(f"sed -n \"/<class name=\"{class_pattern}\">/,/class>/p\" \"{xmlfilepath}\" > \"{outputfilepath}\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise Exception(result.stderr.decode('utf-8'))

class ObjectXmlParser:
    def execute(self, xml_dir, xmlfilename):
        xmlpath = f"{xml_dir}/{xmlfilename}"
        validation = False
        with open(xmlpath, 'r') as file:
            for line in file:
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
        os.unlink(xmlpath)
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
        config = {
            'template': "INSERT INTO dump_columnas_faltantes(COLUMNA, NOMBRE_TABLA) values (:1, :2)",
            'bindings': [cx_Oracle.STRING, cx_Oracle.STRING],
            'row_type': 'array',
            'limit_to_commit': 50
        }
        self.db.query(f"DELETE FROM {tablename} WHERE NOMBRE_TABLA = '{tablename}'")
        self.db.save_from_array2(config, fields_to_load)

        query = f"""begin
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
        end loop;"""
        self.db.query(query)
