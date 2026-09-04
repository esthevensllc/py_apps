import cx_Oracle
import clickhouse_connect


class Controller:
    def __init__ (self):
        self.db = cx_Oracle.connect("SMART", "Sm4rt12$$", "scan-smart.tim.com.pe:1521/SMART")
        self.cursor = self.db.cursor()
        self.clickhouse_db =  clickhouse_connect.get_client(host='172.19.242.109',
                                                        username='desempenio_red',
                                                        password='D3s3mp3n1oR3d',
                                                        connect_timeout=3
                                                        )

    def executeQueryOutputArray(self, query):
        retorno = []
        for row in self.cursor.execute(query).fetchall():
            retorno.append(row)
        return retorno


    def obtenerDatos(self):
        QUERY_DATA = '''
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
        '''
        df = self.executeQueryOutputArray(QUERY_DATA)
        return df
        
    
    def borrarDatos(self):
        p_command = 'DELETE FROM ranreport.maestro_tec_mapa_densidad_site WHERE 1=1'
        try:
            self.clickhouse_db.command(p_command)
            print('Se ejecuto la query correctamente')
        except Exception as e:
            raise Exception(f'ClickHouseDB.execute: {e}')
    
    def InsertarDF(self,df):
        self.clickhouse_db.insert('ranreport.maestro_tec_mapa_densidad_site', 
        df, column_names=['codigo','latitud','longitud','ubigeo','portadoras_2g','portadoras_3g','portadoras_5g','portadoras_4g','portadoras_4g_1900','portadoras_4g_2600','portadoras_4g_700','portadoras_4g_otros','th_dl_4g','th_ul_4g','th_dl_3g','th_ul_3g'])

