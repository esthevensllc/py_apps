from src.shared.config import STORAGE_DIR, BASE_DIR, DTFORMAT_BY_ALIAS
import datetime
import subprocess as subp
import os
import csv
import re
import cx_Oracle
from src.apic.shared.services import BaseApicService

class LoadCSV(BaseApicService):
    def __init__(self, repository, shared_repo, control_carga_repo, sftp_service):
        self.repository = repository
        self.shared_repo = shared_repo
        self.control_carga_repo = control_carga_repo
        self.sftp_service = sftp_service
        self.dir_base = '/hfs_public/nbi/text/pfm_output'
        self.storage_dir = STORAGE_DIR+'NCE'
        self.csv_format_by_alias = {'dxd': '%Y%m%d', 'hxh': '%Y%m%d%H', 'mxm': '%Y%m%d%H%M'}
    
    def execute(self, queue_id, mediciones, fecha, dt_format = 'mxm'):
        print("nce.carga_csv")
        start_time = datetime.datetime.now()

        codigo_medicion = mediciones[0]
        fecha2 = None
        if dt_format == 'dxd':
            fecha2 = fecha + datetime.timedelta(days=1)
        elif dt_format == 'hxh':
            fecha2 = fecha + datetime.timedelta(hours=1)
        elif dt_format == 'mxm':
            fecha2 = fecha + datetime.timedelta(minutes=1)

        base_config = self.repository.find_by_codigo_med(codigo_medicion)
        if base_config is None:
            raise Exception(f"El codigo_medicion '{codigo_medicion}' no existe")
        
        fields = self.repository.get_fields_by_tabla(base_config['nombre_tabla'])
        remote_dir = f"{self.dir_base}/{fecha.strftime('%Y%m%d')}"
        storage_dir = f"{self.storage_dir}/{codigo_medicion}_{start_time.strftime('%H%M%S%f')}"
        str_to_filter = f"{base_config['codigo_medicion']}_{base_config['granularidad']}_{fecha.strftime(self.csv_format_by_alias[dt_format])}.*.csv"

        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        if not os.path.exists(storage_dir):
            raise Exception(f"El directorio local de trabajo {storage_dir} no se puedo crear y no existe")

        #subp.run(['sh', f"{BASE_DIR}src/nce/shared/util_get_files_from_nce.sh", remote_dir, f"{self.storage_dir}/{base_config['codigo_medicion']}", str_to_filter])
        pattern = re.compile(str_to_filter)
        for local_file in os.listdir(storage_dir):
            if pattern.match(local_file):
                os.unlink(f"{storage_dir}/{local_file}")

        csv_files = self.sftp_service.get_files(remote_dir, storage_dir, str_to_filter, True)

        if len(csv_files) == 0:
            raise Exception(f"No se encontro archivos en '{remote_dir}' para '{str_to_filter}'")

        #str_to_filter = str_to_filter.replace('*', '.*')
        #csv_files = os.listdir(storage_dir)
        #pattern = re.compile(str_to_filter)
        #csv_files = list(filter(lambda filename: pattern.match(filename) is not None, csv_files))

        #load config
        cvffields_by_fieldconfig = {}
        template = ''
        bindings = {}
        valid_cvffields = []
        skip_lines = 2

        if len(csv_files) > 0:
            filename = csv_files[0]['file']
            with open(f"{storage_dir}/{filename}", newline='', encoding='UTF-8') as csvfile:
                reader = csv.reader(csvfile)
                row = next(reader)
                headers = next(reader)
                cvffields_by_fieldconfig = self.get_csvfields_by_field(fields, headers)
                template, bindings = self.shared_repo.get_insert_template_and_bindings(base_config['nombre_tabla'], cvffields_by_fieldconfig)
                valid_cvffields = list(filter(lambda fld: cvffields_by_fieldconfig[fld] != None, list(cvffields_by_fieldconfig)))
        
        registros_to_insert = []
        counter_by_files = []
        
        """map_by_datatype = {
            'VARCHAR2': lambda v: v,
            'DATE': lambda v: v,
            'NUMBER': lambda v: None if v == '' else float(v),
        }"""
        for row_file in csv_files:
            filename = row_file['file']
            with open(f"{storage_dir}/{filename}", newline='', encoding='UTF-8') as csvfile:
                reader = csv.reader(csvfile)
                #reader = csv.DictReader(csvfile)
                #row = next(reader)
                #headers = next(reader)

                counter = 0 - skip_lines
                for row in reader:
                    counter += 1
                    if counter <=0:
                        continue
                    row_to_add = {}
                    for field in valid_cvffields:
                        value = row[cvffields_by_fieldconfig[field]['index']]
                        # row_to_add[cvffields_by_fieldconfig[field]['columna_smart']] = map_by_datatype[cvffields_by_fieldconfig[field]['tipo_dato']](value)
                        row_to_add[cvffields_by_fieldconfig[field]['columna_smart']] = value
                    registros_to_insert.append(row_to_add)
                counter_by_files.append({'file': row_file, 'counter': counter})

        is_succesfull = False
        error = None

        if len(registros_to_insert) > 0:
            self.shared_repo.db.map_data_by_bindings(registros_to_insert, bindings)
            if base_config['del_duplicados'] == 1:
                registros_to_insert = self._del_duplicados(registros_to_insert, ['deviceid','devicename','resourcename','collectiontime','granularityperiod'])
            
            print(f"[{base_config['nombre_tabla']}]: {fecha} {fecha2} - {len(registros_to_insert)}")
            try:
                count_validation = self.shared_repo.count_where_collectiontime_between(base_config['nombre_tabla'], base_config['granularidad'], 'collectiontime', fecha, fecha2)
                if count_validation > 0:
                    self.shared_repo.delete_where_collectiontime_between(base_config['nombre_tabla'], base_config['granularidad'], 'collectiontime', fecha, fecha2)
                self.shared_repo.insert_from_array(template, bindings, registros_to_insert)
                print(f"registros: {len(registros_to_insert)}")
                is_succesfull = True
            except BaseException as e:
                error = e
            except:
                is_succesfull = False

        #print(csv_files)
        for row in csv_files:
            filename = row['file']
            os.unlink(f"{storage_dir}/{filename}")
        os.rmdir(storage_dir)
        
        end_time = datetime.datetime.now()

        diff_delta = end_time - start_time
        diff_per_file = diff_delta / (len(counter_by_files) if len(counter_by_files) == 1 else len(counter_by_files)+1)
        fecha_ini = start_time
        fecha_fin = start_time + diff_per_file
        control_format = '%Y-%m-%d %H:%M:%S'

        for row in counter_by_files:
            file = row['file']
            self.control_carga_repo.save_carga(
                queue_id,
                file['updated']+'|'+file['file'],
                row['counter'] if is_succesfull == True else 0,
                row['counter'],
                fecha_ini,
                fecha_fin,
                'CARGADO' if is_succesfull == True else 'ERROR',
                '',
                fecha
            )
            fecha_ini += diff_per_file
            fecha_fin += diff_per_file

        # envio de error
        if is_succesfull == False:
            if error is not None:
                raise error
            else:
                raise Exception("Ocurrio un error no identificado al realizar la carga")
        else:
            self.shared_repo.createSuccessEvent(queue_id, fecha)

    def get_csvfields_by_field(self, fields, headers):
        cvffields_by_fieldconfig = {}
        index = 0
        for head in headers:
            finded = False
            for fld in fields:
                if fld['columna_100g'].lower() == head.lower():
                    fld['index'] = index
                    cvffields_by_fieldconfig[head] = fld
                    finded = True
            if not finded:
                cvffields_by_fieldconfig[head] = None
            index += 1
        return cvffields_by_fieldconfig

    def event_handler(self, event):
        self.__guard(event)
        event_formats_by_alias = {'dxd': '%Y-%m-%d', 'hxh': '%Y-%m-%d %H', 'mxm': '%Y-%m-%d %H:%M'}
        date_format = DTFORMAT_BY_ALIAS[event['msg_body']['format']]
        queue_id = event['queue_id']
        mediciones = event['msg_body']['mediciones']
        fecha1 = datetime.datetime.strptime(event['msg_body']['fec_ini'], date_format)
        self.execute(queue_id, mediciones, fecha1, event['msg_body']['format'])

    def __guard(self, event):
        msg_body_keys = event['msg_body'].keys()
        if 'mediciones' not in msg_body_keys or ('fec_ini' not in msg_body_keys) or ('format' not in msg_body_keys):
            raise Exception("Error no se encontro el atributo 'mediciones', 'fec_ini' o 'format'")

        if type(event['msg_body']['mediciones']) != type([]):
            raise Exception("Las mediciones deven ser una lista")

        if event['msg_body']['format'] not in list(DTFORMAT_BY_ALIAS):
            raise Exception(f"Formato '{event['msg_body']['format']}' no valido")

        

        

