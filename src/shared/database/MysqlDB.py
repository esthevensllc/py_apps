import mysql.connector

class MysqlDB:

    def __init__(self):
        self.db = {'BSSOSS_standby': {'host': "172.19.255.49", 'user': "root", 'password': "P@SSWORD", 'db': "BSSOSS"}}
        self.db['BSSOSS'] = {'host': "172.19.255.48", 'user': "root", 'password': "P@SSWORD", 'db': "BSSOSS"}
        self.db['U2000'] = {'host': "172.19.255.48", 'user': "root", 'password': "P@SSWORD", 'db': "U2000"}
        self.db['U2000_standby'] = {'host': "172.19.255.49", 'user': "root", 'password': "P@SSWORD", 'db': "U2000"}
        self.connection = 'default'
        self.connections = {}
        self.con = None

    def useConnection(self, connection):
        self.connection = connection

    def __connect__(self):
        if self.connection not in list(self.connections):
            config = self.db[self.connection]
            connection = mysql.connector.connect(host=config["host"], user=config["user"], password=config["password"], db=config["db"])
            self.connections[self.connection] = connection
            return connection
        return self.connections[self.connection]

    def __disconnect__(self):
        for key in self.connections.keys():
            self.connections[key].close()
        self.connections = {}

    def close(self):
        self.__disconnect__()

    def fetch(self, sql):
        connection = self.__connect__()
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result

    def fetch_as_df(self, sql, df_fields):
        resp = self.fetch(sql)
        registros = []
        for row in resp:
            row_to_add = {}
            for i in range(len(row)):
                row_to_add[df_fields[i]] = row[i]
            registros.append(row_to_add)
        return registros

    def execute(self, sql):
        connection = self.__connect__()
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.close()
    
    def callproc(self, sql, args):
        connection = self.__connect__()
        cursor = connection.cursor()
        cursor.callproc(sql, args)
        result = cursor.stored_results()
        cursor.close()
        return result