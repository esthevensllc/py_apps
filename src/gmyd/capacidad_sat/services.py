import datetime as dt
class LoadCapacidadSat:
    def __init__(self, repository, sqlserver_service, db):
        self.repository = repository
        self.sqlserver_service = sqlserver_service
        self.db = db

    def execute(self):
        print("Load_capacidad_sat")
        df_fields = ['codigo','sede','capacidad']
        registros = self.sqlserver_service.fetch_as_df("""select codigo, sede, capacidad from capacidad_sat""", df_fields)

        self.repository.delete_by_f_actualizacion(dt.datetime.now().strftime('%Y-%m-%d'))
        self.repository.insert_from_array(registros)

        self.db.callproc("pk_rtn_carga_sem.sp_chrg_rss_tx_porc_ocup_sat", {})
        
        print(f"registros: {len(registros)}")
