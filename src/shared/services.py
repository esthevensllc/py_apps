from datetime import datetime
from datetime import timedelta
import calendar
import csv
import uuid
import json
import os

class AppService:
    def loopEachDay(self, fecha_ini, fecha_fin, handler):
        # fecha_ini = datetime.datetime.strptime('01/01/2022', '%d/%m/%Y')
        # fecha_fin = datetime.datetime.strptime('05/01/2022', '%d/%m/%Y')
        # diff_days = (fecha_fin - fecha_ini).days
        fecha_recorrido = fecha_ini
        while fecha_recorrido < fecha_fin:
            next_fecha = fecha_recorrido + timedelta(days=1)
            handler(fecha_recorrido, next_fecha)
            fecha_recorrido = next_fecha
    # datetime
    def loopEachMonth(self, mes_ini, mes_fin, handler):
        fecha_ini = datetime.strptime("01/"+mes_ini.strftime('%m/%Y'), '%d/%m/%Y')
        fecha_fin = datetime.strptime("01/"+mes_fin.strftime('%m/%Y'), '%d/%m/%Y')
        diff_days = (fecha_fin - fecha_ini).days
        fecha_recorrido = fecha_ini
        while fecha_recorrido < fecha_fin:
            days_of_month = calendar.monthrange(int(fecha_recorrido.strftime('%Y')), int(fecha_recorrido.strftime('%m')))[1]

            next_fecha = fecha_recorrido + timedelta(days=days_of_month)
            # service.execute(fecha_recorrido.strftime('%d/%m/%Y'), next_fecha.strftime('%d/%m/%Y'))
            handler(fecha_recorrido, next_fecha)
            # print("{} - {}".format(fecha_recorrido.strftime('%d/%m/%Y'), next_fecha.strftime('%d/%m/%Y')))
            fecha_recorrido = next_fecha

    def upload_files(self, fecha1, fecha2, work_dir, files_to_upload, delete_where_collectiontime_between_handler, insert_from_array_handler, offset=1, func_map_item = None):
        if len(files_to_upload) == 0:
            raise Exception("No hay archivos para procesar")
        # no incluye la ultima fecha
        delete_where_collectiontime_between_handler(fecha1, fecha2)
        main_counter = 0
        for fichero in files_to_upload:
            start_time = datetime.now()
            with open(work_dir+fichero['file'], newline='') as csvfile:
                # reader = csv.DictReader(csvfile)
                reader = csv.reader(csvfile)
                
                registros_to_insert = []
                counter = 0
                for row in reader:
                    counter = counter + 1
                    if counter <= offset:
                        continue
                    main_counter = main_counter + 1

                    row_to_add = row
                    if func_map_item is not None:
                        row_to_add = func_map_item(row)
                    # print(row_to_add)
                    
                    registros_to_insert.append(row_to_add)
                
                end_time = datetime.now()
                insert_from_array_handler(registros_to_insert, fichero, start_time, end_time)
        print("{} registros insertados".format(main_counter))


class SimplePaginator:
    def __init__(self, servers, perPage):
        self._data = servers
        self._perPage = perPage
        self._data_by_page = {}
        len_servers = len(servers)
        lastIndex = 0
        i = perPage-1
        actual_page = 1
        while i <= len_servers or lastIndex < len_servers:
            #print(f"{i-(perPage-1)} - {i}")
            #print(servers[i-(perPage-1):i+1])
            data_to_add = servers[i-(perPage-1):i+1]
            if len(data_to_add) == 0:
                break
            self._data_by_page[actual_page] = data_to_add
            lastIndex = i
            i += perPage
            actual_page += 1

    def get_num_pages(self) -> int:
        return len(self._data_by_page.keys())

    def get_page(self, page):
        if self._data_by_page.get(page) is None:
            raise Exception("La pagina no existe")
        return self._data_by_page[page]


class TempDataManager:
    def __init__(self, limit, path, filename=None):
        self.data = []
        self.limit = limit
        self.path = path
        self.filename = filename
        if filename is None:
            self.filename = str(uuid.uuid4())
        self.file_counter = 1

    def add(self, row):
        self.data.append(row)
        if len(self.data) >= self.limit:
            self._save_to_file()
            self.data = []

    def count(self):
        return ((self.file_counter - 1) * self.limit) + len(self.data)

    def _save_to_file(self):
        filepath = f"{self.path}/{self.filename}_{self.file_counter}.json"
        print(f"{filepath} - {len(self.data)}")
        with open(filepath, "w") as tempfile:
            json.dump(self.data, tempfile)
        self.file_counter += 1

    def _get_and_delete_file(self, filepath):
        data = []
        with open(filepath, "r") as tempfile:
            data = json.loads(tempfile.read())
        os.unlink(filepath)
        return data

    def get(self):
        if len(self.data) > 0:
            self._save_to_file()
            self.data = []

        file_counter = 1
        while file_counter < self.file_counter:
            filepath = f"{self.path}/{self.filename}_{file_counter}.json"
            yield self._get_and_delete_file(filepath)
            file_counter += 1
        self.file_counter = 1