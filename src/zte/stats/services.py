from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.zte.shared.services import LOAD_ZTE_STATS_FROM_CONFIG
from src.shared.config import STORAGE_DIR
from src.shared.batch.domain import (DataChunkStep, ItemProcessor, EventMapper, WorkingDirectoryCreator)
from src.shared.batch.writers import OracleWriter
from src.shared.batch.readers import PandasDataFrameReader
import os
import datetime as dt
import pandas as pd
from zipfile import ZipFile
import re
from shutil import rmtree, copyfileobj


class DynamicProcessor(ItemProcessor):
    def __init__(self):
        self.context = dict()
    
    def start(self, context):
        self.context = context
        
    def process(self, items):
        headers = [field['src_fieldname'] for field in self.context['config']['fields']]
        if "COLLECT_TIME" in headers:
            items['COLLECT_TIME'] = pd.to_datetime(items['COLLECT_TIME'], format='%Y%m%d%H%M%S')
        if "Begin Time" in headers:
            items['Begin Time'] = pd.to_datetime(items['Begin Time'], format='%Y-%m-%d %H:%M:%S')
        if "End Time" in headers:
            items['End Time'] = pd.to_datetime(items['End Time'], format='%Y-%m-%d %H:%M:%S')
        if "Max Value of Detecting Point Temperature(Celsius)" in headers:
            items['Max Value of Detecting Point Temperature(Celsius)'] = pd.to_numeric(items['Max Value of Detecting Point Temperature(Celsius)'].replace('Too Low to Measure', None))
        if "Min Value of Detecting Point Temperature(Celsius)" in headers:
            items['Min Value of Detecting Point Temperature(Celsius)'] = pd.to_numeric(items['Min Value of Detecting Point Temperature(Celsius)'].replace('Too Low to Measure', None))
        if "Value of Detecting Point Temperature(Celsius)" in headers:
            items['Value of Detecting Point Temperature(Celsius)'] = pd.to_numeric(items['Value of Detecting Point Temperature(Celsius)'].replace('Too Low to Measure', None))
        if "Max Value of Laser Temperature(Celsius)" in headers:
            items['Max Value of Laser Temperature(Celsius)'] = pd.to_numeric(items['Max Value of Laser Temperature(Celsius)'].replace('Too Low to Measure', None))
        if "Min Value of Laser Temperature(Celsius)" in headers:
            items['Min Value of Laser Temperature(Celsius)'] = pd.to_numeric(items['Min Value of Laser Temperature(Celsius)'].replace('Too Low to Measure', None))
        if "Laser Temperature (Celsius)" in headers:
            items['Laser Temperature (Celsius)'] = pd.to_numeric(items['Laser Temperature (Celsius)'].replace('Too Low to Measure', None))
        items['filename'] = self.context['filename']
        items = items[headers]
        # print(items.head())
        # items = items.fillna(value=None, how='all')
        rows = items.to_dict(orient='split')
        rows = rows['data']
        rows = [[None if pd.isna(value) else value for value in row] for row in rows]
        # print("row_count", len(rows[0]))
        # print("process", len(rows))
        return rows


class ZteConfigFinder:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, context):
        config = self.repo.find(context['config_id'])
        context['config'] = config
        return context


class ZteStatsFinder:
    def __init__(self, sftp):
        self.sftp = sftp

    def execute(self, config):
        files = self.sftp.get_filename_and_updated_at(config['work_dir'], config['file_pattern'])
        pattern = re.compile(config['file_pattern'])
        files_filtered = list(filter(lambda row: pattern.match(row['file']) is not None, files))
        return files_filtered


class ZtePoller:
    def __init__(self, sftp):
        self.sftp = sftp

    def download(self, context):
        config = context['config']
        self.sftp.useConnection(config['server_id'])
        self.sftp.connect()
        self.sftp.get_files(config['work_dir'], context['storage_dir'], context['filename'])
        pattern = re.compile(config['file_pattern'])
        str_date = pattern.search(context['filename']).group(1)
        context['file_date'] = dt.datetime.strptime(str_date, config['file_date_format'])
        print(context['filename'])


class ZteZipChunkTask(DataChunkStep):
    def __init__(self, db, control_repo):
        super().__init__(PandasDataFrameReader(), DynamicProcessor(), OracleWriter(db, control_repo))
        self.control_repo = control_repo
        self.counter = 0
        self.start_time = None

    def execute(self, content):
        self.counter = 0
        self.start_time = dt.datetime.now()
        content['file_count'] = 0
        subqueue_id = ''
        try:
            subcontext = content.copy()
            config = content['config']
            files = self.extrac_files(content['storage_dir'], content['filename'])
            content['file_count'] = len(files)
            for subconfig in config['sub_config']:
                subqueue_id = subconfig['queue_id']
                pattern = re.compile(subconfig['file_pattern'])
                files_filtered = list(filter(lambda subfilename: pattern.match(subfilename) is not None, files))
                # print(subqueue_id, len(files_filtered))
                for subfile in files_filtered:
                    subcontext['config'] = subconfig
                    subcontext['original_filename'] = content['filename']
                    subcontext['filename'] = subfile
                    self.counter += 1
                    super().execute(subcontext)
            self._save_control_file(content, None)
        except BaseException as e:
            self._save_control_file(content, subqueue_id+': '+str(e))
            raise e
        return content

    def extrac_files(self, storage_dir, filename):
        zf = ZipFile(f'{storage_dir}/{filename}', 'r')
        zf.extractall(storage_dir)
        unzip_files = zf.namelist()
        zf.close()
        os.unlink(f"{storage_dir}/{filename}")
        return unzip_files

    def _save_control_file(self, context, error):
        if context is not None:
            config = context['config']
            end_time = dt.datetime.now()
            self.control_repo.save_carga(
                config['queue_id'],
                context['filename'],
                self.counter,
                context['file_count'],
                self.start_time,
                end_time,
                'CARGADO' if error is None else 'ERROR',
                str(error) if error is not None else None,
                context['file_date']
            )


class ZteStatsFromConfig:
    def __init__(self, db, repo, sftp, control_repo):
        self.config_finder = ZteConfigFinder(repo)
        self.poller = ZtePoller(sftp)
        self.dataframe_task = ZteZipChunkTask(db.getReference(), control_repo)
        self.event_mapper = EventMapper()
        self.wk_creator = WorkingDirectoryCreator()
        self.base_storage_dir = f"{STORAGE_DIR}zte_stats"
        self.storage_dir = None

    def execute(self, context):
        try:
            context = self.config_finder.execute(context)
            self.start(context)
            self.poller.download(context)
            context = self.dataframe_task.execute(context)
            self.complete()
        except BaseException as e:
            self.error(e)

    def start(self, context):
        self.storage_dir = self.wk_creator.create(self.base_storage_dir)
        context['storage_dir'] = self.storage_dir

    def complete(self):
        self.end_time = dt.datetime.now()
        if self.storage_dir is not None:
            rmtree(self.storage_dir)

    def error(self, error):
        self.complete()
        raise error

    def event_handler(self, event):
        event_mapped = self.event_mapper.execute(event)
        self.execute(event_mapped)


class ZTEEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, repository, sftp_service, control_carga_repo, queue_service):
        super().__init__(sftp_service, control_carga_repo, queue_service)
        self.repository = repository

    def get_cargas_config(self, group_id=None):
        if group_id is not None:
            return self.repository.get_by_group_id(group_id)
        return self.repository.get()


class ZTEEventConsumerFromConfig(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, repository, notification_service):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.1
        self.repository = repository
        self.loop = False
        self.carga_config = {}
        self.max_jobs_per_run = 10

    def execute(self, group_id=None):
        cargas = []
        if group_id == None:
            cargas = self.repository.get()
        else:
            cargas = self.repository.get_by_group_id(group_id)

        if len(cargas) == 0:
            raise Exception(f"No existen cargas")
        
        for row in cargas:
            self.carga_config[row["queue_id"]] = row

        def map_event(event):
            event['msg_body']['config_id'] = self.carga_config[event['queue_id']]["id"]
            return event

        for row in cargas:
            queue_id = row["queue_id"]
            self.queue_handlers[queue_id] = {'handler': LOAD_ZTE_STATS_FROM_CONFIG, 'callback': lambda s, e: s.event_handler(map_event(e))}

        self.queue_ids = list(self.queue_handlers)
        super().execute()