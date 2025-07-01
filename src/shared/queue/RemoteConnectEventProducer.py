from src.shared.config import STORAGE_DIR, BASE_DIR, DTFORMAT_BY_ALIAS, TDINTERVAL_BY_ALIAS
import datetime as dt
import json
import re
import stat

class RemoteConnectEventProducer:
    def __init__(self, sftp_service, control_carga_repo, queue_service):
        self.sftp_service = sftp_service
        self.control_carga_repo = control_carga_repo
        self.queue_service = queue_service
        self.succesfull_state = 'CARGADO'
        self.max_retries = 5
    
    def execute(self, group_id=None):
        configs = self.get_cargas_config(group_id)
        if len(configs) == 0:
            raise Exception(f"No existen cargas a procesar")

        for row in configs:
            self._produce_events_to(row)
            print("")

    def get_cargas_config(self, group_id=None):
        return []

    def get_date_range(self, config):
        time_ago_delta = json.loads(config["search_time_ago"])
        dt_fecha2 = dt.datetime.now()
        dt_fecha1 = dt_fecha2 - dt.timedelta(**time_ago_delta)
        return dt_fecha1, dt_fecha2

    def _produce_events_to(self, config):
        self.time_ago_delta = json.loads(config["search_time_ago"])
        self.dt_fecha1, self.dt_fecha2 = self.get_date_range(config)
        print(f"[{config['name']}]: {self.dt_fecha1.strftime('%Y-%m-%d %H:%M:%S')} - {self.dt_fecha2.strftime('%Y-%m-%d %H:%M:%S')}")

        if config.get('server_id') is not None:
            self.sftp_service.useConnection(config['server_id'])
            self.sftp_service.connect()

        files = []
        if '{date}' in config['work_dir']:
            wk_date_format = "%Y%m%d" if config.get("wk_date_format") is None else config["wk_date_format"]
            dt_fecha_recorrido = self.dt_fecha1
            
            dt_fecha_ini_to_day = dt_fecha_recorrido.replace(second=0, microsecond=0)
            dt_fecha_fin_to_day = None
            while dt_fecha_recorrido.strftime('%Y%m%d') <= self.dt_fecha2.strftime('%Y%m%d'):
                str_date = dt_fecha_recorrido.strftime(wk_date_format)
                next_date = dt_fecha_recorrido + dt.timedelta(days=1)
                date_work_dir = config['work_dir'].format(date=str_date)
                if dt_fecha_recorrido.strftime('%Y-%m-%d %H:%M') == self.dt_fecha2.strftime('%Y-%m-%d %H:%M'):
                    dt_fecha_fin_to_day = self.dt_fecha2.replace(second=0, microsecond=0)
                else:
                    dt_fecha_fin_to_day = next_date.replace(hour=0, minute=0, second=0, microsecond=0)
                files_of_date = self._get_files_from_server(config, date_work_dir, None, dt_fecha_ini_to_day, dt_fecha_fin_to_day)
                files += files_of_date
                dt_fecha_recorrido = dt_fecha_recorrido + dt.timedelta(days=1)
                dt_fecha_ini_to_day = dt_fecha_recorrido.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            files = self._get_files_from_server(config, config['work_dir'], None, self.dt_fecha1, self.dt_fecha2)

        # filter files whithout permission
        if config.get('files_permission') is not None:
            files = self._get_files_with_access(files, config['files_permission'])

        # add file date
        pattern = re.compile(config['file_pattern'])
        for index in range(len(files)):
            str_date = pattern.search(files[index]['file']).group(1)
            files[index]['filedate'] = dt.datetime.strptime(str_date, config['file_date_format'])

        controlfiles_by_filename = self._get_controlfiles_by_filename(config["queue_id"], self.dt_fecha1, self.dt_fecha2)

        # print(f"server_files: {len(files)}")
        # print(f"control_files: {len(controlfiles_by_filename)}")
        events = self._get_event_to_insert(config, files, controlfiles_by_filename)
        # print(f"new events: {len(events)}")
        print(f"files: {len(files)}\tcontrol_files: {len(controlfiles_by_filename)}\tnew events: {len(events)}")

    def _get_files_from_server(self, config, remote_dir, storage_dir, dt_fecha1, dt_fecha2):
        sftp = self.sftp_service.getReference()
        try:
            sftp.chdir(remote_dir)
        except Exception as e:
            print(e)
            return []
            # raise Exception(f"El directorio {remote_dir} no existe")
        
        pattern = re.compile(config['file_pattern'])
        files = self.sftp_service.get_filename_and_updated_at(remote_dir, config['file_pattern'])
        files_filtered = []
        for row in files:
            str_date = pattern.search(row['file']).group(1)
            date_of_file = dt.datetime.strptime(str_date, config['file_date_format'])
            if dt_fecha1 <= date_of_file and date_of_file < dt_fecha2:
                files_filtered.append(row)

        return files_filtered

    def _get_files_with_access(self, files, files_permission):
        files_filtered = []
        pattern = re.compile("\-r..r..r..")
        if files_permission == "owner":
            pattern = re.compile("\-r........")
        elif files_permission == "group":
            pattern = re.compile("\-r..r.....")

        # print("files_filtered")
        for row in files:
            filemode = stat.filemode(row["st_mode"])
            if pattern.match(filemode) is not None:
                files_filtered.append(row)
            else:
                print({"file": row["file"], "filemode": filemode})
        return files_filtered

    def _get_controlfiles_by_filename(self, queue_id, dt_fecha1, dt_fecha2):
        files_of_control = self.control_carga_repo.getOfProyectWhereFechaArchivo(queue_id, dt_fecha1, dt_fecha2)
        files_by_filename = {}
        for file in files_of_control:
            files_by_filename[file["archivo"]] = file
        return files_by_filename

    def _get_event_to_insert(self, config, server_files, control_files_by_filename):
        events = []
        max_retries = self.max_retries
        if config.get("max_retries") is not None:
            max_retries = config["max_retries"]

        events_inserted = self.queue_service.find_by_queue_id_and_estado(config["queue_id"], [0,2])
        events_inserted_by_key = {}
        for row in events_inserted:
            if config.get('msg_send_filename', False):
                events_inserted_by_key[row['msg_body'].get('fec_ini')+'_'+row['msg_body'].get('filename')] = 1
            else:
                events_inserted_by_key[row['msg_body'].get('fec_ini')] = 1
        events_inserted = []

        for row in server_files:
            py_format = DTFORMAT_BY_ALIAS[config["event_format"]]
            str_filedate = row['filedate'].strftime(py_format)
            # event_inserted = None
            event_key = None
            if config.get('msg_send_filename', False):
                event_key = str_filedate+"_"+row['file']
            else:
                event_key = str_filedate
            event_inserted = events_inserted_by_key.get(event_key)

            if control_files_by_filename.get(row['file']) is None:
                if event_inserted is None:
                    events.append({'file': row['file'], 'filedate': str_filedate})
                    self.filename = row['file']
                    self.create_event(config, row['filedate'])
                    events_inserted_by_key[event_key] = 1
            else:
                cfile = control_files_by_filename[row['file']]
                if cfile['estado'] != self.succesfull_state and cfile["n_errors"] <= max_retries:
                    if event_inserted is None:
                        events.append({'file': row['file'], 'filedate': str_filedate})
                        self.filename = row['file']
                        self.create_event(config, row['filedate'])
                        events_inserted_by_key[event_key] = 1
        return events

    def create_event(self, config, filedate):
        py_format = DTFORMAT_BY_ALIAS[config["event_format"]]
        msg_body = {'fec_ini': filedate.strftime(py_format), 'format': config["event_format"]}
        if config.get("msg_send_granularity") == True:
            loop_time = json.loads(config["loop_time"])
            if config["event_format"] == "mxm":
                msg_body["granularity"] = loop_time["minutes"]
            elif config["event_format"] == "hxh":
                msg_body["granularity"] = loop_time["hours"]
            elif config["event_format"] == "dxd":
                msg_body["granularity"] = loop_time["days"]
        if config.get('msg_send_filename', False):
            msg_body["filename"] = self.filename
        msg_body = json.dumps(msg_body)
        self.queue_service.createEvent({'queue_id': config["queue_id"], 'msg_body': msg_body})