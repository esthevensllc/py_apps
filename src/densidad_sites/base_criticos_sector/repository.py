from src.shared.database.ClickHouseDB import ClickHouseDB

class OracleSourceCriticosSectorRepository:
    def __init__(self, db):
        self.db = db

    def reload_sectores_4g_sem(self, date):
        str_date = date.strftime("%Y-%m-%d")
        self.db.callproc("PK_MAPA_SITES.SP_sectores_4g_sem(TO_DATE(:p_fecha, 'yyyy-mm-dd'))", {'p_fecha': str_date})

    def get_sectores_4g_sem(self):
        sql = "SELECT anio, semana, codigo, sector, prioridad_sector_mx, bandera, azimuth, longitud, latitud, ubigeo FROM ranreport_sectores_4g_sem"
        return self.db.fetch(sql)

    def get_semana_from_date(self, date):
        str_date = date.strftime("%Y-%m-%d")
        sql = f"SELECT ANO, SEMANA FROM SMMICS WHERE FEC_INI <= TO_DATE('{str_date}', 'yyyy-mm-dd') AND TO_DATE('{str_date}', 'yyyy-mm-dd') <= FEC_FIN"
        result = self.db.fetch(sql)
        if len(result) == 0:
            return {"anio": None, "semana": None}
        return {"anio": result[0][0], "semana": result[0][1]}


class ClickhouseCriticosSectorRepository:
    def __init__(self, db):
        self.db = db

    def insert_sectores_4g_sem(self, anio, semana, registros_to_insert):
        bindings = [
            {"name": "anio", "type": ClickHouseDB.INTEGER},
            {"name": "semana", "type": ClickHouseDB.INTEGER},
            {"name": "codigo", "type": ClickHouseDB.STRING},
            {"name": "sector", "type": ClickHouseDB.STRING},
            {"name": "prioridad_sector_mx", "type": ClickHouseDB.INTEGER},
            {"name": "bandera", "type": ClickHouseDB.INTEGER},
            {"name": "azimuth", "type": ClickHouseDB.INTEGER},
            {"name": "longitud", "type": ClickHouseDB.FLOAT},
            {"name": "latitud", "type": ClickHouseDB.FLOAT},
            {"name": "ubigeo", "type": ClickHouseDB.INTEGER}
        ]

        params = {'p_anio': anio, 'p_semana': semana}
        self.db.query("ALTER TABLE ranreport.sectores_4g_sem DELETE WHERE anio = {p_anio:Int64} and semana = {p_semana:Int64}", params)
        
        config = {'template': 'ranreport.sectores_4g_sem', 'bindings': bindings, 'row_type': 'array', 'limit_to_commit': 5000}
        self.db.insert(config, registros_to_insert)

    def reload_base_criticos_sector(self, anio, semana):
        self.db.query("TRUNCATE TABLE ranreport.base_criticos_sector_aux")
        self.db.query("insert into ranreport.base_criticos_sector_aux select * from ranreport.base_criticos_sector a")

        self.db.query("TRUNCATE TABLE ranreport.base_criticos_sector")

        params = {'p_anio': anio, 'p_semana': semana}
        self.db.query("""insert into ranreport.base_criticos_sector
        select case when a.codigo = '' then b.codigo else a.codigo end codigo,
            case when a.sector = '' then b.sector else a.sector end sector,
            case when b.azimuth is null then a.azimuth else b.azimuth end azimuth,
            case when b.latitud is null then a.latitud else b.latitud end latitud,
            case when b.longitud is null then a.longitud else b.longitud end longitud,
            case when b.prioridad_sector_mx is null then 7 else b.prioridad_sector_mx end prioridad_sector_mx,
            case when b.bandera is null then 4 else b.bandera end bandera
        from ranreport.base_criticos_sector_aux a
        full join (
        select * from ranreport.sectores_4g_sem
        where anio = {p_anio:Int64} and semana = {p_semana:Int64}
        ) b on a.codigo = b.codigo and a.sector=b.sector
        ;""", params)