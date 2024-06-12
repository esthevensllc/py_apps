from src.shared.database.ClickHouseDB import ClickHouseDB

class LoadMaestroTecMapa:
    def __init__(self, oracle, ch):
        self.oracle = oracle
        self.ch = ch

    def execute(self):
        data = self.get_data()
        print(f"ranreport.maestro_tec_mapa_densidad_site: {len(data)}")
        self.load_to_clickhouse(data)

    def get_data(self):
        query = """
        select CODIGO,
        LATITUD,
        LONGITUD,
        UBIGEO,
        PORTADORAS_2G,
        PORTADORAS_3G,
        PORTADORAS_5G,
        PORTADORAS_4G,
        PORTADORAS_4G_1900,
        PORTADORAS_4G_2600,
        PORTADORAS_4G_700,
        PORTADORAS_4G_OTROS,
        TH_DL_4G,
        TH_UL_4G,
        TH_DL_3G,
        TH_UL_3G
        from maestro_tec_mapa_densidad_site
        """
        return self.oracle.fetch(query)

    def load_to_clickhouse(self, data):
        self.ch.query("truncate table ranreport.maestro_tec_mapa_densidad_site")
        bindings = [
            {"name": "codigo", "type": ClickHouseDB.STRING},
            {"name": "latitud", "type": ClickHouseDB.FLOAT},
            {"name": "longitud", "type": ClickHouseDB.FLOAT},
            {"name": "ubigeo", "type": ClickHouseDB.STRING},
            {"name": "portadoras_2g", "type": ClickHouseDB.FLOAT},
            {"name": "portadoras_3g", "type": ClickHouseDB.FLOAT},
            {"name": "portadoras_5g", "type": ClickHouseDB.FLOAT},
            {"name": "portadoras_4g", "type": ClickHouseDB.FLOAT},
            {"name": "portadoras_4g_1900", "type": ClickHouseDB.FLOAT},
            {"name": "portadoras_4g_2600", "type": ClickHouseDB.FLOAT},
            {"name": "portadoras_4g_700", "type": ClickHouseDB.FLOAT},
            {"name": "portadoras_4g_otros", "type": ClickHouseDB.FLOAT},
            {"name": "th_dl_4g", "type": ClickHouseDB.FLOAT},
            {"name": "th_ul_4g", "type": ClickHouseDB.FLOAT},
            {"name": "th_dl_3g", "type": ClickHouseDB.FLOAT},
            {"name": "th_ul_3g", "type": ClickHouseDB.FLOAT},
        ]
        config = {'template': 'ranreport.maestro_tec_mapa_densidad_site', 'bindings': bindings, 'row_type': 'array', 'limit_to_commit': 5000}
        self.ch.insert(config, data)