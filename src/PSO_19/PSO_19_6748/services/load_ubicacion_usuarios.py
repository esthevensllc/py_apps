import requests
import json
from src.shared.config import (BASE_DIR, STORAGE_DIR)
from src.PSO_19.PSO_19_6748.repository import PSO_19_6748_Repository

class load_ubicacion_usuarios:
    def __init__(self, repository):
        self.repository = repository
        self.dir_csv="files/usuarios_ifi_ubicacion.csv"

    def execute(self):
        file = open(BASE_DIR+self.dir_csv, 'r')
        file.readline()
        rows_to_temp_space = []
        counter = 0
        for v_line in file:
            counter = counter +1
            # print(counter)
            row = v_line.replace('\n', '').split(',')
            row = {"msisdm": row[0], "lat_base": row[1], "lon_base": row[2]}
            # registro_finded = self.repository.find_by_msisdm(row['msisdm'])
            rows_to_temp_space.append(row)
        
        print("Cargando PSO_0DATA_19_6748_TEST")
        self.repository.insert_from_array_to_temp_space(rows_to_temp_space)
        self.repository.load_from_temp_space()
        file.close()
        # self.repository.db.__disconnect__()
