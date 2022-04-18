class Main_PM_IG7511Repository:
    def __init__(self, db):
        self.db = db
        self.limit_to_commit = 1000

    def createFromArray(self, registros_to_insert):
        sql = ""
        insert_into_template = "INSERT INTO PRTLTX_CALIDAD_MYSQL(DIA, HORA, COLLECTIONTIME, DEVICENAME, DELAY, PKLOSS, jitteravg, jittermax) VALUES (TO_DATE('{}', 'YYYY-MM-DD'), {}, TO_DATE('{}', 'YYYY-MM-DD HH24:MI:SS'),'{}', {}, {}, {}, {})"

        self.db.insert_from_array(insert_into_template, registros_to_insert)

    def deleteWhereCollectiontimeBetweenExceptLast(self, fecha_ini, fecha_fin):
        sql = "DELETE FROM PRTLTX_CALIDAD_MYSQL WHERE COLLECTIONTIME >= TO_DATE('{}', 'DD/MM/YYYY') AND COLLECTIONTIME < TO_DATE('{}', 'DD/MM/YYYY')".format(fecha_ini, fecha_fin)
        return self.db.query(sql)

    def reloadResumen(self, mes_ini, mes_fin):
        sql = "BEGIN PK_PRTLTX_ALARMA.SP_LOAD_PRTLTX_CALIDAD_DET(TO_DATE('{}', 'DD/MM/YYYY'), TO_DATE('{}', 'DD/MM/YYYY')); END;".format(mes_ini, mes_fin)
        # self.db.query(sql)
