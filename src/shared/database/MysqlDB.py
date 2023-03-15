import mysql.connector

class MysqlDB:

    def __init__(self):
        self.db = {'default': {'host': "172.19.255.48", 'user': "root", 'password': "P@SSWORD", 'db': "BSSOSS"}}
        self.db['U2000'] = {'host': "172.19.255.48", 'user': "root", 'password': "P@SSWORD", 'db': "U2000"}
        self.connection = 'default'
        self.con = None

    def useConnection(self, connection):
        self.connection = connection

    def __connect__(self):
        dbConfig = self.db[self.connection]
        self.con = mysql.connector.connect(host=dbConfig["host"], user=dbConfig["user"], password=dbConfig["password"], db=dbConfig["db"])
        self.con._open_connection()
        self.cur = self.con.cursor()

    def __disconnect__(self):
        if not self.con is None:
            self.con.close()

    def fetch(self, sql):
        self.__connect__()
        self.cur.execute(sql)
        result = self.cur.fetchall()
        self.__disconnect__()
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
        self.__connect__()
        self.cur.execute(sql)
        self.__disconnect__()
    
    def callproc(self, sql, args):
        self.__connect__()
        self.cur.callproc(sql, args)
        result = self.cur.stored_results()
        self.__disconnect__()
        return result