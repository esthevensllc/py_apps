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
            return LoadPeers(*app_container.getInstancesInArray([PEERS_REPO]))
        app_container.bind(LOAD_PEERS, import_load_peers)

        # sites
        def import_sites_repo(name):
            from src.gmyd.sites_temp.repository import SitesRepository
            return SitesRepository(app_container.getInstance('dboracle'))
        app_container.bind(SITES_REPO, import_sites_repo)
        def import_load_sites(name):
            from src.gmyd.sites_temp.services import LoadSites
            return LoadSites(*app_container.getInstancesInArray([SITES_REPO]))
        app_container.bind(LOAD_SITES, import_load_sites)
