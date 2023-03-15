import cx_Oracle

class ResumenPacketLossRepository:
    def __init__(self, db):
        self.db = db
        self.table = 'TX_RESUMEN_PKLOSS_GMD'

    def delete_by_f_actualizacion(self, f_actualizacion):
        query = f"DELETE FROM {self.table} WHERE F_ACTUALIZACION = TO_DATE('{f_actualizacion}', 'YYYY-MM-DD')"
        self.db.query(query)

    def insert_from_array(self, registros_to_insert):
        #template = f"INSERT INTO {self.table}(F_ACTUALIZACION, FECHA_FC, PROYECTO, AREA_RESPONSABLE, SITE, REGION, NODE_NAME, RNC_NAME, TIPO_MEDIO_TX, SUB_REGION, DEPARTAMENTO, PROVINCIA, DISTRITO, SITIO_USUARIOS_VIVEN, TRAFICO_VOZ_ERL, LATITUD, LONGITUD, TRAFICO_PS_GB, ESTADO, PRIORIDAD, SCORE_PKLOSS, PERCENT_PKLOSS, NHPL, FECHA_INSERCION, FECHA_ACTUALIZACION, AGREGADOR_PUERTO, AREA, RESPONSABLE, PROBLEMA, INCIDENCIA, CAUSA, SOLUCION, MOTIVO_DERIVACION) VALUES (TRUNC(SYSDATE, 'DD'), :fecha_fc, :proyecto, :area_responsable, :site, :region, :node_name, :rnc_name, :tipo_medio_tx, :sub_region, :departamento, :provincia, :distrito, :sitio_usuarios_viven, :trafico_voz_erl, :latitud, :longitud, :trafico_ps_gb, :estado, :prioridad, :score_pkloss, :percent_pkloss, :nhpl, :fecha_insercion, :fecha_actualizacion, :agregador_puerto, :area, :responsable, :problema, :incidencia, :causa, :solucion, :motivo_derivacion)"
        """bindings = {
            'fecha_fc': cx_Oracle.STRING,
            'proyecto': cx_Oracle.STRING,
            'area_responsable': cx_Oracle.STRING,
            'site': cx_Oracle.STRING,
            'region': cx_Oracle.STRING,
            'node_name': cx_Oracle.STRING,
            'rnc_name': cx_Oracle.STRING,
            'tipo_medio_tx': cx_Oracle.STRING,
            'sub_region': cx_Oracle.STRING,
            'departamento': cx_Oracle.STRING,
            'provincia': cx_Oracle.STRING,
            'distrito': cx_Oracle.STRING,
            'sitio_usuarios_viven': cx_Oracle.STRING,
            'trafico_voz_erl': cx_Oracle.STRING,
            'latitud': cx_Oracle.STRING,
            'longitud': cx_Oracle.STRING,
            'trafico_ps_gb': cx_Oracle.STRING,
            'estado': cx_Oracle.STRING,
            'prioridad': cx_Oracle.STRING,
            'score_pkloss': cx_Oracle.STRING,
            'percent_pkloss': cx_Oracle.STRING,
            'nhpl': cx_Oracle.STRING,
            'fecha_insercion': cx_Oracle.STRING,
            'fecha_actualizacion': cx_Oracle.STRING,
            'agregador_puerto': cx_Oracle.STRING,
            'area': cx_Oracle.STRING,
            'responsable': cx_Oracle.STRING,
            'problema': cx_Oracle.STRING,
            'incidencia': cx_Oracle.STRING,
            'causa': cx_Oracle.STRING,
            'solucion': cx_Oracle.STRING,
            'motivo_derivacion': cx_Oracle.STRING,
            #'estado_planif': cx_Oracle.STRING
        }"""

        template = f"INSERT INTO {self.table}(F_ACTUALIZACION, fecha_fc,proyecto,area_responsable,site,region,node_name,problema,incidencia,causa,solucion,motivo_derivacion,estado_planif,pap_gmd) VALUES (TO_DATE(:f_actualizacion, 'yyyy-mm-dd'), :fecha_fc, :proyecto, :area_responsable, :site, :region, :node_name, :problema, :incidencia, :causa, :solucion, :motivo_derivacion, :estado_planif, :pap)"
        bindings = {
            'f_actualizacion': cx_Oracle.STRING,
            'fecha_fc': cx_Oracle.STRING,
            'proyecto': cx_Oracle.STRING,
            'area_responsable': cx_Oracle.STRING,
            'site': cx_Oracle.STRING,
            'region': cx_Oracle.STRING,
            'node_name': cx_Oracle.STRING,
            'problema': cx_Oracle.STRING,
            'incidencia': cx_Oracle.STRING,
            'causa': cx_Oracle.STRING,
            'solucion': cx_Oracle.STRING,
            'motivo_derivacion': cx_Oracle.STRING,
            'estado_planif': cx_Oracle.STRING,
            'pap': cx_Oracle.STRING
        }
        
        config = {'template': template, 'bindings': bindings, 'row_type': 'object', 'limit_to_commit': 5000}
        self.db.save_from_array2(config, registros_to_insert)