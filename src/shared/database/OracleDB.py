"""
    Oracle database connection wrapper
    @author: esthevensllc
"""
import cx_Oracle
import os
#cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_19_11")

class OracleDB:

    def __init__(self):
        self.limit_to_commit = 1000
        self.connections_config = {
            "default": {'host': os.getenv('DB_HOST'), 'user': os.getenv('DB_USER'), 'password': os.getenv('DB_PASSWORD'), 'port': 1521, 'servicename': os.getenv('DB_DATABASE')},
            "DBOPTDA": {'host': os.getenv('DB_DBOPTDA_HOST'), 'user': os.getenv('DB_DBOPTDA_USER'), 'password': os.getenv('DB_DBOPTDA_PASSWORD'), 'port': 1521, 'servicename': os.getenv('DB_DBOPTDA_DATABASE')},
        }
        self.connection_key = 'default'
        self.db_connections = {}
        self.connect()

    def getDatabaseProductName(self):
        return "oracle"

    def useConnection(self, connection_key = "default"):
        self.connection_key = connection_key
        self.connect()

    def connect(self):
        if self.connection_key not in self.db_connections.keys():
            config = self.connections_config[self.connection_key]            
            tns = cx_Oracle.makedsn(config["host"], config["port"], service_name=config["servicename"])
            client = cx_Oracle.connect(config["user"], config["password"], tns)
            self.connection = client
            self.db_connections[self.connection_key] = client
        else:
            self.connection = self.db_connections[self.connection_key]
        return self.db_connections[self.connection_key]

    def connectWithConfig(self, key, config):
        self.connections_config[key] = config
        self.useConnection(key)

    def getReference(self):
        return self.connect()

    def __connect__(self):
        self.connection = cx_Oracle.connect(self.user, self.password, self.tns)
        self.cur = self.connection.cursor()

    def fetch(self, sql, params={}):
        # self.__connect__()
        cur = self.connection.cursor()
        cur.execute(sql, params)
        result = cur.fetchall()
        cur.close()
        # self.__disconnect__()
        return result

    def query(self, sql, params={}):
        cur = self.connection.cursor()
        # self.__connect__()
        cur.prepare(sql)
        cur.execute(sql, params)
        self.connection.commit()
        # self.__disconnect__()
        cur.close()

    def callproc(self, procedure, params):
        cur = self.connection.cursor()
        cur.execute(f"begin {procedure}; end;", params)
        cur.close()

    def __disconnect__(self):
        pass
        # self.cur.close()

    def insert_from_array(self, insert_template, registros_to_insert):
        sql = ""
        commit_count=1
        length_registros = len(registros_to_insert)
        for index in range(length_registros):
            sql += insert_template.format(*registros_to_insert[index])+";"
            if commit_count == self.limit_to_commit or (index+1) == length_registros:
                sql += "commit;"
                sql = "begin {} commit; end;".format(sql)
                self.query(sql)
                print('commit {}'.format(index+1))
                commit_count = 0
                sql = ""
            commit_count = commit_count+1

    def save_from_array(self, insert_template, registros_to_insert, row_type = "array", limit_to_commit = -1):
        def array_resolver(template, params):
            new_params = []
            for param in params:
                new_params.append(repr(param))
            return template.format(*params)
        
        def obj_resolver(template, params):
            keys = params.keys()
            new_params = {}
            for index in keys:
                new_params[index] = repr(params[index])
            return template.format(**params)
        
        row_resolver = {"array": array_resolver, "object": obj_resolver}
        sql = ""
        commit_count=1
        length_registros = len(registros_to_insert)
        if limit_to_commit == -1:
            limit_to_commit = self.limit_to_commit

        for index in range(length_registros):
            sql += row_resolver[row_type](insert_template, registros_to_insert[index])+";"
            if commit_count == limit_to_commit or (index+1) == length_registros:
                sql += "commit;"
                sql = "begin {} commit; end;".format(sql)
                self.query(sql)
                print('commit {}'.format(index+1))
                commit_count = 0
                sql = ""
            commit_count = commit_count+1
    
    def save(self, template, data, data_type = 'array'):
        cur = self.connection.cursor()
        if data_type == 'array':
            cur.execute(template, data)
        else:
            cur.execute(template, **data)
        self.connection.commit()
        cur.close()
    
    def save_from_array2(self, config, registros_to_insert):
        cursor = self.connection.cursor()
        # cursor.setinputsizes(id = cx_Oracle.NUMBER, template = cx_Oracle.CLOB, nombre = cx_Oracle.STRING)
        template = config['template']
        bindings = config['bindings']
        row_type = config['row_type'] if "row_type" in config else "array"
        limit_to_commit = config['limit_to_commit'] if "limit_to_commit" in config else self.limit_to_commit

        if row_type == "array":
            cursor.setinputsizes(*bindings)
        elif row_type == "object":
            cursor.setinputsizes(**bindings)

        def array_resolver(template, params):
            cursor.execute(template, params)
        
        def obj_resolver(template, params):
            cursor.execute(template, **params)
        
        row_resolver = {"array": array_resolver, "object": obj_resolver}

        sql = []
        commit_count=1
        length_registros = len(registros_to_insert)
        index_part = 0

        cursor.prepare(template)

        for index in range(length_registros):
            #sql.append( registros_to_insert[index])
            # row_resolver[row_type](template, registros_to_insert[index])
            if commit_count == limit_to_commit or (index+1) == length_registros:
                #cursor.executemany(None, sql, batcherrors=True)
                cursor.executemany(None, registros_to_insert[index_part:index+1], batcherrors=True)
                error_messages = []
                for error in cursor.getbatcherrors():
                    print("Error", error.message, "at row offset", error.offset)
                    error_messages.append("Error {} at row offset {}".format(error.message, error.offset))
                    break
                if len(error_messages) == 0:
                    self.connection.commit()
                else:
                    self.connection.rollback()
                    raise Exception(', '.join(error_messages))
                # print('commit {}'.format(index+1))
                commit_count = 0
                index_part = index+1
                sql = []
            commit_count = commit_count+1
        
        cursor.close()

        # sql = "INSERT INTO PSO_0DATA_19_6748_PLANOS_TEMP(ID, NOMBRE, GEOMETRY) VALUES (:id, :nombre, :template)"
        """sql = "INSERT INTO PSO_0DATA_19_6748_PLANOS_TEMP(ID, NOMBRE, GEOMETRY) VALUES (:1, :2, :3)"
        template = '{"type": "MultiPolygon", "coordinates": [[[[-77.083570360893, -12.086537579274], [-77.083899619043, -12.086386980465], [-77.08383555107, -12.086248910786], [-77.08400103544, -12.086177355593], [-77.084075998626, -12.086145070675], [-77.08414781788, -12.086110007585], [-77.084237869991, -12.086069475426], [-77.084335480277, -12.086020662129], [-77.084307469448, -12.085961222477], [-77.084476363938, -12.085879428719], [-77.084590760771, -12.085828139615], [-77.084564010342, -12.08576543692], [-77.084562887389, -12.085762733992], [-77.084712157932, -12.085696541998], [-77.085891219281, -12.085161965343], [-77.085849775435, -12.085075603584], [-77.086086527457, -12.084969168771], [-77.086132736069, -12.084947492693], [-77.087022291643, -12.084550380954], [-77.086563764677, -12.083591023816], [-77.085361871554, -12.084034220145], [-77.08525223015, -12.083738963272], [-77.085251497617, -12.083739239902], [-77.084994226395, -12.083828565537], [-77.084996570415, -12.083834784061], [-77.08487101835, -12.083880372645], [-77.084273090949, -12.084035517292], [-77.084067885358, -12.0840887523], [-77.083993279715, -12.084107839206], [-77.083957283834, -12.084120129395], [-77.083888360395, -12.084137727621], [-77.083069614892, -12.084358151621], [-77.083080103047, -12.084396212722], [-77.082827344275, -12.084463631154], [-77.082979197189, -12.08508727939], [-77.083570360893, -12.086537579274]]]]}'
        # self.cur.execute(sql, template=template, nombre='LMSM034', id=36323508)
        # self.cur.execute(sql, [36323508, 'LMSM034', template])
        # self.cur.execute(sql, [2, 'LMSM034', template])
        self.connection.commit()"""

    def exec_batch(self, config, registros_to_insert):
        cursor = self.connection.cursor()

        template = config['template']
        bindings = config['bindings']
        row_type = config['row_type'] if "row_type" in config else "array"

        if row_type == "array":
            cursor.setinputsizes(*bindings)
        elif row_type == "object":
            cursor.setinputsizes(**bindings)

        cursor.prepare(template)
        cursor.executemany(None, registros_to_insert, batcherrors=True)

        error_messages = []
        for error in cursor.getbatcherrors():
            error_messages.append(f"[{error.offset}]{error.message}")
            print(f"[{error.offset}]{error.message}")
        
        if len(error_messages) == 0:
            self.connection.commit()
            print(f"commit {len(registros_to_insert)}")
        else:
            self.connection.rollback()
            raise Exception(', '.join(error_messages))
        cursor.close()

    def map_data_by_bindings(self, data, bindings, map_keys = {}, fill_data=False):
        range_list = range(len(data))
        bindings_keys = list(bindings)

        if type(bindings) == type([]):
            bindings_keys = range(len(bindings))
            for i in range_list:
                row_to_add = []
                for field in bindings_keys:
                    if bindings[field] == cx_Oracle.NUMBER:
                        value = data[i][field]
                        if value != '' and value != None:
                            value = float(value)
                        elif value == '':
                            value = None
                        row_to_add.append(value)
                    else:
                        value = data[i][field]
                        row_to_add.append(value)
                data[i] = row_to_add
            return data
        none_by_field = {}
        for i in range_list:
            row_to_add = {}
            for field in bindings_keys:
                if fill_data:
                    if data[i].get(field) is None:
                        if none_by_field.get(field) is None:
                            none_by_field[field] = 1
                        else:
                            none_by_field[field] += 1
                        data[i][field] = None
                if bindings[field] == cx_Oracle.NUMBER:
                    value = data[i][field]
                    if value != '' and value != None:
                        try:
                            value = float(value)
                        except BaseException as e:
                            print(i, data[i])
                            raise e

                    elif value == '':
                        value = None
                    if map_keys.get(field) is None:
                        row_to_add[field] = value
                    else:
                        row_to_add[map_keys.get(field)] = value
                else:
                    value = data[i][field]
                    if map_keys.get(field) is None:
                        row_to_add[field] = value
                    else:
                        row_to_add[map_keys.get(field)] = value

            data[i] = row_to_add
        print(f"none values:", none_by_field)
        return data

    def close(self):
        for key in self.db_connections.keys():
            self.db_connections[key].close()
        self.db_connections = {}