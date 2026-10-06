import os
import json
import datetime as dt
import time
import re
from src.gde.shared.services import LOAD_GDE_FROM_CONFIG
from src.shared.config import STORAGE_DIR
from src.shared.services import TempDataManager
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.shared.carga.services import BaseCargaFromConfig
from src.shared.carga.services import (ApiDataPoller)
from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer

class GdeDataFinder:
    def get_source_files(self, config, dt_fecha1, dt_fecha2):
        files = []
        dt_fecha_recorrido = dt_fecha1
        delta = dt.timedelta(**json.loads(config['loop_time']))
        # delta_utc = dt.timedelta(hours=4, minutes=59)
        while dt_fecha_recorrido.strftime(config['file_date_format']) < dt_fecha2.strftime(config['file_date_format']):
            str_date = dt_fecha_recorrido.strftime(config["file_date_format"])
            next_date = dt_fecha_recorrido + delta

            params = {
                "date": dt_fecha_recorrido.strftime('%Y-%m-%d %H:%M')+":00",
                "substract_minutes": config.get("api_lookback_minutes", 20),
                "configured_field": "ttcreatetime",
                "limit": 30000,
                "start": 0
            }
            
            files.append({
                'file': f"{config['name']}_{str_date}_1.json",
                'str_filedate': dt_fecha_recorrido.strftime('%Y-%m-%d %H:%M')+":00",
                'str_filedate_day': dt_fecha_recorrido.strftime('%Y-%m-%d')+" 00:00:00",
                'url': config["api_query"],
                'params': params
            })

            params2 = params.copy()
            params2["configured_field"] = "clearalarmfirstreceivetime"
            clear_minutes = config.get("api_clear_lookback_minutes", params["substract_minutes"])
            if clear_minutes <= 0:
                raise ValueError("La ventana de limpiezas GDE debe ser positiva")
            query_windows = []
            window_end = dt_fecha_recorrido - dt.timedelta(minutes=params["substract_minutes"])
            while window_end < dt_fecha_recorrido:
                remaining = int((dt_fecha_recorrido - window_end).total_seconds() / 60)
                minutes = min(clear_minutes, remaining)
                window_end += dt.timedelta(minutes=minutes)
                query_windows.append({
                    **params2,
                    "date": window_end.strftime('%Y-%m-%d %H:%M:00'),
                    "substract_minutes": minutes,
                })
            files.append({
                'file': f"{config['name']}_{str_date}_2.json",
                'str_filedate': dt_fecha_recorrido.strftime('%Y-%m-%d %H:%M')+":00",
                'str_filedate_day': dt_fecha_recorrido.strftime('%Y-%m-%d')+" 00:00:00",
                'url': config["api_query"],
                'params': query_windows[-1],
                'query_windows': query_windows,
            })
            dt_fecha_recorrido = next_date
            
        pattern = re.compile(config['file_pattern'])
        files_filtered = list(filter(lambda row: pattern.match(row['file']) is not None, files))
        # for row in files_filtered:
        # print(row)
        return files_filtered


class GdeDataPoller(ApiDataPoller):
    def __init__(self, api):
        self.api = api

    def download_one(self, config, source, storage_dir):
        if "query_windows" in source:
            managers = []
            for params in source["query_windows"]:
                window_source = {**source, "params": params}
                window_source.pop("query_windows")
                self.download_one(config, window_source, storage_dir)
                managers.extend(window_source["temp_manager"])
            source["temp_manager"] = managers
            return
        page_size = source["params"]["limit"]
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                time.sleep(1)
            params = source["params"].copy()
            data_manager = TempDataManager(config["chunk_limit"], storage_dir)
            downloaded = 0
            total = None
            previous_page = None
            short_page_probe = False
            while True:
                result = self.api.get(source["url"], params).json()
                rows = result.get("results")
                if not isinstance(rows, list):
                    raise ValueError(
                        f"GDE devolvió una respuesta sin lista results para {source['file']}: "
                        f"{str(result)[:500]}"
                    )
                reported_total = result.get("total")
                if reported_total is not None:
                    total = int(reported_total)
                    if total < 0:
                        raise ValueError(f"Total inválido en respuesta GDE: {total}")
                if len(rows) > page_size:
                    print(f"GDE_API_OVERSIZED_PAGE file={source['file']} rows={len(rows)} limit={page_size}")
                if params["start"] > 0 and total is not None and len(rows) >= total:
                    data_manager = TempDataManager(config["chunk_limit"], storage_dir)
                    data_manager.add_rows(rows)
                    print(
                        f"GDE_API_SNAPSHOT file={source['file']} "
                        f"start={params['start']} rows={len(rows)} total={total}; "
                        "se usa esta respuesta completa"
                    )
                    print(f"GDE_API_COMPLETE file={source['file']} rows={len(rows)}")
                    source["temp_manager"] = [data_manager]
                    return
                if params["start"] > 0 and rows and rows == previous_page:
                    print(f"GDE_API_RETRY file={source['file']} attempt={attempt} repeated_page")
                    break
                data_manager.add_rows(rows)
                downloaded += len(rows)
                print(
                    f"GDE_API_PAGE file={source['file']} "
                    f"field={params['configured_field']} date={params['date']} "
                    f"attempt={attempt} start={params['start']} rows={len(rows)} "
                    f"downloaded={downloaded} total={total}"
                )
                if total is not None and downloaded >= total:
                    if downloaded > total:
                        print(
                            f"GDE_API_TOTAL_MISMATCH file={source['file']} "
                            f"received={downloaded} reported_total={total}; "
                            "se procesan todas las filas recibidas"
                        )
                    print(f"GDE_API_COMPLETE file={source['file']} rows={downloaded}")
                    source["temp_manager"] = [data_manager]
                    return
                if len(rows) < page_size:
                    if total is None:
                        print(f"GDE_API_COMPLETE file={source['file']} rows={downloaded}")
                        source["temp_manager"] = [data_manager]
                        return
                    if rows and not short_page_probe:
                        short_page_probe = True
                        previous_page = rows
                        params["start"] += len(rows)
                        print(
                            f"GDE_API_PROBE file={source['file']} "
                            f"attempt={attempt} start={params['start']}"
                        )
                        continue
                    print(
                        f"GDE_API_RETRY file={source['file']} attempt={attempt} "
                        f"received={downloaded} reported_total={total}"
                    )
                    break
                previous_page = rows
                params["start"] += len(rows)

        raise RuntimeError(
            f"GDE no completó {source['file']} tras {max_attempts} "
            f"consultas desde start=0"
        )


class GdeProcessor:
    def process(self, config, sources):
        for index in range(len(sources)):
            sources[index] = self.process_one(sources[index], config)
        return sources

    def process_one(self, source, config):
        mapped_manager = []
        for temp_data in source["temp_manager"]:
            envlist = {
                'str_filedate': source['str_filedate'],
                'str_filedate_day': source['str_filedate_day'],
                'filename': source['file'],
            }
            temp_manager = self.map_temp_manager(temp_data, config, env=envlist)
            mapped_manager.append(temp_manager)
        source["temp_manager"] = mapped_manager
        return source

    def map_temp_manager(self, temp_manager, config, env):
        mapped_temp_data = TempDataManager(temp_manager.limit, temp_manager.path)
        counter = 0
        for chunk_data in temp_manager.get():
            for index in range(len(chunk_data)):
                row = chunk_data[index]
                mapped_row = {}
                counter += 1
                for field in config["fields"]:
                    value = None
                    try:
                        value = row[field["src_fieldname"]]
                        if field.get('map_with') is not None:
                            value = eval(f"f\"{field['map_with']}\"")
                        if value == '':
                            value = None
                        mapped_row[field["fieldname"]] = value
                    except BaseException as e:
                        print(row)
                        print(f"line: {counter}, field: {field['fieldname']}, value: '{value}'")
                        raise e
                chunk_data[index] = mapped_row
            mapped_temp_data.add_rows(chunk_data)
        return mapped_temp_data



class LoadGdeFromConfig(BaseCargaFromConfig):
    def __init__(self, db, repository, sftp_service, control_carga_repo):
        super().__init__(db, repository, sftp_service, control_carga_repo)
        self.nfa_api = sftp_service
        self.base_storage_dir = f"{STORAGE_DIR}gde"
        self.gde_finder = GdeDataFinder()
        self.gde_poller = GdeDataPoller(self.nfa_api)
        self.gde_processor = GdeProcessor()

    def event_handler(self, event):
        body = event["msg_body"]
        if body.get("backfill_id") != "gde-20261001-ttcreatetime":
            return super().event_handler(event)

        if body.get("format") != "mxm" or body.get("granularity") != 180:
            raise ValueError("El evento de recarga GDE debe cubrir 180 minutos")
        anchor = dt.datetime.strptime(body["fec_ini"], "%Y-%m-%d %H:%M")
        self.execute(
            body["config_id"],
            anchor,
            anchor + dt.timedelta(minutes=180),
            config_overrides={
                "loop_time": json.dumps({"minutes": 180}),
                "api_lookback_minutes": 180,
                "api_clear_lookback_minutes": 60,
            },
        )

    def _get_files_from_server(self, config, remote_dir, dt_fecha1, dt_fecha2):
        return self.gde_finder.get_source_files(config, dt_fecha1, dt_fecha2)

    def _download_files(self, storage_dir, files):
        self.sources = self.gde_poller.download(self.config, files, storage_dir)

    def _get_data_from_csv(self, fields_config, filename, skip_lines=0, date_of_file=None, env={}):
        self.config["fields"] = fields_config
        filtered_sources = list(filter(lambda source: source['file'] in filename, self.sources))
        if len(filtered_sources) == 0:
            raise Exception("No se encontro el file a procesar")
        if len(filtered_sources) != 1:
            raise Exception("No se puede procesar mas de un archivo al mismo tiempo")
        sources = self.gde_processor.process(self.config, filtered_sources)
        data = []
        for src in sources:
            for manager in src["temp_manager"]:
                for chunk_data in manager.get():
                    data += chunk_data
        return data


class GdeEventProducerFromConfig(RemoteConnectEventProducer):
    def __init__(self, repository, sftp_service, control_carga_repo, queue_service):
        super().__init__(sftp_service, control_carga_repo, queue_service)
        self.repository = repository
        self.gde_finder = GdeDataFinder()

    def get_cargas_config(self, group_id=None):
        return self.repository.get()

    def get_date_range(self, config):
        dt_fecha2 = dt.datetime.now()

        # dt_fecha2 = dt_fecha2 - dt.timedelta(**json.loads(config['loop_time']))
        fecha_loop = dt_fecha2.replace(minute=0, second=0)
        while fecha_loop <= dt_fecha2:
            fecha_loop = fecha_loop + dt.timedelta(**json.loads(config["loop_time"]))
        
        # fecha ini - fin
        dt_fecha2 = fecha_loop
        time_ago_delta = json.loads(config["search_time_ago"])
        dt_fecha1 = dt_fecha2 - dt.timedelta(**time_ago_delta)

        dt_fecha2 = dt_fecha2 - dt.timedelta(**json.loads(config['loop_time']))
        if config.get("search_time_delay") is not None:
            dt_fecha2 = dt_fecha2 - dt.timedelta(**json.loads(config['search_time_delay']))
        return dt_fecha1, dt_fecha2

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        return self.gde_finder.get_source_files(config, dt_fecha1, dt_fecha2)


class GdeEventConsumerFromConfig(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service, repository):
        super().__init__(queue_service, app_container, notification_service)
        # A backfill event can contain three hours of alarms. Bound each run
        # so the producer and metadata updater get another turn promptly.
        self.sleep_time_in_work = 1
        self.max_jobs_per_run = 2
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
            self.queue_handlers[queue_id] = {'handler': LOAD_GDE_FROM_CONFIG, 'callback': lambda s, e: s.event_handler(map_event(e))}

        self.queue_ids = list(self.queue_handlers)
        super().execute()
