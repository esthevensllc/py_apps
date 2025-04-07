SITE_ON_AIR_REPO = 'src.gmyd.sites_on_air.SiteOnAirRepository'
LOAD_SITES_ON_AIR = 'src.gmyd.sites_on_air.LoadSitesOnAir'

RESUMEN_PACKETLOSS_REPO = 'src.gmyd.resumen_packetloss.ResumenPacketLossRepository'
LOAD_RESUMEN_PACKETLOSS = 'src.gmyd.resumen_packetloss.LoadResumenPacketLoss'

CAPACIDAD_SAT_REPO = "src.gmyd.capacidad_sat.CapacidadSatRepository"
LOAD_CAPACIDAD_SAT = "src.gmyd.capacidad_sat.LoadCapacidadSat"

PEERS_REPO = "src.gmyd.peers.PeersRepository"
LOAD_PEERS = "src.gmyd.peers.LoadPeers"

SITES_REPO = "src.gmyd.sites_temp.SitesRepository"
LOAD_SITES = "src.gmyd.sites_temp.LoadSites"

LOAD_RESUMEN_DELAY = "src.gmyd.resumen_deday.LoadResumenDelay"
LOAD_LISTA_HOPS = "src.gmyd.lista_hops.LoadListaHops"

GMYD_CONFIG_REPO = "src.gmyd.reports.GMyDConfigRepository"
LOAD_GMYD_FROM_CONFIG = "src.gmyd.reports.LoadGMyDFromConfig"
GMYD_PRODUCER_FROM_CONFIG = "src.gmyd.reports.GMyDEventProducerFromConfig"
GMYD_CONSUMER_FROM_CONFIG = "src.gmyd.reports.GMyDEventConsumerFromConfig"

class GMyDAppProvider:
    def __init__(self, app_container):
        def import_site_on_air_repo(name):
            from src.gmyd.sites_on_air.repository import SiteOnAirRepository
            return SiteOnAirRepository(app_container.getInstance('dboracle'))
        app_container.bind(SITE_ON_AIR_REPO, import_site_on_air_repo)
        def import_load_sites_on_air(name):
            from src.gmyd.sites_on_air.services import LoadSitesOnAir
            return LoadSitesOnAir(*app_container.getInstancesInArray([SITE_ON_AIR_REPO, 'sqlserver']))
        app_container.bind(LOAD_SITES_ON_AIR, import_load_sites_on_air)
        
        #packetloss
        def import_resumen_packetloss_repo(name):
            from src.gmyd.resumen_packetloss.repository import ResumenPacketLossRepository
            return ResumenPacketLossRepository(app_container.getInstance('dboracle'))
        app_container.bind(RESUMEN_PACKETLOSS_REPO, import_resumen_packetloss_repo)
        def import_load_resumen_packetloss(name):
            from src.gmyd.resumen_packetloss.services import LoadResumenPacketLoss
            return LoadResumenPacketLoss(*app_container.getInstancesInArray([RESUMEN_PACKETLOSS_REPO, 'sqlserver']))
        app_container.bind(LOAD_RESUMEN_PACKETLOSS, import_load_resumen_packetloss)

        #capacidad_sat
        def import_capacidad_sat_repo(name):
            from src.gmyd.capacidad_sat.repository import CapacidadSatRepository
            return CapacidadSatRepository(app_container.getInstance('dboracle'))
        app_container.bind(CAPACIDAD_SAT_REPO, import_capacidad_sat_repo)
        def import_load_capacidad_sat(name):
            from src.gmyd.capacidad_sat.services import LoadCapacidadSat
            return LoadCapacidadSat(*app_container.getInstancesInArray([CAPACIDAD_SAT_REPO, 'sqlserver', 'dboracle']))
        app_container.bind(LOAD_CAPACIDAD_SAT, import_load_capacidad_sat)

        # peers
        def import_peers_repo(name):
            from src.gmyd.peers.repository import PeersRepository
            return PeersRepository(app_container.getInstance('dboracle'))
        app_container.bind(PEERS_REPO, import_peers_repo)
        def import_load_peers(name):
            from src.gmyd.peers.services import LoadPeers
            dboptda = app_container.getInstance('dbprovider').getConnection("DBOPTDA")
            return LoadPeers(app_container.getInstance(PEERS_REPO), dboptda)
        app_container.bind(LOAD_PEERS, import_load_peers)

        # sites
        def import_sites_repo(name):
            from src.gmyd.sites_temp.repository import SitesRepository
            return SitesRepository(app_container.getInstance('dboracle'))
        app_container.bind(SITES_REPO, import_sites_repo)
        def import_load_sites(name):
            from src.gmyd.sites_temp.services import LoadSites
            dboptda = app_container.getInstance('dbprovider').getConnection("DBOPTDA")
            return LoadSites(app_container.getInstance(SITES_REPO), dboptda)
        app_container.bind(LOAD_SITES, import_load_sites)

        def import_gmyd_config_repo(name):
            from src.gmyd.reports.repository import InMemoryGMyDConfigRepository
            return InMemoryGMyDConfigRepository(app_container.getInstance('dboracle'))
        app_container.bind(GMYD_CONFIG_REPO, import_gmyd_config_repo)
        
        def import_load_gmyd_from_config(name):
            from src.gmyd.reports.services import LoadGMyDFromConfig
            deps = app_container.getInstancesInArray(["dboracle", GMYD_CONFIG_REPO, "dboracle", "control_carga_repo"])
            return LoadGMyDFromConfig(*deps)
        app_container.bind(LOAD_GMYD_FROM_CONFIG, import_load_gmyd_from_config)

        def import_gmyd_producer_from_config(name):
            from src.gmyd.reports.services import GMyDEventProducerFromConfig
            deps = app_container.getInstancesInArray([GMYD_CONFIG_REPO, "dboracle", "control_carga_repo", "queue_service"])
            return GMyDEventProducerFromConfig(*deps)
        app_container.bind(GMYD_PRODUCER_FROM_CONFIG, import_gmyd_producer_from_config)
        
        def import_gmyd_consumer_from_config(name):
            from src.gmyd.reports.services import GMyDEventConsumerFromConfig
            queue_service = app_container.getInstance('queue_service')
            notification_service = app_container.getInstance('notification_service')
            repository = app_container.getInstance(GMYD_CONFIG_REPO)
            return GMyDEventConsumerFromConfig(queue_service, app_container, notification_service, repository)
        app_container.bind(GMYD_CONSUMER_FROM_CONFIG, import_gmyd_consumer_from_config)

        def import_load_resumen_delay(name):
            from src.gmyd.resumen_delay.services import LoadResumenDelay
            oracle = app_container.getInstance("dbprovider").getConnection("default")
            sqlserver = app_container.getInstance("dbprovider").getConnection("mssql_dbrtu")
            return LoadResumenDelay(oracle, sqlserver)
        app_container.bind(LOAD_RESUMEN_DELAY, import_load_resumen_delay)

        def import_load_lista_hops(name):
            from src.gmyd.lista_hops.services import LoadListaHops
            from src.gmyd.lista_hops.repository import ListaHopsRepository
            oracle = app_container.getInstance("dbprovider").getConnection("default")
            dboptda = app_container.getInstance('dbprovider').getConnection("DBOPTDA")
            return LoadListaHops(ListaHopsRepository(oracle), dboptda)
        app_container.bind(LOAD_LISTA_HOPS, import_load_lista_hops)
