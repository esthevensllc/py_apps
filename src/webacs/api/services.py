import requests
import pytz
import datetime as dt
import json
import re
import os
from requests.auth import HTTPBasicAuth
from shutil import rmtree

from src.webacs.shared.services import LOAD_WEBACS_FROM_CONFIG
from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer
from src.shared.queue.SimpleEventConsumer import EventConsumerFromConfig
from src.shared.config import STORAGE_DIR, TIMEZONE
from src.shared.batch.domain import (ReactiveDataChunkStep, ItemProcessor, EventMapper, WorkingDirectoryCreator)
from src.shared.batch.readers import DatabaseCursorReader
from src.shared.batch.writers import OracleWriter
from src.shared.batch.pollers import DBCursor
from src.shared.batch.finder import ConfigFinder

class WebacsProcessor(ItemProcessor):
    def __init__(self):
        self.context = dict()
        self.tzone = pytz.timezone(TIMEZONE)
    
    def start(self, context):
        self.context = context
        
    def process(self, items):
        headers = [field['src_fieldname'] for field in self.context['config']['fields']]
        src_headers = self.context['poller']['cursor'].get_columns()
        src_headers_index = {}
        for index in range(len(src_headers)):
            src_headers_index[src_headers[index]] = index

        for row in items:
            row['@uuid'] = row.get('@uuid')
            row['alarmFoundAt'] = self.format_date(row['alarmFoundAt'].replace('Z', '+00:00')) if row['alarmFoundAt'] is not None else None
            row['lastUpdatedAt'] = self.format_date(row['lastUpdatedAt'].replace('Z', '+00:00')) if row['lastUpdatedAt'] is not None else None
            row['deviceTimestamp'] = self.format_date(row['deviceTimestamp'].replace('Z', '+00:00')) if row.get('deviceTimestamp') is not None else None
            row['timeStamp'] = self.format_date(row['timeStamp'].replace('Z', '+00:00')) if row['timeStamp'] is not None else None
            row['category_ordinal'] = row['category'].get('ordinal')
            row['category_value'] = row['category'].get('value')
            row['condition_ordinal'] = row['condition'].get('ordinal')
            row['condition_value'] = row['condition'].get('value')
            row['nttyaddrss7_address_address'] = row['nttyaddrss7_address'].get('address')
            row['owner'] = row.get('owner')
            row['result_time'] = self.context['file_date']

        src_headers += ['result_time']

        return [[row[header] for header in headers] for row in items]

    def format_date(self, str_utc):
        formated_date = dt.datetime.fromisoformat(str_utc).replace(tzinfo=None)
        return pytz.utc.localize(formated_date).astimezone(self.tzone)


class WebacsReportFinder:

    def execute(self, config, dt_fecha1, dt_fecha2):
        # files = self.db.fetch(config['src_query_finder'])
        # files = [files] if isinstance(files, dict) else files
        # files = list(map(lambda row: self._map_date_to_file(config, row[0]), files))

        files = []
        dt_fecha_recorrido = dt_fecha1
        delta = dt.timedelta(**json.loads(config['loop_time']))
        while dt_fecha_recorrido.strftime(config['file_date_format']) < dt_fecha2.strftime(config['file_date_format']):
            str_date = dt_fecha_recorrido.strftime(config["file_date_format"])
            next_date = dt_fecha_recorrido + delta

            files.append({
                'file': f"{config['name']}_{str_date}.json",
                'str_filedate': dt_fecha_recorrido.strftime('%Y-%m-%d %H:%M')+":00",
                # 'str_filedate_day': dt_fecha_recorrido.strftime('%Y-%m-%d')+" 00:00:00",
                # 'url': config["api_query"],
                # 'params': params
            })
            dt_fecha_recorrido = next_date
            
        pattern = re.compile(config['file_pattern'])
        files_filtered = list(filter(lambda row: pattern.match(row['file']) is not None, files))
        return files_filtered


class WebacsPoller:

    def download(self, context):
        config = context['config']

        pattern = re.compile(config['file_pattern'])
        str_date = pattern.search(context['filename']).group(1)
        context['file_date'] = dt.datetime.strptime(str_date, config['file_date_format'])

        params = {
            'fecha_ini': context['file_date'] - dt.timedelta(minutes=30),
            'fecha_fin': context['file_date']
        }
        
        print(f"{config['name']}: {str_date}")

        uris = [
            f'{config["src_uri"]}&timeStamp=between("{params["fecha_ini"].strftime("%Y-%m-%dT%H:%M:%S")}","{params["fecha_fin"].strftime("%Y-%m-%dT%H:%M:%S")}")',
            f'{config["src_uri"]}&lastUpdatedAt=between("{params["fecha_ini"].strftime("%Y-%m-%dT%H:%M:%S")}","{params["fecha_fin"].strftime("%Y-%m-%dT%H:%M:%S")}")',
        ]
        cursor = ApiCursor(config['type'], uris, context['config']['chunk_limit'])

        context['poller'] = {
            'cursor': cursor,
        }

class ApiCursor(DBCursor):
    def __init__(self, type, uris, chunk_limit):
        self.base_url = os.getenv('PYAPP_WEBACS_BASE_URL')
        self.auth = HTTPBasicAuth(os.getenv('PYAPP_WEBACS_USER'), os.getenv('PYAPP_WEBACS_PASSWORD'))
        self.type = type
        self.uris = uris
        self.chunk_limit = chunk_limit
        self.columns = None
    
    def get_columns(self):
        return self.columns

    def on_next(self, callback):
        self.on_next_callback = callback

    def subscribe(self):
        self.columns = [
            "@displayName"
            "@id"
            "acknowledgementStatus"
            "alarmFoundAt"
            "alarmId"
            "category_ordinal"
            "category_value"
            "condition_ordinal"
            "condition_value"
            "deviceName"
            "lastUpdatedAt"
            "message"
            "nttyaddrss7_address"
            "severity"
            "source"
            "timeStamp"
            "wirelessSpecificAlarmId",
            "src_filter_by"
            # "result_time"
        ]
        for uri in self.uris:
            params = {
                '.firstResult': 0,
                '.maxResults': self.chunk_limit,
            }
            filter_by = "timeStamp" if "timeStamp" in uri else "lastUpdatedAt"
            print("uri:", uri)
            response = requests.get(f"{self.base_url}/{uri}", params, auth=self.auth, verify=False)
            response = response.json()
            if response['queryResponse'].get('entity') is not None:
                results = [ self._map_row(row[row['@dtoType']], filter_by) for row in response['queryResponse']['entity']]
                self.on_next_callback(results)
            else:
                break

            while (response['queryResponse']['@first'] + len(results)) < response['queryResponse']['@count']:
                params['.firstResult'] = params['.firstResult'] + params['.maxResults']
                response = requests.get(f"{self.base_url}/{uri}", params, auth=self.auth, verify=False).json()
                if response['queryResponse'].get('entity') is not None:
                    results = [ self._map_row(row[row['@dtoType']], filter_by) for row in response['queryResponse']['entity']]
                    self.on_next_callback(results)
                else:
                    break

    def _map_row(self, row, filter_by):
        row['src_filter_by'] = filter_by
        return row


class WebacsReportFromConfig:
    def __init__(self, db, repo, control_repo):
        self.config_finder = ConfigFinder(repo)
        self.poller = WebacsPoller()
        self.chunk_task = ReactiveDataChunkStep(DatabaseCursorReader(), WebacsProcessor(), OracleWriter(db.getReference(), control_repo))
        self.event_mapper = EventMapper()
        self.wk_creator = WorkingDirectoryCreator()
        self.base_storage_dir = f"{STORAGE_DIR}webacs"
        self.storage_dir = None

    def execute(self, context):
        try:
            context = self.config_finder.execute(context)
            self.start(context)
            self.poller.download(context)
            context = self.chunk_task.execute(context)
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


class WebacsEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, repository, control_carga_repo, queue_service):
        super().__init__(None, control_carga_repo, queue_service)
        self.repository = repository
        self.finder = WebacsReportFinder()

    def get_cargas_config(self, group_id=None):
        if group_id is not None:
            return self.repository.get_by_group_id(group_id)
        return self.repository.get()

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        return self.finder.execute(config, dt_fecha1, dt_fecha2)

    def get_date_range(self, config):
        dt_fecha2 = dt.datetime.now()

        dt_fecha2 = dt_fecha2 - dt.timedelta(**json.loads(config['loop_time']))
        fecha_loop = dt_fecha2.replace(minute=0, second=0)
        while fecha_loop <= dt_fecha2:
            fecha_loop = fecha_loop + dt.timedelta(**json.loads(config["loop_time"]))
        
        # fecha ini - fin
        dt_fecha2 = fecha_loop
        time_ago_delta = json.loads(config["search_time_ago"])
        dt_fecha1 = dt_fecha2 - dt.timedelta(**time_ago_delta)

        # dt_fecha2 = dt_fecha2 - dt.timedelta(**json.loads(config['loop_time']))
        if config.get("search_time_delay") is not None:
            dt_fecha2 = dt_fecha2 - dt.timedelta(**json.loads(config['search_time_delay']))
        return dt_fecha1, dt_fecha2


class WebacsEventConsumerFromConfig(EventConsumerFromConfig):
    def __init__(self, queue_service, app_container, notification_service, repository):
        super().__init__(queue_service, app_container, notification_service, repository)
        self.handler_name = LOAD_WEBACS_FROM_CONFIG