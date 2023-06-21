import clickhouse_connect
from clickhouse_connect.driver.client import Client
import datetime as dt

class ClickHouseDB:
    INTEGER = "int"
    DECIMAL = "decimal"
    FLOAT = "float"
    STRING = "string"
    DATETIME = "datetime"

    def __init__(self):
        self.connections_config = {
            "clickhouse_dn02": {'host': "172.19.242.57", 'user': "nifi", 'password': "nifi", 'port': 8123, 'database': 'nce'},
            "clickhouse_nce": {'host': "172.19.242.109", 'user': "desempenio_red", 'password': "D3s3mp3n1oR3d", 'port': 8123, 'database': 'nce'},
            "clickhouse_san": {'host': "172.19.242.109", 'user': "desempenio_red", 'password': "D3s3mp3n1oR3d", 'port': 8123, 'database': 'sam_nokia'},
            "clickhouse_apic": {'host': "172.19.242.109", 'user': "desempenio_red", 'password': "D3s3mp3n1oR3d", 'port': 8123, 'database': 'aci_fabric'},
        }
        self.connection_key = ''
        self.db_connections = {}

    def getDatabaseProductName(self):
        return "clickhouse"

    def useConnection(self, connection_key):
        self.connection_key = connection_key
        self.connect()

    def connect(self) -> Client:
        if self.connection_key not in self.db_connections.keys():
            config = self.connections_config[self.connection_key]
            client = clickhouse_connect.get_client(**config)
            self.db_connections[self.connection_key] = client
        return self.db_connections[self.connection_key]

    def getReference(self):
        return self.connect()
    
    def fetch(self, sql, params={}):
        result = self.getReference().query(sql, parameters=params)
        return result.result_rows
    
    def query(self, sql, params={}):
        return self.getReference().command(sql, parameters=params)

    def insert(self, config, registros_to_insert):
        bindings = config["bindings"]
        fields = []
        columns = []
        date_fields = []
        if type(bindings) == type([]):
            fields = list(range(len(bindings)))
            for index in range(len(bindings)):
                columns.append(bindings[index]["name"])
                if bindings[index]["type"] == "datetime":
                    date_fields.append(index)
        else:
            fields = bindings.keys()
            for index in bindings.keys():
                if type({}) != type(bindings[index]):
                    columns.append(index)
                    if bindings[index] == "datetime":
                        date_fields.append(index)
                else:
                    if bindings[index].get("name") is None:
                        columns.append(index)
                        if bindings[index]["type"] == "datetime":
                            date_fields.append(index)
                    else:
                        columns.append(bindings[index]["name"])
                        if bindings[index]["type"] == "datetime":
                            date_fields.append(bindings[index]["name"])

        # date_fields = list(filter(lambda key: bindings[key] == "datetime", bindings.keys()))
        for i in range(len(registros_to_insert)):
            for field in date_fields:
                registros_to_insert[i][field] = dt.datetime.strptime(registros_to_insert[i][field], '%Y-%m-%d %H:%M:%S')
        
        if config["row_type"] == "object":
            datarange = range(len(registros_to_insert))
            for i in datarange:
                row = []
                for field in fields:
                    row.append(registros_to_insert[i][field])
                registros_to_insert[i] = row

        self.getReference().insert(config["template"], registros_to_insert, column_names=columns)

    def map_rowdata_to_array(self, data, bindings):
        bindings = config["bindings"]
        fields = bindings.keys()
        
        datarange = range(len(data))
        for i in datarange:
            row = []
            for field in fields:
                row.append(data[i][field])
            data[i] = row
        return data


    def map_data_by_bindings(self, data, bindings, map_keys = {}, fill_data=False):
        range_list = range(len(data))

        if type(bindings) == type([]):
            bindings_types = []
            for index in range(len(bindings)):
                bindings_types.append(bindings[index]["type"])

            bindings_keys = range(len(bindings))
            for i in range_list:
                row_to_add = []
                for field in bindings_keys:
                    value = data[i][field]
                    if bindings_types[field] == "decimal" or bindings_types[field] == "float":
                        if value != '' and value != None:
                            value = float(value)
                        elif value == '':
                            value = None
                        row_to_add.append(value)
                    elif bindings_types[field] == "int":
                        if value != '' and value != None:
                            value = int(value)
                        elif value == '':
                            value = None
                        row_to_add.append(value)
                    else:
                        row_to_add.append(value)
                data[i] = row_to_add
            return data
        else:
            bindings_types = {}
            for index in bindings.keys():
                if type({}) == type(bindings[index]):
                    bindings_types[index] = bindings[index]["type"]
                else:
                    bindings_types[index] = bindings[index]

            bindings_keys = list(bindings)
            for i in range_list:
                row_to_add = {}
                for field in bindings_keys:
                    value = data[i][field]
                    if bindings_types[field] == "decimal" or bindings_types[field] == "float":
                        if value != '' and value != None:
                            value = float(value)
                        elif value == '':
                            value = None
                        row_to_add[field] = value
                    elif bindings_types[field] == "int":
                        if value != '' and value != None:
                            value = int(value)
                        elif value == '':
                            value = None
                        row_to_add.append(value)
                    else:
                        row_to_add[field] = value
                data[i] = row_to_add
            return data
