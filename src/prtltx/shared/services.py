PRTLTX_ALARMA_REPO = 'src.prtltx.alarmas.services.PrtltxAlarmasRepository'
LOAD_ALARMAS = 'src.prtltx.alarmas.services.LoadPrtltxAlarmas'

class PrtltxAppProvider:
    def __init__(self, app_container):
        def import_PrtltxAlarmasRepository(name):
            from src.prtltx.alarmas.repository import PrtltxAlarmasRepository
            return PrtltxAlarmasRepository(app_container.getInstance('dboracle'))
        app_container.bind(PRTLTX_ALARMA_REPO, import_PrtltxAlarmasRepository)
        def import_load_alarmas(name):
            from src.prtltx.alarmas.services import LoadPrtltxAlarmas
            dependencies = app_container.getInstancesInArray([PRTLTX_ALARMA_REPO, 'dbmysql'])
            try:
                dependencies[1].useConnection('BSSOSS')
                dependencies[1].fetch("select now()")
            except:
                dependencies[1].useConnection('BSSOSS_standby')
                print("Carga desde base de datos en espera")
            return LoadPrtltxAlarmas(*dependencies)
        app_container.bind(LOAD_ALARMAS, import_load_alarmas)
        
        #packetloss
        