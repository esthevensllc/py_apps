import pyodbc
import re

class SQLServerDB:
    def __init__(self):
        self.db = {'default': {'host': "LIMDBSQLF03", 'user': "USRSMART", 'password': "Claro321", 'db': "DBRTU"}}
        self.connection = 'default'
        self.connections = {}
        self.driver = self.__get_drivername()

    def __get_drivername(self):
        p = re.compile('.*SQL Server.*')
        result = list(filter(lambda r: p.match(r) is not None, pyodbc.drivers()))
        if len(result)>0:
            return result[0]
        return None

    def useConnection(self, connection):
        self.connection = connection

    def __connect(self):
        if self.connection not in list(self.connections):
            config = self.db[self.connection]
            conexion = pyodbc.connect('DRIVER={'+self.driver+'};'+f"SERVER={config['host']};DATABASE={config['db']};UID={config['user']};PWD={config['password']};TrustServerCertificate=yes")
            self.connections[self.connection] = conexion
            return conexion
        return self.connections[self.connection]

    def fetch(self, sql):
        cn = self.__connect()
        cur = cn.cursor()
        cur.execute(sql)
        return cur.fetchall()

    def fetch_as_df(self, sql, df_fields):
        resp = self.fetch(sql)
        registros = []
        for row in resp:
            row_to_add = {}
            for i in range(len(row)):
                row_to_add[df_fields[i]] = row[i]
            registros.append(row_to_add)
        return registros