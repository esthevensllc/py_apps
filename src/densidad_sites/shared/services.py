LOAD_BASE_CRITICOS_SECTOR = 'densidad_sites.base_criticos_sector.LoadBaseCriticosSector'
LOAD_SITIOS_IPT = 'densidad_sites.sitios_ipt.LoadSitiosIPT'
LOAD_MAESTRO_TEC_MAPA = 'densidad_sites.maestro_tec_mapa.LoadMaestroTecMapa'

class DensidadSitesAppProvider:
    def __init__(self, app_container):
        def load_base_criticos_sector(name):
            from src.densidad_sites.base_criticos_sector.services import LoadBaseCriticosSector
            from src.densidad_sites.base_criticos_sector.repository import (
                OracleSourceCriticosSectorRepository,
                ClickhouseCriticosSectorRepository
            )
            source_repo = OracleSourceCriticosSectorRepository(app_container.getInstance("dboracle"))
            clickhouse = app_container.getInstance("clickhouse")
            clickhouse.useConnection("clickhouse_nce")
            repo = ClickhouseCriticosSectorRepository(clickhouse)
            return LoadBaseCriticosSector(source_repo, repo)
        app_container.bind(LOAD_BASE_CRITICOS_SECTOR, load_base_criticos_sector)

        def load_sitios_ipt(name):
            from src.densidad_sites.sitios_ipt.services import LoadSitiosIPT
            from src.densidad_sites.sitios_ipt.repository import (SitiosIPTRepository)
            clickhouse = app_container.getInstance("clickhouse")
            clickhouse.useConnection("clickhouse_nce")
            repo = SitiosIPTRepository(clickhouse)
            return LoadSitiosIPT(repo, app_container.getInstance("dboracle"))
        app_container.bind(LOAD_SITIOS_IPT, load_sitios_ipt)

        def load_maestro_tec_mapa(name):
            from src.densidad_sites.maestro_tec_mapa.services import LoadMaestroTecMapa
            clickhouse = app_container.getInstance("clickhouse")
            clickhouse.useConnection("clickhouse_nce")
            return LoadMaestroTecMapa(app_container.getInstance("dboracle"), clickhouse)
        app_container.bind(LOAD_MAESTRO_TEC_MAPA, load_maestro_tec_mapa)
