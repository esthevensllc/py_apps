from src.shared.database.OracleDB import OracleDB
from src.shared.database.ClickHouseDB import ClickHouseDB
from src.shared.database.SQLServerDB import SQLServerDB

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
            "mssql_dbrtu": {'host': "LIMDBSQLF03", 'user': "USRSMART", 'password': "Claro321", 'db': "DBRTU", "driver": "mssql"}
        }

    def getConnection(self, key):
        if key not in list(self.connections_config):
            raise Exception(f"La conexión {key} no esta configurada")

        if key not in list(self.instances):
            config = self.connections_config[key].copy()
            config["key"] = key
            if config["driver"] == "oracle":
                self.instances[key] = OracleDB()
                self.instances[key].connectWithConfig(config)
            elif config["driver"] == "clickhouse":
                self.instances[key] = ClickHouseDB()
                self.instances[key].connectWithConfig(config)
            elif config["driver"] == "mssql":
                self.instances[key] = SQLServerDB()
                self.instances[key].connectWithConfig(config)
            else:
                raise Exception(f"El driver {config['driver']} no esta soportado")
        return self.instances[key]
