UPDATE_INFO_SOTS = 'src.factibilidad_fija.sots.UpdateInfoSots'

class FactibilidadFijaAppProvider:
    def __init__(self, app_container):
        def update_info_sots(name):
            from src.factibilidad_fija.sots.services import UpdateInfoSots
            return UpdateInfoSots(app_container.getInstance("dboracle"), app_container.getInstance("busquedadir_api"))
        app_container.bind(UPDATE_INFO_SOTS, update_info_sots)
