from src.shared.config import STORAGE_DIR, BASE_DIR
import datetime
import subprocess as subp
import os
import csv

class LoadCSV:
    def __init__(self, repository, remote_connect):
        self.repository = repository
        self.remote_connect = remote_connect
        self.dir_base = '/hfs_public/nbi/text/pfm_output'
        self.storage_dir = STORAGE_DIR+'NCE'
    
    def execute(self, codigo_medicion = 'PM_IG30029', fecha = None):
        fecha = datetime.datetime.strptime('2022-05-05 15:00', '%Y-%m-%d %H:%M')

        base_config = self.repository.find_by_codigo_med(codigo_medicion)
        if base_config == None:
            raise f"El codigo_medicion '{codigo_medicion}' no existe"
        
        fields = self.repository.get_fields_by_codigo_med(codigo_medicion)
        remote_dir = f"{self.dir_base}/{fecha.strftime('%Y%m%d')}"
        storage_dir = f"{self.storage_dir}/{base_config['codigo_medicion']}"
        str_to_filter = f"{base_config['codigo_medicion']}_{base_config['granularidad']}*{fecha.strftime('%Y%m%d')}*.csv"

        subp.run(['sh', f"{BASE_DIR}src/nce/shared/util_get_files_from_nce.sh", remote_dir, f"{self.storage_dir}/{base_config['codigo_medicion']}", str_to_filter])
        csv_files = os.listdir(storage_dir)
        for filename in csv_files:
            with open(f"{storage_dir}/{filename}", newline='') as csvfile:
                reader = csv.reader(csvfile)
                print(type(reader))
            break

        print(csv_files)
        

