import json
import datetime as dt
import re

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
        files = self.sftp_service.get_filenames(config['work_dir'], config['file_pattern'])

        files_filtered = []
        pattern = re.compile(config['file_pattern'])

        for filename in files:
            str_date = pattern.search(filename).group(1)
            date_of_file = dt.datetime.strptime(str_date, config['file_date_format'])
            if dt_fecha1 <= date_of_file and date_of_file <= dt_fecha2:
                files_filtered.append({
                    'file': filename,
                    'str_filedate': date_of_file.strftime('%Y-%m-%d %H:%M')+":00",
                })
        
        return files_filtered
