import mysql.connector

class MariaDB:

    def __init__(self):
        self.connections_config = {}
        self.connection_key = ''
        self.db_connections = {}

    def getDatabaseProductName(self):
        return "mariadb"

    def useConnection(self, connection_key):
        self.connection_key = connection_key
        self.connect()

    def connect(self):
        if self.connection_key not in self.db_connections.keys():
            config = self.connections_config[self.connection_key]
            client = mysql.connector.connect(host=config["host"], user=config["user"], password=config["password"], db=config["db"])
            client._open_connection()
            self.db_connections[self.connection_key] = client
        return self.db_connections[self.connection_key]

    def connectWithConfig(self, key, config):
        self.connections_config[key] = config
        self.useConnection(key)

    def getReference(self):
        return self.connect()
    
    def fetch(self, sql, params={}):
        cursor = self.getReference().cursor()
        cursor.execute(sql, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    def close(self):
        for key in self.db_connections.keys():
            self.db_connections[key].close()
        self.db_connections = {}