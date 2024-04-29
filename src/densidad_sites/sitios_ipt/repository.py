from src.shared.database.ClickHouseDB import ClickHouseDB

class SitiosIPTRepository:
    def __init__(self, db):
        self.db = db
        self.table = "ranreport.sitios_ipt"

    def delete_all(self):
        self.db.query(f'truncate table {self.table}')

    def insert_from_array(self, registros):
        bindings = {
            "id_sitio": ClickHouseDB.INTEGER,
            "codigosite": ClickHouseDB.STRING,
            "nombresite": ClickHouseDB.STRING,
            "latitud": ClickHouseDB.FLOAT,
            "longitud": ClickHouseDB.FLOAT,
            "proveedor": ClickHouseDB.STRING,
            "on_air_site": ClickHouseDB.DATETIME,
            "departamento": ClickHouseDB.STRING,
            "provincia": ClickHouseDB.STRING,
            "distrito": ClickHouseDB.STRING,
            "tec4g": ClickHouseDB.STRING,
            "tec3g": ClickHouseDB.STRING,
        }
        
        config = {'template': self.table, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 5000}
        self.db.insert(config, registros)