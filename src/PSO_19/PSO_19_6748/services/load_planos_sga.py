import csv
from src.shared.config import STORAGE_DIR

class load_planos_sga:
    def __init__(self, repository):
        self.repository = repository
        self.dir_csv=STORAGE_DIR+"pso_19/PLANOS_SGA.csv"
    
    def execute(self):
        with open(self.dir_csv, newline='') as csvfile:
            # reader = csv.DictReader(csvfile)
            reader = csv.reader(csvfile)
            
            registros_to_insert = []
            counter = 0
            for row in reader:
                counter += 1
                if counter == 1:
                    continue
                registros_to_insert.append({'item': row[0], 'idplano': row[1], 'descripcion': row[2], 'hhpp_totales': row[3]})
            # print(registros_to_insert)
            self.repository.recargar_from_array_to_homepass_temp(registros_to_insert)