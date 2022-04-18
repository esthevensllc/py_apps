import src.shared.database.MysqlDB

class PM_IG7511Repository:
    def __init__(self, db):
        self.db = db
    
    def getWhereCollectiontimeBetweenExceptLast(self, fecha_ini, fecha_fin):
        sql = """
        select DATE(a.collectiontime) dia, HOUR(a.collectiontime) hora, a.collectiontime, a.devicename,
            AVG(avgtwowaydelay)/1000 delay,
            round(MAX(avgtwowaypacketlossratio),2) pkloss,
            AVG(avgtwowayjitter)/1000 jitteravg,
            MAX(maxtwowayjitter)/1000 jittermax
        FROM 	 PM_IG7510 a
        INNER JOIN PM_IG7511 b ON a.collectiontime = b.collectiontime AND a.devicename = b.devicename AND a.resourcename = b.resourcename
        WHERE a.collectiontime >= STR_TO_DATE('{}', '%d/%m/%Y') AND a.collectiontime < STR_TO_DATE('{}', '%d/%m/%Y')
        GROUP BY DATE(a.collectiontime), HOUR(a.collectiontime), a.collectiontime, a.devicename;
        """.format(fecha_ini, fecha_fin)
        return self.db.fetch(sql)
