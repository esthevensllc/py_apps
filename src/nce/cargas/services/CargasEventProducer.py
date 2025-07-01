from src.nce.cargas.services.BaseGenericEventProducer import BaseGenericEventProducer
from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer
from src.shared.batch.finder import SftpFinder
from src.shared.database.SFTPConnect import SFTPConnect
import re

@DeprecationWarning
class CargasEventProducerLegacy:
    def __init__(self, repository, generic_event_producer):
        self.repository = repository
        self.generic_event_producer = generic_event_producer
        self.filter_med = ['PM_IG64']

    def execute(self):
        mediciones_config = self.repository.get()
        #mediciones_config = list(filter(lambda row: row['codigo_medicion'] in self.filter_med, mediciones_config))
        for row in mediciones_config:
            medicion_granularidad = f"{row['codigo_medicion']}_{row['granularidad']}"
            self.generic_event_producer.set_config(
                f'nce.{medicion_granularidad}_min'.lower(),
                f'nce.{medicion_granularidad}_min'.lower(),
                medicion_granularidad
            )
            self.generic_event_producer.execute()

class NceSftpWrapper(SFTPConnect):
    def __init__(self, sftp_service, cache_service):
        super().__init__()
        self.sftp_service = sftp_service
        self.cache_service = cache_service
        self.ttl_seconds = 10 * 60
    
    def get_filenames(self, work_dir, str_pattern):
        cache_key = 'nce'+work_dir.replace('/', '.')
        filenames = self.cache_service.get(cache_key)
        if filenames is None:
            filenames = self.sftp_service.get_filenames(work_dir)
            self.cache_service.set(cache_key, filenames, self.ttl_seconds)
        pattern = re.compile(str_pattern)
        return list(filter(lambda filename: pattern.match(filename) is not None, filenames))

class CargasEventProducer(RemoteConnectEventProducer):
    def __init__(self, sftp_service, repository, control_carga_repo, queue_service, cache_service):
        super().__init__(sftp_service, control_carga_repo, queue_service)
        self.repository = repository
        self.finder = SftpFinder(NceSftpWrapper(sftp_service, cache_service))

    def get_cargas_config(self, group_id=None):
        mapped_rows = []
        if group_id is not None:
            cargas = self.repository.get_by_group_id(group_id)
        else:
            cargas = self.repository.get()
        for index in range(len(cargas)):
            config = cargas[index]
            medicion_granularidad = f"{config['codigo_medicion']}_{config['granularidad']}"
            mapped_config = {
                'id': index+1,
                'name': medicion_granularidad,
                'server_id': 'nce',
                'work_dir': '/hfs_public/nbi/text/pfm_output/{str_date}',
                'wk_date_format': '%Y%m%d',
                'wk_loop_time': '{"days": 1}',
                'file_pattern': f"{medicion_granularidad}_([0-9]{{12}})_[0-9]+.csv",
                'file_date_format': '%Y%m%d%H%M',
                'queue_id': f'nce.{medicion_granularidad}_min'.lower(),
                'status': 1,
                'files_permission': None,
                'search_time_ago': '{"hours": 20}',
                'steps': None,
                'event_format': 'mxm',
                'files': []
            }
            mapped_rows.append(mapped_config)
        return mapped_rows

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        return self.finder.execute(config, dt_fecha1, dt_fecha2)

@DeprecationWarning
class ClickHouseCargasEventProducerLegacy:
    def __init__(self, repository, generic_event_producer):
        self.repository = repository
        self.generic_event_producer = generic_event_producer

    def execute(self):
        mediciones_config = self.repository.get()
        #mediciones_config = list(filter(lambda row: row['codigo_medicion'] in self.filter_med, mediciones_config))
        for row in mediciones_config:
            medicion_granularidad = f"{row['codigo_medicion']}_{row['granularidad']}"
            self.generic_event_producer.set_config(
                f'ch_nce.{medicion_granularidad}_min'.lower(),
                f'ch_nce.{medicion_granularidad}_min'.lower(),
                medicion_granularidad
            )
            self.generic_event_producer.execute()


class ClickHouseCargasEventProducer(RemoteConnectEventProducer):
    def __init__(self, sftp_service, repository, control_carga_repo, queue_service, cache_service):
        super().__init__(sftp_service, control_carga_repo, queue_service)
        self.repository = repository
        self.finder = SftpFinder(NceSftpWrapper(sftp_service, cache_service))

    def get_cargas_config(self, group_id=None):
        mapped_rows = []
        if group_id is not None:
            cargas = self.repository.get_by_group_id(group_id)
        else:
            cargas = self.repository.get()
        for index in range(len(cargas)):
            config = cargas[index]
            medicion_granularidad = f"{config['codigo_medicion']}_{config['granularidad']}"
            mapped_config = {
                'id': index+1,
                'name': medicion_granularidad,
                'server_id': 'nce',
                'work_dir': '/hfs_public/nbi/text/pfm_output/{str_date}',
                'wk_date_format': '%Y%m%d',
                'wk_loop_time': '{"days": 1}',
                'file_pattern': f"{medicion_granularidad}_([0-9]{{12}})_[0-9]+.csv",
                'file_date_format': '%Y%m%d%H%M',
                'queue_id': f'ch_nce.{medicion_granularidad}_min'.lower(),
                'status': 1,
                'files_permission': None,
                'search_time_ago': '{"hours": 20}',
                'steps': None,
                'event_format': 'mxm',
                'files': []
            }
            mapped_rows.append(mapped_config)
        return mapped_rows

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        return self.finder.execute(config, dt_fecha1, dt_fecha2)
