from src.san.shared.services import BaseSanService
from shutil import rmtree
import xml.etree.ElementTree as ET
# import lxml.etree as ET
import datetime as dt
import json
import cx_Oracle
import os
import time
from src.shared.config import DTFORMAT_BY_ALIAS, TDINTERVAL_BY_ALIAS, STORAGE_DIR

class LoadDataFromConfig(BaseSanService):
    def __init__(self, db, repository, san_service, control_carga_repo):
        self.db = db
        self.repository = repository
        self.san_service = san_service
        self.control_carga_repo = control_carga_repo
        self.base_storage_dir = STORAGE_DIR+'san'

    def execute(self, config_id, fecha1, fecha2):
        fecha_recorrido = fecha1
        while fecha_recorrido < fecha2:
            self.__load_data_between(config_id, fecha_recorrido, fecha_recorrido + dt.timedelta(hours=1))
            fecha_recorrido = fecha_recorrido + dt.timedelta(hours=1)
            print("")

    def __load_data_between(self, config_id = None, fecha1 = None, fecha2 = None):
        is_succesfull = False
        error = None
        registros_count = 0
        work_dir = f"{self.base_storage_dir}/"+str(dt.datetime.now().timestamp())
        try:
            os.makedirs(work_dir)
            start_time = dt.datetime.now()

            config = self.repository.find(config_id)
            if config is None:
                raise Exception(f"La configuracion '{config_id}' no existe")
            fields_config = self.repository.get_fields_by_id(config_id)
            if len(fields_config) == 0:
                raise Exception(f"La configuracion '{config_id}' no tiene campos activos")
            #print(fields_config)
            print(config['name'])
            print(f"{fecha1} - {fecha2}")

            registros_count = self.download_data(work_dir, fecha1, fecha2, config, fields_config)
            print(registros_count)

            #carga
            for i in range(len(fields_config)):
                fields_config[i]["index"] = i

            if config['type'] == 'statistics':
                fields_to_use = list(filter(lambda f: f['to_reload'] is not None, fields_config))
                date_field = fields_to_use[0]
                str_fecha1 = fecha1.strftime('%Y-%m-%d %H:%M:%S')
                str_fecha2 = fecha2.strftime('%Y-%m-%d %H:%M:%S')
                
                self.delete_data_between(config, date_field, str_fecha1, str_fecha2)

                list_dirs = os.listdir(work_dir)
                for file in list_dirs:
                    with open(f"{work_dir}/{file}", mode="r", encoding='UTF-8') as tempfile:
                        registros = json.loads(tempfile.read())
                        self.load_to_database(config, fields_config, registros)
                        registros = None
                    # print(f"uploaded {file}")
                    os.unlink(f"{work_dir}/{file}")
                os.rmdir(work_dir)
                
                is_succesfull = True
        except BaseException as e:
            error = e
            rmtree(work_dir)
        except:
            error = Exception("Ocurrio un error no identificado al realizar la carga")
            rmtree(work_dir)

        end_time = dt.datetime.now()
        
        self.control_carga_repo.save_carga(
            config['queue_id'],
            config['name'],
            registros_count if is_succesfull == True else 0,
            registros_count,
            start_time,
            end_time,
            'CARGADO' if is_succesfull == True else 'ERROR',
            str(error) if error is not None else None,
            fecha1
        )
        if is_succesfull == False:
            raise error
        
    def download_data(self, work_dir, fecha1, fecha2, config, fields_config):
        fields_to_map = []
        for index in list(range(len(fields_config))):
            field = fields_config[index]
            if field['map_with'] is not None:
                fields_to_map.append(index)

        registros_count = 0
        # loop 10 min
        fecha_recorrido = fecha1
        counter = 1
        while fecha_recorrido < fecha2:
            next_date = fecha_recorrido + dt.timedelta(minutes=10)
            if next_date > fecha2:
                next_date = fecha2
            registros = self.__get_data(config['query'], json.loads(config['root_data']), fecha_recorrido, next_date, fields_config)

            for i in range(len(registros)):
                array_row = registros[i]
                for field_index in fields_to_map:
                    try:
                        value = array_row[field_index]
                        row = {fields_config[field_index]['api_fieldname']: value}
                        value = eval(f"f\"{fields_config[field_index]['map_with']}\"")
                        array_row[field_index] = value
                    except BaseException as e:
                        print(f"index: {i}")
                        print(f"field_index: {field_index}")
                        print(f"value: {value}")
                        raise e

            with open(f"{work_dir}/part_{counter}.json", mode="w", encoding='UTF-8') as tempfile:
                tempfile.write(json.dumps(registros))

            registros_count += len(registros)
            registros = []
            print(f"{fecha_recorrido} - {next_date}")
            fecha_recorrido = next_date
            counter += 1
        return registros_count
            

    def __get_data(self, query, children_set_lvl, fecha1, fecha2, fields_config):
        #<requestID>bgp.PeerStats</requestID>
        #equipment.InterfaceStats
        fecha1_f1 = int(fecha1.timestamp()*1000)
        fecha2_f1 = int(fecha2.timestamp()*1000)
        params = {
            'fecha1_f1': fecha1_f1,
            'fecha2_f1': fecha2_f1
        }
        body = query.format(**params)
        response = self.san_service.invoke({'data': body})
        root = ET.fromstring(response.text)
        response = None

        for i in children_set_lvl:
            root = root[i]
        field_list = list(map(lambda r: r["api_fieldname"], fields_config))
        registros = self._map_entryset_to_row(root, map_with=field_list)
        root=None
        return registros

    def delete_data_between(self, config, date_field, str_fecha1, str_fecha2):
        query_validation = ""
        delete_template = ""
        db_product_name = self.db.getDatabaseProductName()
        if db_product_name == "oracle":
            query_validation = f"""SELECT COUNT(*) FROM {config['tablename']}
            WHERE TO_DATE(:fecha1, 'yyyy-mm-dd hh24:mi:ss') <= {date_field['fieldname']}
            AND {date_field['fieldname']} < TO_DATE(:fecha2, 'yyyy-mm-dd hh24:mi:ss')"""

            delete_template = f"""DELETE FROM {config['tablename']}
            WHERE TO_DATE('{str_fecha1}', 'yyyy-mm-dd hh24:mi:ss') <= {date_field['fieldname']}
            AND {date_field['fieldname']} < TO_DATE('{str_fecha2}', 'yyyy-mm-dd hh24:mi:ss')"""
        elif db_product_name == "clickhouse":
            query_validation = f"""SELECT count(*) FROM {config['tablename']}
            WHERE toDateTime({{fecha1:String}}) <= {date_field['fieldname']}
            AND {date_field['fieldname']} < toDateTime({{fecha2:String}})"""

            str_partition = str_fecha1.replace("-", "").replace(" ", "")[:10]
            delete_template = f"ALTER TABLE {config['tablename']} drop partition 'P_{str_partition}'"
        count_validation = self.db.fetch(query_validation, {"fecha1": str_fecha1, "fecha2": str_fecha2})
        count_validation = count_validation[0][0]
        if count_validation > 0:
            self.db.query(delete_template)

    def load_to_database(self, config, fields_config, registros):
        # fields_to_use = list(filter(lambda f: f['to_reload'] is not None, fields_config))
        str_fields = ', '.join(list(map(lambda r: r['fieldname'], fields_config)))
        str_bind_fields = ', '.join(list(map(lambda r: f":{r['index']+1}" if r['type'] != 'date' else f"TO_DATE(:{r['index']+1}, 'yyyy-mm-dd hh24:mi:ss')", fields_config)))
        # bindings = {}
        bindings = []
        datatypes_by_db = {
            "oracle": {"number": cx_Oracle.NUMBER, "int": cx_Oracle.NUMBER, "varchar2": cx_Oracle.STRING, "date": cx_Oracle.STRING},
            "clickhouse": {"number": "decimal", "int": "int", "varchar2": "string", "date": "datetime"}
        }

        insert_template = ""
        db_product_name = self.db.getDatabaseProductName()

        db_types = datatypes_by_db[db_product_name]
        
        if db_product_name == "oracle":
            for f in fields_config:
                bindings.append(db_types[f['type']])
            insert_template = f"INSERT INTO {config['tablename']}({str_fields}) VALUES ({str_bind_fields})"
        elif db_product_name == "clickhouse":
            for f in fields_config:
                bindings.append({"type": db_types[f['type']], "name": f['api_fieldname']})
            insert_template = config['tablename']

        insert_config = {'template': insert_template, 'bindings': bindings, 'row_type': 'array', 'limit_to_commit': config['limit_to_commit']}
        registros = self.db.map_data_by_bindings(registros, bindings)
        # print(registros[0])
        # print(bindings)

        if db_product_name == "oracle":
            self.db.exec_batch(insert_config, registros)
        elif db_product_name == "clickhouse":
            self.db.insert(insert_config, registros)

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


class SanEventProducer:
    def __init__(self, db):
        self.db = db

    def execute(self):
        print("san event producer")
        self.db.callproc("PK_PADM_QUEUE.SP_SAM_PRODUCER", {})

class ClickHouseSanEventProducer:
    def __init__(self, db):
        self.db = db

    def execute(self):
        print("san event producer")
        self.db.callproc("PK_PADM_QUEUE.SP_CH_SAM_PRODUCER", {})            
