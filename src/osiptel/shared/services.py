REPORTE_OSIPTEL = 'src.osiptel.reporte_osiptel'

class OsiptelAppProvider:
    def __init__(self, app_container):
        def generar_reporte_osiptel(name):
            from src.osiptel.reporte_osiptel.services import GenerarReporteOsiptelCsv
            return GenerarReporteOsiptelCsv(app_container.getInstance('dboracle'))
        app_container.bind(REPORTE_OSIPTEL, generar_reporte_osiptel)
