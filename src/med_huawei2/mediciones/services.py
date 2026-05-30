import xml.etree.ElementTree as ET
import datetime as dt
from zipfile import ZipFile
import gzip
import tarfile
import re
import os
import json
import math
from src.shared.config import STORAGE_DIR, DTFORMAT_BY_ALIAS
import cx_Oracle
from concurrent.futures import ThreadPoolExecutor
import traceback
import stat
import shutil
import uuid

class CargaMediciones:
    def __init__(self, shared_repo, config_repo, control_carga_repo, app_container):
        self.shared_repo = shared_repo
        self.repository = config_repo
        self.control_carga_repo = control_carga_repo
        self.app_container = app_container
        self.sftp_list = [
            {'id': 'xmlhuawei2_01', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
            {'id': 'xmlhuawei2_02', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
            {'id': 'xmlhuawei2_03', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
            {'id': 'xmlhuawei2_04', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
            {'id': 'xmlhuawei2_05', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
            {'id': 'xmlhuawei2_06', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
            {'id': 'xmlhuawei2_07', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
            {'id': 'xmlhuawei2_08', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
            {'id': 'xmlhuawei2_09', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
            {'id': 'xmlhuawei2_10', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
            {'id': 'xmlhuawei2_11', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
            {'id': 'xmlhuawei2_12', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
            # {'id': 'xmlhuawei2_13', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
            {'id': 'xmlhuawei2_14', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
            {'id': 'xmlhuawei2_15', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
            {'id': 'xmlhuawei2_16', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
            {'id': 'xmlhuawei2_17', 'path': '/export/home/sysm/opt/oss/server/var/fileint/pmneexport/'},
        ]
        self.sftp_by_server = {}

        self.max_workers = 1
        self.max_error_servers = 1
        self.base_storage_dir = f"{STORAGE_DIR}med_huawei2"

        self.storage_dir = None
        self.start_time = None

    def execute(self, fecha, format, granularity, groups):
        print(f"fecha:", fecha, 'granularity:', granularity)
        configs = []
        if groups is None:
            configs = self.repository.get(granularity)
        else:
            configs = self.repository.get_by_group(granularity, groups)
        
        mediciones = list(map(lambda r: r['name'], configs))
        #mediciones = ['82863968']
        #fecha = dt.datetime.strptime('2022-07-15 00', '%Y-%m-%d %H')
        fecha2 = None
        granularity_period = 0
        if granularity == "1H":
            fecha2 = fecha + dt.timedelta(hours=1)
            granularity_period = 60
        elif granularity == "15MIN":
            fecha2 = fecha + dt.timedelta(minutes=15)
            granularity_period = 15
        elif granularity == "30MIN":
            fecha2 = fecha + dt.timedelta(minutes=30)
            granularity_period = 30
        else:
            fecha2 = fecha + dt.timedelta(hours=1)
            granularity_period = 60
        print(f"carga mediciones {mediciones}")
        all_data = {}
        for med in mediciones:
            all_data[med] = []

        self.start_time = dt.datetime.now()
        # self.storage_dir = f"{self.base_storage_dir}/{fecha.strftime('%Y%m%d%H')}_{self.start_time.strftime('%H%M%S%f')}"
        self.storage_dir = f"{self.base_storage_dir}/{fecha.strftime('%Y%m%d%H')}_{uuid.uuid4()}"

        if self.max_workers > 1:
            n_pages = math.ceil(len(self.sftp_list) / self.max_workers)
            executor = ThreadPoolExecutor(max_workers=self.max_workers)
            for page in range(1, n_pages+1):
                servers_to_process = self._get_data_of_page(self.sftp_list, self.max_workers, page)
                executor_by_server = {}
                for server in servers_to_process:
                    #print(server)
                    sftp_by_server = self.app_container.getInstance('sftp_service', True)
                    sftp_by_server.useConnection(server['id'])
                    sftp_by_server.connect()
                    self.sftp_by_server[server['id']] = sftp_by_server
                    executor_by_server[server['id']] = executor.submit(self._get_data_from_sftp, mediciones, server, fecha, fecha2)
                #print(page)
                server_errors = 0
                error = None
                for server in servers_to_process:
                    print(executor_by_server[server['id']].result())
                    result = executor_by_server[server['id']].result()
                    if type(result) != type(""):
                        server_errors += 1
                        error = result
                
                print(f"Fallas en servidores: {server_errors}")
                if server_errors > self.max_error_servers:
                    raise error
        else:
            server_errors = 0
            error = None
            for server in self.sftp_list:
                try:
                    sftp_by_server = self.app_container.getInstance('sftp_service')
                    sftp_by_server.useConnection(server['id'])
                    sftp_by_server.connect()
                    self.sftp_by_server = {}
                    self.sftp_by_server[server['id']] = sftp_by_server
                    result = self._get_data_from_sftp(mediciones, server, fecha, fecha2)
                    if type(result) != type(""):
                        server_errors += 1
                        error = result
                except BaseException as ssh_error:
                    server_errors += 1
                    error = ssh_error

            print(f"Fallas en servidores: {server_errors}")
            if server_errors > self.max_error_servers:
                raise error

        self._load_data(configs, fecha, fecha2, granularity, granularity_period)
        os.rmdir(self.storage_dir)
        #for med in mediciones:
        
        #self.sftp_service.disconnect()
    def _get_data_of_page(self, servers, perPage, page):
        len_servers = len(servers)
        lastIndex = 0
        i = perPage-1
        actual_page = 1
        while i <= len_servers or lastIndex < len_servers:
            #print(f"{i-(perPage-1)} - {i}")
            #print(servers[i-(perPage-1):i+1])
            if actual_page == page:
                return servers[i-(perPage-1):i+1]
            lastIndex = i
            i += perPage
            actual_page += 1

    def _get_data_from_sftp(self, mediciones, row, fecha, fecha2):
        try:
            return self._get_data_from_sftp_handler(mediciones, row, fecha, fecha2)
        except BaseException as e:
            print(f"{traceback.format_exc()}")
            return e
    
    def _get_data_from_sftp_handler(self, mediciones, row, fecha, fecha2):
        print(row['id'])
        #mediciones = ['1542455819', '82863968', '67109467']
        str_fecha = fecha.strftime('%Y%m%d')
        work_dir = f"{row['path']}/neexport_{str_fecha}"
        #storage_dir = f"{self.base_storage_dir}/{fecha.strftime('%Y%m%d%H')}/{row['id']}"
        storage_dir = f"{self.storage_dir}/{row['id']}"
        
        
        #pattern = re.compile(f".*{str_fecha}.{fecha.strftime('%H')}.*")
        dir_list = self.sftp_by_server[row['id']].getReference().listdir(work_dir)
        #dir_list = dir_list[:2]
        zip_files = []
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        for dir in dir_list:
            st_mode = self.sftp_by_server[row['id']].getReference().stat(f"{work_dir}/{dir}").st_mode
            is_dir = stat.S_ISDIR(st_mode)
            if is_dir == False:
                continue
            file_pattern = f".*{str_fecha}[.]{fecha.strftime('%H%M')}-0500-{fecha2.strftime('%H%M')}-0500.*"
            # file_pattern = f".*{str_fecha}[.]{fecha.strftime('%H')}00-0500.*"
            zip_files_part = self.sftp_by_server[row['id']].get_files(f"{work_dir}/{dir}", storage_dir, file_pattern)
            zip_files = zip_files + zip_files_part
            #zip_files = sftp.listdir(f"{work_dir}/{dir}")
            #filtered_files = list(filter(lambda f: pattern.match(f) is not None, zip_files))
            #zip_files_count = zip_files_count + len(zip_files)
        print(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(f"zip_files: {len(zip_files)}")
        
        json_formated = {}
        meas_info = {}
        for med in mediciones:
            json_formated[med] = []
            meas_info[med] = []
        #zip_files = [{'file': 'A20220715.0000-0500-0030-0500_HLIMCGP04.xml.gz'}]
        for file in zip_files:
            gzip_file = f"{storage_dir}/{file['file']}"
            xml_file = f"{storage_dir}/{file['file']}".replace('.gz', '')
            json_file = xml_file.replace('.xml', '.json')
            
            with gzip.open(gzip_file, 'rb') as zf, open(xml_file, 'wb') as xmlref:
                #file_content = gzip.decompress(f.read()).decode('utf-8')
                shutil.copyfileobj(zf, xmlref)
                xmlref.close()
                zf.close()
                file_content = None

                root = ET.parse(xml_file).getroot()
                measDataXml = root[1]

                for measInfoXml in measDataXml:
                    attribs = measInfoXml.attrib
                    measInfoId_of_info = attribs.get('measInfoId')
                    if measInfoId_of_info is not None:
                        if meas_info.get(measInfoId_of_info) is not None:
                            measInfoJson = self._map_all_row(measInfoXml)
                            formated_data = self._map_to_formated_data(measInfoJson)
                            meas_info[measInfoId_of_info].append(measInfoJson)
                            json_formated[measInfoId_of_info] += formated_data
                
                """
                if type([]) != type(json_content['measData']['measInfo']):
                    json_content['measData']['measInfo'] = [json_content['measData']['measInfo']]
                index_to_delete = []
                range_data = range(len(json_content['measData']['measInfo']))
                #print(range(len(json_content['measData']['measInfo'])))
                for i in range_data:
                    measInfoId = json_content['measData']['measInfo'][i]['measInfoId']
                    if measInfoId not in mediciones:
                        index_to_delete.append(i)
                    else:
                        json_formated[measInfoId] = json_formated[measInfoId] + self._map_to_formated_data(json_content['measData']['measInfo'][i])
                
                del json_content
                """

                os.unlink(xml_file)
            os.unlink(gzip_file)
        os.rmdir(storage_dir)

        """
        json_file = open(f"{storage_dir}.json", 'w')
        json_file.write(json.dumps(meas_info))
        json_file.close()
        """

        for med in mediciones:
            json_file = open(f"{storage_dir}_{med}.json", 'w')
            json_file.write(json.dumps(json_formated[med]))
            json_file.close()
        
        #json_file = open(f"{storage_dir}.json", 'r')
        #json_formated = json.loads(json_file.read())
        #json_file.close()
        count_by_med = {}
        for i in json_formated.keys():
            count_by_med[i] = len(json_formated[i])
        
        return f"{row['id']}: {count_by_med}"

    def _map_to_formated_data(self, measInfo):
        str_duration = int(measInfo['granPeriod']['duration'].replace('PT', '').replace('S', ''))
        granPeriod_duration = dt.timedelta(seconds=str_duration)
        granPeriod_time = dt.datetime.fromisoformat(measInfo['granPeriod']['endTime'])
        str_result_time = (granPeriod_time - granPeriod_duration).strftime('%Y-%m-%d %H:%M:%S')
        data = []
        #data_head = ['result_time', 'granularity_pediod', 'managed_object']
        #data_head = data_head + measInfo['measTypes'].strip().split(' ')
        #data.append(data_head)
        data_head = measInfo['measTypes'].strip().split(' ')
        range_head = range(len(data_head))

        measValue = measInfo['measValue']
        if type(measInfo['measValue']) != type([]):
            measValue = [measInfo['measValue']]

        for row in measValue:
            """
            row_data = [str_result_time, str_duration/60, row['measObjLdn']]
            row_data = row_data + row['measResults'].replace('NIL', '').strip().split(' ')
            data.append(row_data)
            """
            row_data = {}
            row_data['result_time'] = str_result_time
            row_data['granularity_period'] = str_duration/60
            #row_data['object_name'] = row['measObjLdn'].upper()
            try:
                row_data['object_name'] = row['measObjLdn'].upper()
            except Exception as e:
                print(row)
                print(measInfo['measValue'])
                raise e
            row_data['reliability'] = 'Reliable' if row.get('suspect') is None else 'Unreliable'
            mediciones = row['measResults'].strip().replace('NIL', '').split(' ')
            for index in range_head:
                row_data["M"+data_head[index]] = mediciones[index]
            data.append(row_data)
        return data

    def get_insert_template_and_bindings(self, table, cvffields_by_fieldconfig):
        str_fields = []
        str_binds = []
        bindings = {}
        for field in cvffields_by_fieldconfig:
            #field = cvffields_by_fieldconfig[csvfield]
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
                bindings[field['src_fieldname']] = cx_oracle_type

        template = f"INSERT INTO {table}({', '.join(str_fields)}) VALUES ({', '.join(str_binds)})"
        return template, bindings

    def _load_data(self, mediciones_config, fecha, fecha2, granularity, granularity_period):
        for row in mediciones_config:
            med_id = row['name']

            # obtiene datos desde json
            pattern = re.compile(f'.*{med_id}.json')
            json_files = os.listdir(self.storage_dir)
            json_files_processed = []
            data = []
            for file in json_files:
                if pattern.match(file) is not None:
                    f = open(f"{self.storage_dir}/{file}", 'r')
                    data += json.loads(f.read())
                    f.close()
                    json_files_processed.append(f"{self.storage_dir}/{file}")

            print(f"cargando {med_id}", len(data))

            fields_config = self.repository.get_fields_by_id(row['name'])

            template, bindings = self.get_insert_template_and_bindings(row['tablename'], fields_config)

            is_succesfull = False
            error = None
            try:
                data = self.del_duplicados(data)
                print(f"del_duplicados:", len(data))
                self.shared_repo.delete_where_collectiontime_between(row['tablename'], 'result_time', fecha, fecha2, granularity_period)
                self.shared_repo.insert_from_array(template, bindings, data)
                is_succesfull = True
            except BaseException as e:
                error = e
            except:
                is_succesfull = False

            self.control_carga_repo.save_carga(
                f"med_huawei2.{med_id}_{granularity}",
                f"med_huawei2_{med_id}_{fecha.strftime('%Y-%m-%d %H:%M:%S')}",
                len(data) if is_succesfull == True else 0,
                len(data),
                self.start_time,
                dt.datetime.now(),
                'CARGADO' if is_succesfull == True else 'ERROR',
                '',
                fecha
            )
            print(f"{med_id}: {len(data)}")

            # elimina archivos procesados
            for fproc in json_files_processed:
                os.unlink(fproc)

            # envio de error
            if is_succesfull == False:
                if error is not None:
                    raise error
                else:
                    raise Exception("Ocurrió un error no identificado al realizar la carga")

        #print(data)

    def del_duplicados(self, data):
        reviewed = set()
        resultado = []

        for d in data:
            tupla = tuple(sorted(d.items()))
            if tupla not in reviewed:
                reviewed.add(tupla)
                resultado.append(d)

        return resultado

    def _map_all_row(self, children_set):
        row_to_add = {}
        for children in children_set:
            #entry_name = children.tag.split('}')[1]
            entry_name = children.tag
            index2 = entry_name.rfind('}')
            if index2 >= 0:
                #index1 = entry_name.rfind('{')
                entry_name = entry_name[index2+1:]
                #print(entry_name)
            #entry_name = entry_name.replace('.', '_')
            if row_to_add.get(entry_name) is None:
                row_to_add[entry_name] = []
            if len(list(children)) > 0 or len(list(children.attrib)) > 0:
                row_to_add[entry_name].append(self._map_all_row(children))
            else:
                row_to_add[entry_name].append(children.text)
        for index in row_to_add.keys():
            if len(row_to_add[index]) == 1:
                row_to_add[index] = row_to_add[index][0]
        return dict(children_set.attrib, **row_to_add)

    def event_handler(self, event):
        self.__guard(event)
        date_format = DTFORMAT_BY_ALIAS[event['msg_body']['format']]
        queue_id = event['queue_id']
        fecha1 = dt.datetime.strptime(event['msg_body']['fec_ini'], date_format)
        granularity = event['msg_body'].get('granularity')
        group = event['msg_body'].get('group')
        if granularity is None:
            granularity = "1H"
        self.execute(fecha1, event['msg_body']['format'], granularity, group)

    def __guard(self, event):
        msg_body_keys = event['msg_body'].keys()
        if ('fec_ini' not in msg_body_keys) or ('format' not in msg_body_keys) or ('granularity' not in msg_body_keys):
            raise Exception("Error no se encontro el atributo 'mediciones', 'fec_ini', 'format' o 'granularity'")

        if event['msg_body']['format'] not in list(DTFORMAT_BY_ALIAS):
            raise Exception(f"Formato '{event['msg_body']['format']}' no valido")
        
        if event['msg_body']['granularity'] not in ('1H', '15MIN', '30MIN'):
            raise Exception(f"granularity '{event['msg_body']['granularity']}' no valido")

from src.med_huawei2.shared.services import LOAD_MEDICIONES
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer

class MedHuawei2EventConsumer(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.5
        self.medicion_by_queue = {}
        self.loop = False
        self.max_jobs_per_run = 4

        self.queue_handlers['med_huawei2'] = {'handler': LOAD_MEDICIONES, 'callback': lambda s, e: s.event_handler(e)}

        self.queue_ids = list(self.queue_handlers)

