import os
from src.shared.database.OracleDB import OracleDB
from src.shared.database.ClickHouseDB import ClickHouseDB
from src.shared.database.SQLServerDB import SQLServerDB
from src.shared.database.MariaDB import MariaDB
# from src.shared.database.PostgreSql import PostgreSql

class DatabaseProvider:
    def __init__(self):
        self.instances = {}
        self.connections_config = {
            "default": {'host': "scan-smart", 'user': "SMART", 'password': "Sm4rt12$$", 'port': 1521, 'servicename': 'SMART', "driver": "oracle"},
            "desarrollo": {'host': "scan-smart", 'user': "desarrollo", 'password': "claro123", 'port': 1521, 'servicename': 'SMART', "driver": "oracle"},
            "DBOPTDA": {'host': "scan-fc", 'user': "USRSMART1", 'password': "Rm4O$u8p", 'port': 1521, 'servicename': 'DBOPTDA', "driver": "oracle"},
            "clickhouse_dn02": {'host': "172.19.242.57", 'user': "nifi", 'password': "nifi", 'port': 8123, 'database': 'nce', "driver": "clickhouse"},
            "clickhouse_nce": {'host': "172.19.242.109", 'user': "desempenio_red", 'password': "D3s3mp3n1oR3d", 'port': 8123, 'database': 'nce', "driver": "clickhouse"},
            "clickhouse_san": {'host': "172.19.242.109", 'user': "desempenio_red", 'password': "D3s3mp3n1oR3d", 'port': 8123, 'database': 'sam_nokia', "driver": "clickhouse"},
            "clickhouse_apic": {'host': "172.19.242.109", 'user': "desempenio_red", 'password': "D3s3mp3n1oR3d", 'port': 8123, 'database': 'aci_fabric', "driver": "clickhouse"},
            "mssql_dbrtu": {'host': "LIMDBSQLF03", 'user': "USRSMART", 'password': "Claro321", 'db': "DBRTU", "driver": "mssql"},
            "mariadb_alarmas": {'host': "172.19.216.92", 'user': "usr_desred", 'password': "037d6t", 'db': "bd_externo", "driver": "mariadb"},
            "pg_ipt": {'host': os.getenv('DB_IPT_HOST'), 'user': os.getenv('DB_IPT_USER'), 'password': os.getenv('DB_IPT_PASSWORD'), 'port': int(os.getenv('DB_IPT_PORT', 5432)), 'database': os.getenv('DB_IPT_DATABASE'), "driver": "postgresql"},
            "clickhouse_dn06": {'host': os.getenv('DB_DN06_HOST'), 'user': os.getenv('DB_DN06_USER'), 'password': os.getenv('DB_DN06_PASSWORD'), 'port': int(os.getenv('DB_DN06_PORT', 8123)), 'database': os.getenv('DB_DN06_DATABASE'), "driver": "clickhouse", "settings": {"max_block_size": 5000}},
        }

    def getConnection(self, key):
        if key not in list(self.connections_config):
            raise Exception(f"La conexión {key} no esta configurada")

        if key not in list(self.instances):
            config = self.connections_config[key].copy()
            driver = config["driver"]
            config.pop("driver")
            if driver == "oracle":
                self.instances[key] = OracleDB()
                self.instances[key].connectWithConfig(key, config)
            elif driver == "clickhouse":
                self.instances[key] = ClickHouseDB()
                self.instances[key].connectWithConfig(key, config)
            elif driver == "mssql":
                self.instances[key] = SQLServerDB()
                self.instances[key].connectWithConfig(key, config)
            elif driver == "mariadb":
                self.instances[key] = MariaDB()
                self.instances[key].connectWithConfig(key, config)
                # elif driver == "postgresql":
                #     self.instances[key] = PostgreSql()
                #     self.instances[key].connectWithConfig(key, config)
            else:
                raise Exception(f"El driver {config['driver']} no esta soportado")
        return self.instances[key]

    def closeConnections(self):
        for key in list(self.instances):
            self.instances[key].close()
