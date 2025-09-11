import json
import datetime as dt
import re
import stat

class ConfigFinder:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, context):
        config = self.repo.find(context['config_id'])
        if config is not None:
            config['fields'] = self.repo.get_fields_by_id(context['config_id'])
        context['config'] = config
        return context

# finders

class SftpFinder:
    def __init__(self, sftp_service):
        self.sftp_service = sftp_service

    def execute(self, config, dt_fecha1, dt_fecha2):
        self.sftp_service.useConnection(config['server_id'])
        files = []
        if '{str_date}' in config['work_dir']:
            wk_loop_time = config.get('wk_loop_time')
            wk_date_format = config.get('wk_date_format')

            dt_fecha_recorrido = dt_fecha1
            delta = dt.timedelta(**json.loads(wk_loop_time))
            while dt_fecha_recorrido.strftime(wk_date_format) <= dt_fecha2.strftime(wk_date_format):
                str_date = dt_fecha_recorrido.strftime(wk_date_format)
                dt_fecha_recorrido = dt_fecha_recorrido + delta

                work_dir = config['work_dir'].replace("{str_date}", str_date)
                work_dir_exists = False
                try:
                    stat.S_ISDIR(self.sftp_service.getReference().stat(work_dir).st_mode)
                    work_dir_exists = True
                except FileNotFoundError:
                    # print(f"El directorio no existe: {work_dir}")
                    pass
                if work_dir_exists:
                    files_to_add = self.sftp_service.get_filenames(work_dir, config['file_pattern'])
                    files_to_add = list(map(lambda filename: {'file': filename, 'subdir': str_date}, files_to_add))
                    files += files_to_add
                    files_to_add = []
        else:
            files_to_add = self.sftp_service.get_filenames(config['work_dir'], config['file_pattern'])
            files_to_add = list(map(lambda filename: {'file': filename}, files_to_add))
            files += files_to_add
            files_to_add = []

        files_filtered = []
        pattern = re.compile(config['file_pattern'])

        for row in files:
            filename = row['file']
            str_date = pattern.search(filename).group(1)
            date_of_file = dt.datetime.strptime(str_date, config['file_date_format'])
            if dt_fecha1 <= date_of_file and date_of_file <= dt_fecha2:
                files_filtered.append({
                    'file': filename,
                    'subdir': row.get('subdir'),
                    'str_filedate': date_of_file.strftime('%Y-%m-%d %H:%M')+":00",
                })
        
        return files_filtered
