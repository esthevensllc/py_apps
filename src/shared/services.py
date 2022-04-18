from datetime import datetime
from datetime import timedelta
import calendar
import csv

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