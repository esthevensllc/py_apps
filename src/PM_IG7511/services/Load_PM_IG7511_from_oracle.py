# import src.shared.U2000.PM_IG7511Repository
from src.shared.services import AppService
from src.shared.database.MysqlDB import MysqlDB
from src.shared.database.OracleDB import OracleDB
from src.shared.U2000.PM_IG7511.repository.PM_IG7511Repository import PM_IG7511Repository
from src.PM_IG7511.repository import Main_PM_IG7511Repository

class Load_PM_IG7511_from_oracle(AppService):
    def __init__(self, mysql_db, oracle_db):
        self.PM_IG7511Service = PM_IG7511Repository(mysql_db)
        self.repository = Main_PM_IG7511Repository(oracle_db)

    def execute(self, v_fecha_ini, v_fecha_fin):
        # inicio
        # v_fecha_ini = datetime.datetime.strptime(str_fecha_ini, '%d/%m/%Y')
        # v_fecha_fin = datetime.datetime.strptime(str_fecha_fin, '%d/%m/%Y')

        str_fecha_ini = v_fecha_ini.strftime('%d/%m/%Y')
        str_fecha_fin = v_fecha_fin.strftime('%d/%m/%Y')

        print("Recarga de \"PRTLTX_CALIDAD_MYSQL\" de MySql a Oracle ({} - {})".format(str_fecha_ini, str_fecha_fin))

        self.loopEachDay(v_fecha_ini, v_fecha_fin, self.reload_handler)
        print("Recarga completada ({} - {})".format(str_fecha_ini, str_fecha_fin))
    
    def reload_handler(self, fecha_ini, fecha_fin):
        v_fecha_ini = fecha_ini.strftime('%d/%m/%Y')
        v_fecha_fin = fecha_fin.strftime('%d/%m/%Y')
        print("({} - {})".format(v_fecha_ini, v_fecha_fin))

        registros_to_insert = self.PM_IG7511Service.getWhereCollectiontimeBetweenExceptLast(v_fecha_ini, v_fecha_fin)

        self.repository.deleteWhereCollectiontimeBetweenExceptLast(v_fecha_ini, v_fecha_fin)
        self.repository.createFromArray(registros_to_insert)

        print("Registros insertados = {}".format(len(registros_to_insert)))
