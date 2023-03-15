import datetime as dt
class LoadResumenPacketLoss:
    def __init__(self, repository, sqlserver_service):
        self.repository = repository
        self.sqlserver_service = sqlserver_service

    def execute(self, fecha=dt.datetime.now().strftime('%Y-%m-%d')):
        #df_fields = 'fecha_fc,proyecto,area_responsable,site,region,node_name,rnc_name,tipo_medio_tx,sub_region,departamento,provincia,distrito,sitio_usuarios_viven,trafico_voz_erl,latitud,longitud,trafico_ps_gb,estado,prioridad,score_pkloss,percent_pkloss,nhpl,fecha_insercion,fecha_actualizacion,agregador_puerto,area,responsable,problema,incidencia,causa,solucion,motivo_derivacion'.split(',')
        #registros = self.sqlserver_service.fetch_as_df("select [FECHA FC], PROYECTO, [AREA RESPONSABLE], SITE, REGION, NODE_NAME, NULL RNC_NAME, NULL [TIPO MEDIO TX], NULL SUB_REGION, NULL DEPARTAMENTO, NULL PROVINCIA, NULL DISTRITO, NULL SITIO_USUARIOS_VIVEN, NULL TRAFICO_VOZ_ERL, NULL LATITUD, NULL LONGITUD, NULL TRAFICO_PS_GB, NULL ESTADO, NULL PRIORIDAD, NULL SCORE_PKLOSS, PERCENT_PKLOSS, NHPL, CONVERT(VARCHAR(20), FECHA_INSERCION, 120) as FECHA_INSERCION, CONVERT(VARCHAR(20), FECHA_ACTUALIZACION, 120) FECHA_ACTUALIZACION, [AGREGADOR - PUERTO], AREA, RESPONSABLE, PROBLEMA, INCIDENCIA, CAUSA, SOLUCION, MOTIVO_DERIVACION from dbo.resumen_packetloss$", df_fields)
        df_fields = 'fecha_fc,proyecto,area_responsable,site,region,node_name,problema,incidencia,causa,solucion,motivo_derivacion,estado_planif,pap'.split(',')
        registros = self.sqlserver_service.fetch_as_df("""select
        [FECHA FC], PROYECTO, [AREA RESPONSABLE], SITE, REGION, NODE_NAME,
        NULL PROBLEMA, NULL INCIDENCIA, NULL CAUSA, NULL SOLUCION, NULL MOTIVO_DERIVACION,
        NULL ESTADO_PLANIF, PAP
        from dbo.resumen_packetloss$""", df_fields)
        
        print(f"load_resumen_packetloss {len(registros)}")
        dt_fecha = dt.datetime.strptime(fecha, '%Y-%m-%d')
        for index in range(len(registros)):
            registros[index]['f_actualizacion'] = fecha

        print(f"Fecha recarga oracle: {fecha}")
        self.repository.delete_by_f_actualizacion(dt_fecha.strftime('%Y-%m-%d'))
        self.repository.insert_from_array(registros)