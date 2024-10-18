import datetime as dt
import re
import json
import csv
import math
import aiohttp
import aiofiles
import asyncio
import uuid
import os
import pandas as pd
from shutil import rmtree
from concurrent.futures import ThreadPoolExecutor
from src.shared.config import STORAGE_DIR
from src.shared.carga.services import BaseCargaFromConfig

from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.pm.shared.services import (LOAD_PM_FROM_CONFIG, LOAD_PM_BATCH_FROM_CONFIG)

from src.shared.batch.domain import (DataChunkStep, ItemProcessor, EventMapper, WorkingDirectoryCreator)
from src.shared.batch.writers import OracleWriter
from src.shared.batch.readers import PandasDataFrameReader

class LoadPMFromConfig(BaseCargaFromConfig):
    def __init__(self, db, repository, sftp_service, control_carga_repo):
        super().__init__(db, repository, sftp_service, control_carga_repo)
        self.pm_api = sftp_service
        self.base_storage_dir = f"{STORAGE_DIR}pm"
        self.max_workers = 10

    def _get_files_from_server(self, config, remote_dir, dt_fecha1, dt_fecha2):
        files = []
        str_date = dt_fecha1.strftime(config["file_date_format"])
        starttime = int(dt.datetime.timestamp(dt_fecha1 - dt.timedelta(minutes=1)))
        endtime = int(dt.datetime.timestamp(dt_fecha2 - dt.timedelta(minutes=1)))
        # print([starttime, endtime])
        url = None
        sub_url = None
        if config.get("sub_api_query") is None:
            url = f"{config['api_query']}&starttime={starttime}&endtime={endtime}"
        else:
            url = f"{config['api_query']}"
            sub_url = f"{config['sub_api_query']}&starttime={starttime}&endtime={endtime}"
        
        files.append({
            'file': f"{config['name']}_{str_date}.csv",
            'url': url,
            'sub_url': sub_url
        })
        
        pattern = re.compile(config['file_pattern'])
        files_filtered = []
        for row in files:
            str_date = pattern.search(row['file']).group(1)
            date_of_file = dt.datetime.strptime(str_date, config['file_date_format'])
            if dt_fecha1 <= date_of_file and date_of_file < dt_fecha2:
                files_filtered.append(row)
        
        for row in files_filtered:
            print(row["file"])
        return files_filtered

    def _download_files(self, storage_dir, files_filtered):
        for file in files_filtered:
            filename = file['file']
            local_path_filename = f"{storage_dir}/{filename}"
            try:
                if file.get('sub_url') is None:
                    response = self.pm_api.get(file['url'])
                    with open(local_path_filename, 'wb') as content:
                        content.write(response.content)
                else:
                    reload_fields = list(filter(lambda r: r["to_reload"] is not None, self.fields_config))
                    skip_lines= 1
                    response = self.pm_api.get(file['url'])
                    result = response.json()
                    devices = result["d"]["results"]
                    # csv_values = []
                    
                    n_pages = math.ceil(len(devices) / self.max_workers)
                    executor = ThreadPoolExecutor(max_workers=self.max_workers)

                    for page in range(1, n_pages+1):
                        devices_to_process = self._get_data_of_page(devices, self.max_workers, page)
                        executor_by_key = {}
                        print(list(map(lambda r: r["ID"], devices_to_process)))
                        for row in devices_to_process:
                            deviceid = row["ID"]
                            url = f"{file['sub_url']}&$filter=((device/ID eq {deviceid}))"
                            local_filename = f"{storage_dir}/{deviceid}_{filename}"
                            executor_by_key[deviceid] = executor.submit(self._download_one_file, url, local_filename)

                        error = None
                        for row in devices_to_process:
                            print(row["ID"], executor_by_key[row["ID"]].result())
                            result = executor_by_key[row["ID"]].result()
                            if type(result) != type(""):
                                error = result
                        if error is not None:
                            raise error
                    
                    # for row in devices:
                    #     deviceid = row["ID"]
                    #     self._download_one_file(
                    #         f"{file['sub_url']}&$filter=((device/ID eq {deviceid}))",
                    #         f"{storage_dir}/{deviceid}_{filename}"
                    #     )

                    with open(local_path_filename, 'w', encoding="utf-8",  newline="") as csvfile:
                        writer = csv.writer(csvfile)
                        for device in devices:
                            csv_values = []
                            deviceid = device["ID"]

                            with open(f"{storage_dir}/{deviceid}_{filename}", encoding='UTF-8') as content:
                                reader = csv.reader(content)
                                counter = 0 - skip_lines
                                for row in reader:
                                    counter += 1
                                    if counter <=0:
                                        continue
                                    validation = True
                                    for field in reload_fields:
                                        value = row[int(field["src_fieldname"])]
                                        if value is None or value == '':
                                            validation = False
                                            # break
                                    if validation == False:
                                        continue
                                    csv_values.append(row)
                            
                            # print(device["ID"], len(csv_values))
                            writer.writerows(csv_values)
            except Exception as e:
                raise e

    def _download_one_file(self, url, local_filename):
        try:
            response = self.pm_api.get(url)
            with open(f"{local_filename}", 'wb') as content:
                content.write(response.content)
            return "ok"
        except BaseException as e:
            return e

    def _get_data_of_page(self, servers, perPage, page):
        len_servers = len(servers)
        lastIndex = 0
        i = perPage-1
        actual_page = 1
        while i <= len_servers or lastIndex < len_servers:
            if actual_page == page:
                return servers[i-(perPage-1):i+1]
            lastIndex = i
            i += perPage
            actual_page += 1


class PMEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, repository, sftp_service, control_carga_repo, queue_service):
        super().__init__(sftp_service, control_carga_repo, queue_service)
        self.repository = repository
        self.pm_api = sftp_service

    def get_cargas_config(self, group_id=None):
        return self.repository.get()

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        files = []
        pattern = re.compile(config['file_pattern'])

        dt_fecha_recorrido = dt_fecha1.replace(minute=0, second=0)
        while dt_fecha_recorrido.strftime(config['file_date_format']) < (dt_fecha2.replace(minute=0, second=0)).strftime(config['file_date_format']):
            str_date = dt_fecha_recorrido.strftime(config["file_date_format"])
            files.append({
                'file': f"{config['name']}_{str_date}.csv"
            })
            dt_fecha_recorrido = dt_fecha_recorrido + dt.timedelta(**json.loads(config['loop_time']))
        
        files_filtered = []
        for row in files:
            str_date = pattern.search(row['file']).group(1)
            date_of_file = dt.datetime.strptime(str_date, config['file_date_format'])
            if dt_fecha1 <= date_of_file and date_of_file < dt_fecha2:
                files_filtered.append(row)
        return files_filtered


class PMEventConsumerFromConfig(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service, repository):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.1
        self.repository = repository
        self.loop = False
        self.config_by_queueid = {}

    def execute(self, group_id=None):
        cargas = []
        if group_id == None:
            cargas = self.repository.get()
        else:
            cargas = self.repository.get_by_group_id(group_id)

        if len(cargas) == 0:
            raise Exception(f"No existen cargas")
        
        for row in cargas:
            self.config_by_queueid[row["queue_id"]] = row

        def map_event(event):
            event['msg_body']['config_id'] = self.config_by_queueid[event['queue_id']]["id"]
            return event

        for row in cargas:
            queue_id = row["queue_id"]
            self.queue_handlers[queue_id] = {'handler': LOAD_PM_FROM_CONFIG, 'callback': lambda s, e: s.event_handler(map_event(e))}

        self.queue_ids = list(self.queue_handlers)
        super().execute()


### batch service

class PMProcessor(ItemProcessor):
    def __init__(self):
        self.context = dict()
    
    def start(self, context):
        self.context = context
        
    def process(self, items):
        items['result_time'] = pd.NaT
        items = items[items['portmfs/Timestamp'].notna()]
        items.loc[:, 'result_time'] = items['portmfs/Timestamp'].apply(lambda value: dt.datetime.fromtimestamp(int(value)))
        print("process: ", len(items))

        headers = [field['src_fieldname'] for field in self.context['config']['fields']]
        items = items[headers]
        rows = items.to_dict(orient='split')
        rows = rows['data']
        rows = [[None if pd.isna(value) else value for value in row] for row in rows]
        return rows

class PMConfigFinder:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, context):
        config = self.repo.find(context['config_id'])
        if config is not None:
            config['fields'] = self.repo.get_fields_by_id(context['config_id'])
        context['config'] = config
        return context

class PMPoller:
    def __init__(self):
        self.storage_dir = None
        self.base_url = os.getenv('PYAPP_PM_BASE_URL')
        self.user = os.getenv('PYAPP_PM_USER')
        self.password = os.getenv('PYAPP_PM_PASSWORD')
        self.active_fetch = {}
        self.max_workers = 15

    def download(self, context):
        self.storage_dir = context['storage_dir']
        asyncio.run(self.async_download(context))

    async def async_download(self, context):
        pattern = re.compile(context['config']['file_pattern'])
        str_date = pattern.search(context['filename']).group(1)
        file_date = dt.datetime.strptime(str_date, context['config']['file_date_format'])
        file_date_end = file_date + dt.timedelta(**json.loads(context['config']['loop_time']))
        # api filters
        starttime = int(dt.datetime.timestamp(file_date - dt.timedelta(minutes=1)))
        endtime = int(dt.datetime.timestamp(file_date_end - dt.timedelta(minutes=1)))

        if context['config'].get('api_query') is None:
            semaphore = asyncio.Semaphore(1)
            api_uri = f"{context['config']['api_query']}&starttime={starttime}&endtime={endtime}"
            localfile = f"{self.storage_dir}/{context['filename']}"

            async with aiohttp.ClientSession() as session:
                tasks = [asyncio.create_task(self.fetch_content(semaphore, session, api_uri))]
                for task in asyncio.as_completed(tasks):
                    tempfilename = await task
                    os.rename(tempfilename, localfile)
        else:
            response = await self.fetch_json(context['config']['api_query'])
            devices = response["d"]["results"]

            api_uri = f"{context['config']['sub_api_query']}&starttime={starttime}&endtime={endtime}"+'&$filter=((device/ID eq {deviceid}))'
            localfile = f"{self.storage_dir}/{context['filename']}"
            print(api_uri)
            print(f"devices: {len(devices)}")

            semaphore = asyncio.Semaphore(self.max_workers)
            async with aiohttp.ClientSession() as session:
                tasks = [asyncio.create_task(self.fetch_content(semaphore, session, api_uri.format(deviceid=row['ID']))) for row in devices]
                tempfiles = [await task for task in asyncio.as_completed(tasks)]
                localfile_exists = False
                with open(localfile, 'w', encoding="utf-8",  newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    for tempfilename in tempfiles:
                        # tempfilename = await task
                        if type(tempfilename) == type(""):
                            with open(f"{self.storage_dir}/{tempfilename}", encoding='UTF-8') as csvtemp:
                                reader = csv.reader(csvtemp)
                                headers = next(reader)
                                if localfile_exists == False:
                                    writer.writerows([headers])
                                    localfile_exists = True
                                writer.writerows([row for row in reader])
                            os.unlink(f"{self.storage_dir}/{tempfilename}")
                            # print(f"ok: {tempfilename}")
                        else:
                            print(f"error: {tempfilename}")
                            raise tempfilename
            
        context['file_date'] = file_date

    async def fetch_content(self, semaphore, session, uri):
        async with semaphore:
            auth = aiohttp.BasicAuth(self.user, self.password)
            uuid_file = str(uuid.uuid4())+'.csv'
            # self.active_fetch[uuid_file] = 1
            async with session.get(f"{self.base_url}/{uri}", auth=auth) as response:
                if response.status == 200:
                    async with aiofiles.open(f"{self.storage_dir}/{uuid_file}", 'wb') as file:
                        while True:
                            chunk = await response.content.read(2048)
                            if not chunk:
                                break
                            await file.write(chunk)
                    # print(f"ok: {uuid_file} {len(list(self.active_fetch))}")
                    # self.active_fetch.pop(uuid_file)
                    return uuid_file
                else:
                    # return Exception(await response.text())
                    return Exception(await response.text())
    
    async def fetch_json(self, uri):
        auth = aiohttp.BasicAuth(self.user, self.password)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/{uri}", auth=auth) as response:
                return await response.json()


class PmBatchFromConfig:
    def __init__(self, db, repo, control_repo):
        self.config_finder = PMConfigFinder(repo)
        self.poller = PMPoller()
        self.dataframe_task = DataChunkStep(PandasDataFrameReader(), PMProcessor(), OracleWriter(db.getReference(), control_repo))
        self.event_mapper = EventMapper()
        self.wk_creator = WorkingDirectoryCreator()
        self.base_storage_dir = f"{STORAGE_DIR}pm_batch"
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


class PmEventBatchConsumerFromConfig(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service, repository):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.1
        self.repository = repository
        self.loop = False
        self.carga_config = {}

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
            self.queue_handlers[queue_id] = {'handler': LOAD_PM_BATCH_FROM_CONFIG, 'callback': lambda s, e: s.event_handler(map_event(e))}

        self.queue_ids = list(self.queue_handlers)
        super().execute()
