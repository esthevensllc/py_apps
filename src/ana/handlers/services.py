import datetime as dt
import xlsxwriter
import os

class ReporteEvolucionGenerator:
    def __init__(self, db):
        self.db = db
        self.traffic_config = {
            'movil_voz pico': {'servicio': 'Voz Pico', 'red': 'Movil', 'medida': 'Mill. Minutos'},
            'movil_voz acum': {'servicio': 'Voz Acumulado', 'red': 'Movil', 'medida': 'Mill. Minutos'},
            'movil_datos pico': {'servicio': 'Datos Pico', 'red': 'Movil', 'medida': 'TB hora'},
            'movil_datos acum': {'servicio': 'Datos Acumulado', 'red': 'Movil', 'medida': 'TB dia'},
            'movil_facebook': {'servicio': 'Facebook', 'red': 'Movil', 'medida': '40.1%', 'med_text': 'TB dia'},
            'movil_youtube': {'servicio': 'Youtube', 'red': 'Movil', 'medida': '11.7%', 'med_text': 'TB dia'},
            'movil_whatsapp': {'servicio': 'Whatsapp', 'red': 'Movil', 'medida': '11.5%', 'med_text': 'TB dia'},
            'movil_instagram': {'servicio': 'Instagram', 'red': 'Movil', 'medida': '40.1%', 'med_text': 'TB dia'},
            'movil_tik tok': {'servicio': 'Tiktok', 'red': 'Movil', 'medida': '40.1%', 'med_text': 'TB dia'},
            'movil_netflix': {'servicio': 'Netflix', 'red': 'Movil', 'medida': '40.1%', 'med_text': 'TB dia'},
            'fijo_voz pico': {'servicio': 'Voz Pico', 'red': 'Fijo', 'medida': 'Miles Minutos Hora'},
            'fijo_voz acum': {'servicio': 'Voz Acumulado', 'red': 'Fijo', 'medida': 'Millones Minutos dia'},
            'fijo_datos pico': {'servicio': 'Datos Pico', 'red': 'Fijo', 'medida': 'Gbps'},
            'fijo_netflix': {'servicio': 'Netflix', 'red': 'Fijo', 'medida': '22.1%', 'med_text': 'TB dia'},
            'fijo_youtube': {'servicio': 'Youtube', 'red': 'Fijo', 'medida': '22.6%', 'med_text': 'TB dia'},
            'fijo_facebook': {'servicio': 'Facebook', 'red': 'Fijo', 'medida': '15.7%', 'med_text': 'TB dia'},
            'fijo_whatsapp': {'servicio': 'Whatsapp', 'red': 'Fijo', 'medida': '3.1%', 'med_text': 'TB dia'},
            'fijo_instagram': {'servicio': 'Instagram', 'red': 'Fijo', 'medida': '2.8%', 'med_text': 'TB dia'},
            'fijo_tik tok': {'servicio': 'Tiktok', 'red': 'Fijo', 'medida': '2.1%', 'med_text': 'TB dia'},
        }
        self.remote_path = "/opt/airflow/tareas/estadisticas/Reporte_Evolucion"

    def execute(self, month: dt.datetime = dt.datetime.strptime('2024-11','%Y-%m')):
        result = self.get_trafico(month)
        str_dates = self.get_day_headers(list(result.keys()))
        week_traffic = self.get_trafico_semana()

        if not os.path.exists(self.remote_path):
            os.makedirs(self.remote_path)

        filename = f"{self.remote_path}/Reporte_Evolucion_{month.strftime('%Y%m')}.xlsx"
        # workbook = xlsxwriter.Workbook(filename, {'constant_memory': True})
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()

        header_format = workbook.add_format({'bold': True, 'bg_color': 'FF0000', 'border': 1, 'font_color': 'white', 'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        header_format_week = workbook.add_format({'bold': True, 'bg_color': 'A9D08E', 'border': 1, 'font_color': 'white', 'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        header_format_prom = workbook.add_format({'bold': True, 'bg_color': 'F2F2F2', 'border': 1, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        body_format = workbook.add_format({'border': 1, 'align': 'center'})
        body_all_services_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'bold': True})
        body_services_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'bold': True, 'bg_color': 'DDEBF7'})
        body_porc_format = workbook.add_format({'border': 1, 'num_format': '0%', 'bg_color': 'FFF2CC', 'align': 'center'})
        body_porc_prom_format = workbook.add_format({'border': 1, 'num_format': '0%', 'bg_color': 'FFFF00', 'align': 'center'})

        worksheet.write(0, 0, 'Red', header_format)
        worksheet.set_column(0, 0, 13)
        worksheet.write(0, 1, 'Servicio', header_format)
        worksheet.set_column(1, 1, 20)
        worksheet.merge_range(0, 2, 0, 3, 'Medida', header_format)
        worksheet.set_column(3, 3, 10)

        col = 4
        for str_date in week_traffic['days']:
            worksheet.write(0, col, str_date, header_format_week)
            worksheet.set_column(col, col, 13)
            col += 1

        for row in [0]:
            col = 11
            for col_str in str_dates:
                worksheet.merge_range(row, col, row, col+1, col_str, header_format)
                col += 2
            worksheet.write(row, col, '% Variacion promedio por emergencia', header_format_prom)
            worksheet.set_column(col, col, 12)

        # write body

        # services
        row = 1
        for traffic_key in list(self.traffic_config.keys()):
            med_text = self.traffic_config[traffic_key].get('med_text')
            format_selected = body_all_services_format if med_text is None else body_services_format
            worksheet.write(row, 0, self.traffic_config[traffic_key]['red'], format_selected)
            worksheet.write(row, 1, self.traffic_config[traffic_key]['servicio'], format_selected)
            worksheet.write(row, 2, self.traffic_config[traffic_key]['medida'], format_selected)
            worksheet.write(row, 3, med_text, format_selected)
            if med_text is None:
                worksheet.merge_range(row, 2, row, 3, self.traffic_config[traffic_key]['medida'], format_selected)
            row += 1

        # base week
        row = 1
        col = 4
        for traffic_key in self.traffic_config.keys():
            worksheet.write(row, col, week_traffic[traffic_key][0], body_format)
            worksheet.write(row, col+1, week_traffic[traffic_key][1], body_format)
            worksheet.write(row, col+2, week_traffic[traffic_key][2], body_format)
            worksheet.write(row, col+3, week_traffic[traffic_key][3], body_format)
            worksheet.write(row, col+4, week_traffic[traffic_key][4], body_format)
            worksheet.write(row, col+5, week_traffic[traffic_key][5], body_format)
            worksheet.write(row, col+6, week_traffic[traffic_key][6], body_format)
            row += 1

        # month traffic
        row = 1
        first_week_index = 0
        for str_date in result.keys():
            first_week_index = dt.datetime.strptime(str_date, '%Y-%m-%d').weekday()
            break

        for traffic_key in self.traffic_config.keys():
            col = 11
            week_index = first_week_index
            last_week_excel = [None, None, None, None, None, None, None]
            base_week_excel = [self.get_excel_notation(row, windex+4) for windex in range(7)]
            for str_day in result.keys():
                worksheet.write(row, col, result[str_day].get(traffic_key), body_format)
                col += 1
                rowcol_traffic = self.get_excel_notation(row, col-1)
                rowcol_week = self.get_excel_notation(row, week_index+4)
                last_week_excel[week_index] = rowcol_traffic
                worksheet.write_formula(row, col, f"=+{rowcol_traffic}/{rowcol_week}-1", body_porc_format)
                col += 1
                week_index += 1
                if week_index > 6:
                    week_index = 0
            formula_promedio = f"+({'+'.join(last_week_excel)})/({'+'.join(base_week_excel)})-1"
            worksheet.write_formula(row, col, formula_promedio, body_porc_prom_format)
            row += 1

        # merge
        worksheet.merge_range(1, 0, 10, 0, 'Movil', body_all_services_format)
        worksheet.merge_range(11, 0, 19, 0, 'Fijo', body_all_services_format)

        workbook.close()

        self.generate_historico_apps(month)

    def generate_historico_apps(self, month):
        result = self.get_trafico(month)
        str_dates = list(map(lambda str_date: dt.datetime.strptime(str_date, '%Y-%m-%d').strftime('%d-%b'), result.keys()))
        week_traffic = self.get_trafico_semana()

        filename = f"{self.remote_path}/HISTORICO_APPS_{month.strftime('%Y%m')}.xlsx"
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()

        header_format = workbook.add_format({'bold': True, 'bg_color': 'FF0000', 'border': 1, 'font_color': 'white', 'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        body_format = workbook.add_format({'border': 1, 'align': 'center'})
        body_all_services_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'bold': True})
        body_services_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'bold': True, 'bg_color': 'DDEBF7'})

        worksheet.write(0, 0, 'Red', header_format)
        worksheet.set_column(0, 0, 13)
        worksheet.write(0, 1, 'Servicio', header_format)
        worksheet.set_column(1, 1, 20)
        worksheet.write(0, 2, '', header_format)
        worksheet.set_column(2, 2, 10)

        row = 0
        col = 3
        for col_str in str_dates:
            worksheet.write(row, col, col_str, header_format)
            worksheet.set_column(col, col, 12)
            col += 1

        worksheet.write(row, col, 'Red', header_format)
        # worksheet.set_column(col, col, 13)
        worksheet.write(row, col+1, 'Servicio', header_format)

        # body

        row = 1
        for traffic_key in list(self.traffic_config.keys()):
            col = 0
            med_text = self.traffic_config[traffic_key].get('med_text')
            if med_text is None:
                continue
            # format_selected = body_all_services_format if med_text is None else body_services_format
            worksheet.write(row, 0, self.traffic_config[traffic_key]['red'], body_services_format)
            worksheet.write(row, 1, self.traffic_config[traffic_key]['servicio'], body_services_format)
            # worksheet.write(row, 2, self.traffic_config[traffic_key]['medida'], format_selected)
            worksheet.write(row, 2, med_text, body_services_format)
            col += 3

            for str_day in result.keys():
                worksheet.write(row, col, result[str_day].get(traffic_key), body_format)
                col += 1

            worksheet.write(row, col, self.traffic_config[traffic_key]['red'], body_services_format)
            worksheet.set_column(col, col, 13)
            worksheet.write(row, col+1, self.traffic_config[traffic_key]['servicio'], body_services_format)
            worksheet.set_column(col+1, col+1, 20)
            col += 2
            row += 1

        worksheet.merge_range(1, 0, 6, 0, 'MOVIL', body_all_services_format)
        worksheet.merge_range(7, 0, 12, 0, 'FIJA', body_all_services_format)

        worksheet.merge_range(1, col-2, 6, col-2, 'MOVIL', body_all_services_format)
        worksheet.merge_range(7, col-2, 12, col-2, 'FIJA', body_all_services_format)

        workbook.close()


    def get_day_headers(self, dates):
        weekstr = ('Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo')
        dates_mapped = []
        for str_date in dates:
            dt_date = dt.datetime.strptime(str_date, '%Y-%m-%d')
            dates_mapped.append(f"{weekstr[dt_date.weekday()]} {dt_date.strftime('%d/%m')}")
        return dates_mapped

    def get_trafico(self, month: dt.datetime):
        query = """
        select * from
        (select to_char(dia, 'yyyy-mm-dd') dia, case when red = 'fija' then 'fijo' else red end red, servicio, traf_tb traffic from ana_historico_apps
        where dia >= to_date(:fecha_ini, 'yyyy-mm') and dia < to_date(:fecha_fin, 'yyyy-mm') + interval '1' month
        union all
        select to_char(dia, 'yyyy-mm-dd') dia, red, tipo servicio, trafico traffic from TP_TRAFICO_fija_REP
        where dia >= to_date(:fecha_ini_2, 'yyyy-mm') and dia < to_date(:fecha_fin_2, 'yyyy-mm') + interval '1' month
        union all
        select to_char(dia, 'yyyy-mm-dd') dia, red, tipo servicio, trafico traffic from TP_TRAFICO_movil_REP
        where dia >= to_date(:fecha_ini_3, 'yyyy-mm') and dia < to_date(:fecha_fin_3, 'yyyy-mm') + interval '1' month
        )
        order by dia
        """
        params = {
            'fecha_ini': month.strftime('%Y-%m'),
            'fecha_fin': month.strftime('%Y-%m'),
            'fecha_ini_2': month.strftime('%Y-%m'),
            'fecha_fin_2': month.strftime('%Y-%m'),
            'fecha_ini_3': month.strftime('%Y-%m'),
            'fecha_fin_3': month.strftime('%Y-%m'),
        }
        result = self.db.fetch(query, params)
        result_by_day = {}
        for row in result:
            key = f"{row[1]}_{row[2]}".lower()
            if result_by_day.get(row[0]) is None:
                result_by_day[row[0]] = {}
            result_by_day[row[0]][key] = row[3]
        return result_by_day

    def get_trafico_semana(self):
        return {
            'days': ['Lunes 09/03/2020', 'Martes 10/03/2020', 'Miercoles 11/03/2020', 'Jueves 12/03/2020', 'Viernes 06/03/2020', 'Sabado 07/03/2020', 'Domingo 08/03/2020'],
            'movil_voz pico': [15.11, 15.00, 15.09, 16.00, 14.60, 13.89, 12.91],
            'movil_voz acum': [216.7, 211.6, 215.9, 220.5, 214.4, 190.4, 173.9],
            'movil_datos pico': [16.47, 16.81, 16.92, 16.80, 16.92, 16.81, 16.83],
            'movil_datos acum': [2.542, 2.583, 2.625, 2.641, 2.667, 2.654, 2.677],
            'movil_facebook': [706.4, 722.1, 688.8, 710.8, 690.1, 717.0, 722.5],
            'movil_youtube': [337.2, 341.4, 316.8, 324.2, 330.2, 384.0, 397.1],
            'movil_whatsapp': [202.7, 200.0, 204.4, 212.2, 210.5, 216.1, 232.9],
            'movil_instagram': [132.1, 130.3, 120.8, 122.4, 126.2, 142.0, 145.8],
            'movil_tik tok': [34.3, 35.1, 34.4, 36.2, 32.4, 39.7, 39.8],
            'movil_netflix': [39.5, 38.7, 35.6, 37.0, 36.3, 45.3, 52.8],
            'fijo_voz pico': [543.7, 535.9, 559.2, 542.3, 459.0, 467.3, 471.4],
            'fijo_voz acum': [5.78, 5.71, 5.83, 6.07, 5.63, 4.16, 2.97],
            'fijo_datos pico': [691, 695, 700, 698, 691, 683, 687],
            'fijo_netflix': [53.0, 51.2, 49.0, 53.1, 50.6, 60.4, 67.7],
            'fijo_youtube': [74.6, 71.3, 66.3, 76.3, 74.1, 77.0, 72.8],
            'fijo_facebook': [20.0, 20.6, 20.6, 24.0, 19.6, 20.0, 21.0],
            'fijo_whatsapp': [4.5, 4.5, 4.7, 5.1, 4.7, 4.7, 5.5],
            'fijo_instagram': [6.4, 6.5, 6.1, 6.4, 6.7, 6.9, 7.3],
            'fijo_tik tok': [3.3, 3.3, 3.4, 3.9, 3.3, 3.7, 3.5],
        }

    def get_excel_notation(self, row, col):
        column_str = ''
        while col >= 0:
            column_str = chr(col % 26 + 65) + column_str
            col = col // 26 - 1
        row_str = str(row + 1)
        return f"{column_str}{row_str}"
        