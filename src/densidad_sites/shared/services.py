LOAD_BASE_CRITICOS_SECTOR = 'densidad_sites.base_criticos_sector.LoadBaseCriticosSector'

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
