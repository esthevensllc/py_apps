import datetime
import calendar
from src.shared.services import AppService
from src.PM_IG7511.repository import Main_PM_IG7511Repository

# Recarga tabla resumen 'PRTLTX_CALIDAD_DET'
# usada para el dashboard de calidad  de 'PRONATEL TX' del portalregulatorio

class LoadResumenDetalle_PM_IG7511(AppService):
    def __init__(self,oracle_db):
        self.repository = Main_PM_IG7511Repository(oracle_db)

    # datetime
    def execute(self, mes_ini, mes_fin):
        print("Recarga de \"PRTLTX_CALIDAD_DET\" desde procedimiento ({} - {})".format(mes_ini, mes_fin))
        self.loopEachMonth(mes_ini, mes_fin, self.reload_handler)
        print("Recarga completada")
    
    def reload_handler(self, mes_ini, mes_fin):
        str_mes_ini = mes_ini.strftime('%d/%m/%Y')
        str_mes_fin = mes_fin.strftime('%d/%m/%Y')

        self.repository.reloadResumen(str_mes_ini, str_mes_fin)
        
        print("{} - {}".format(str_mes_ini, str_mes_fin))
    

