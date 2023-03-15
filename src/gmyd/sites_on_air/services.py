class LoadSitesOnAir:
    def __init__(self, repository, sqlserver_service):
        self.repository = repository
        self.sqlserver_service = sqlserver_service

    def execute(self):
        df_fields = "tsoa_id,tsoa_codigo,tsoa_nombre,ttt_tipo,tsoa_direccion,tsoa_latitud,tsoa_longitud,tsoa_router_agreg,equipo,tsoa_estado,tte_id,tercero,satelital".split(',')
        registros = self.sqlserver_service.fetch_as_df("""
        SELECT B.TSOA_ID,
        B.TSOA_CODIGO,
        B.TSOA_NOMBRE,
        B.TTT_TIPO,
        B.TSOA_DIRECCION,
        B.TSOA_LATITUD,
        B.TSOA_LONGITUD,
        B.TSOA_ROUTER_AGREG,
        B.EQUIPO,
        B.TSOA_ESTADO,
        B.TTE_ID,
        COALESCE(C.TERCERO,0)TERCERO,
        CASE WHEN B.TTT_TIPO LIKE '%SAT%' THEN 1 ELSE 0 END SATELITAL
        FROM dbo.vw_tabla_sites_on_air B
        LEFT JOIN (SELECT E.*,1 'TERCERO'
        FROM dbo.vw_tabla_sites_on_air E
        WHERE E.TSOA_ROUTER_AGREG IN (SELECT S.TSOA_ROUTER_AGREG
        FROM(SELECT A.*,
        CASE WHEN UPPER(A.EQUIPO) LIKE '%AZTECA%' THEN 1
        WHEN UPPER(A.EQUIPO) LIKE '%TDP%' THEN 1
        WHEN UPPER(A.EQUIPO) LIKE '%GILAT%' THEN 1
        WHEN UPPER(A.EQUIPO) LIKE '%INTERNEXA%' THEN 1
        WHEN UPPER(A.TSOA_ROUTER_AGREG) LIKE '%AZTECA%' THEN 1
        WHEN UPPER(A.TSOA_ROUTER_AGREG) LIKE '%TDP%' THEN 1
        WHEN UPPER(A.TSOA_ROUTER_AGREG) LIKE '%GILAT%' THEN 1
        WHEN UPPER(A.TSOA_ROUTER_AGREG) LIKE '%INTERNEXA%' THEN 1
        ELSE 0 END ROUTER_OTRO
        FROM dbo.vw_tabla_sites_on_air A
        WHERE A.tsoa_estado='OPERATIVO') S
        WHERE S.ROUTER_OTRO = 1 AND S.TSOA_ROUTER_AGREG <> 'NULL')) C
        ON B.tsoa_id=C.TSOA_ID
        WHERE B.tsoa_estado='OPERATIVO'
        """, df_fields)
        #resp = self.sqlserver_service.fetch('select @@version')

        print("load_sites_on_air")

        self.repository.delete_all()
        self.repository.insert_from_array(registros)
        print(f"registros: {len(registros)}")