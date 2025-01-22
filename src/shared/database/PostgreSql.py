import psycopg2
import os
from sshtunnel import SSHTunnelForwarder

class PostgreSql:
    def __init__(self):
        self.connections_config = {}
        self.connection_key = ''
        self.db_connections = {}
        self.tunnel_db_connections = {}

    def getDatabaseProductName(self):
        return "postgres"

    def useConnection(self, connection_key):
        self.connection_key = connection_key
        self.connect()

    def connect(self):
        if self.connection_key not in self.db_connections.keys():
            config = self.connections_config[self.connection_key]
            client = None
            if config.get('sshtunnel') is not None:
                sshname_key = config.get('sshtunnel')
                tunnel = SSHTunnelForwarder(
                    (os.getenv(f'{sshname_key}_HOST'), int(os.getenv(f'{sshname_key}_PORT', 22))),
                    ssh_username=os.getenv(f'{sshname_key}_USERNAME'),
                    ssh_password=os.getenv(f'{sshname_key}_PASSWORD'),
                    remote_bind_address=(config['host'], config['port']),
                    local_bind_address=('127.0.0.1', 5433)
                )
                tunnel.start()
                client = psycopg2.connect(
                    host=tunnel.local_bind_host,
                    port=tunnel.local_bind_port,
                    user=config['user'],
                    password=config['password'],
                    database=config['database']
                )
                self.tunnel_db_connections[self.connection_key] = tunnel
            else:
                client = psycopg2.connect(**config)
            self.db_connections[self.connection_key] = client
        return self.db_connections[self.connection_key]

    def connectWithConfig(self, key, config):
        self.connections_config[key] = config
        self.useConnection(key)

    def getReference(self):
        return self.connect()

    def fetch(self, sql, params={}):
        with self.getReference().cursor() as cursor:
            if len(params.keys()) > 0:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return result

    def close(self):
        for key in self.db_connections.keys():
            self.db_connections[key].close()
            if self.tunnel_db_connections[key] and self.tunnel_db_connections[key].is_active:
                self.tunnel_db_connections[key].close()
        self.db_connections = {}
