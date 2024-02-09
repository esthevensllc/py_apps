class LoadListaHops:
    def __init__(self, repository, dboptda):
        self.repository = repository
        self.dboptda = dboptda

    def execute(self):
        print("dboptda.view_tbl_hops")
        registros = self.get_data_from_source()

        self.repository.delete_all()
        self.repository.insert_from_array(registros)
        print(f"registros: {len(registros)}")
    
    def get_data_from_source(self):
        result = self.dboptda.fetch("""SELECT
        ID, CODIGO_NE, NOMBRE_NE, CODIGO_FE, NOMBRE_FE, ALTURA_TORRE_NE, ALTURA_PREDIO_NE,
        ALTURA_MW_NE, ALTURA_TORRE_FE, ALTURA_PREDIO_FE, ALTURA_MW_FE, EQUIPO_NE, EQUIPO_FE,
        MARCA_IDU_ORIGEN, MARCA_IDU_DESTINO, ANTENA_NE, ANTENA_FE, DIAMETRO_NE, DIAMETRO_FE,
        GANANCIA_NE, GANANCIA_FE, ANTENA_VENDOR_ORIGEN, ANTENA_VENDOR_DESTINO, POLARIZACION,
        CONFIGURACION, AZIMUTH_NE, AZIMUTH_FE, FECHA_ULTIMO_CAMBIO, FECHA_CREACION, FECHA_APROBACION,
        FECHA_BAJA, RESP_ULTIMO_CAMBIO, RESP_CREACION, RESP_APROBACION, RESP_BAJA, PROYECTO, ESTADO,
        DISTANCIA, ID_MTC_ORIGEN, ID_MTC_DESTINO, RESOLUCION, FREC_NE, FREC_FE, FREC, BW_MTC, PTX,
        CAPACIDAD
        from dboptda.view_tbl_hops""")
        data = []
        for row in result:
            data.append({
                'ID': row[0],
                'CODIGO_NE': row[1],
                'NOMBRE_NE': row[2],
                'CODIGO_FE': row[3],
                'NOMBRE_FE': row[4],
                'ALTURA_TORRE_NE': row[5],
                'ALTURA_PREDIO_NE': row[6],
                'ALTURA_MW_NE': row[7],
                'ALTURA_TORRE_FE': row[8],
                'ALTURA_PREDIO_FE': row[9],
                'ALTURA_MW_FE': row[10],
                'EQUIPO_NE': row[11],
                'EQUIPO_FE': row[12],
                'MARCA_IDU_ORIGEN': row[13],
                'MARCA_IDU_DESTINO': row[14],
                'ANTENA_NE': row[15],
                'ANTENA_FE': row[16],
                'DIAMETRO_NE': row[17],
                'DIAMETRO_FE': row[18],
                'GANANCIA_NE': row[19],
                'GANANCIA_FE': row[20],
                'ANTENA_VENDOR_ORIGEN': row[21],
                'ANTENA_VENDOR_DESTINO': row[22],
                'POLARIZACION': row[23],
                'CONFIGURACION': row[24],
                'AZIMUTH_NE': row[25],
                'AZIMUTH_FE': row[26],
                'FECHA_ULTIMO_CAMBIO': row[27],
                'FECHA_CREACION': row[28],
                'FECHA_APROBACION': row[29],
                'FECHA_BAJA': row[30],
                'RESP_ULTIMO_CAMBIO': row[31],
                'RESP_CREACION': row[32],
                'RESP_APROBACION': row[33],
                'RESP_BAJA': row[34],
                'PROYECTO': row[35],
                'ESTADO': row[36],
                'DISTANCIA': row[37],
                'ID_MTC_ORIGEN': row[38],
                'ID_MTC_DESTINO': row[39],
                'RESOLUCION': row[40],
                'FREC_NE': row[41],
                'FREC_FE': row[42],
                'FREC': row[43],
                'BW_MTC': row[44],
                'PTX': row[45],
                'CAPACIDAD': row[46]
            })
        return data