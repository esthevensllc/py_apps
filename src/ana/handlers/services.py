from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.ana.shared.services import (
    REPORTE_EVOLUCION_GENERATOR,
    TRAFICO_3G_2G_GENERATOR,
    REP_MAGGIE_GENERATOR,
    REP_BANDAS_GENERATOR,
    REP_MEXICO_GENERATOR
)
from src.shared.config import DTFORMAT_BY_ALIAS

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

    def execute(self, month: dt.datetime):
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

    def event_handler(self, event):
        self.__guard(event)
        date_format = DTFORMAT_BY_ALIAS[event['msg_body']['format']]
        fecha = dt.datetime.strptime(event['msg_body']['fec_ini'], date_format)
        self.execute(fecha)

    def __guard(self, event):
        msg_body_keys = event['msg_body'].keys()
        if 'fec_ini' not in msg_body_keys or 'format' not in msg_body_keys:
            raise Exception("Error no se encontro el atributo fec_ini o format")

        if event['msg_body']['format'] not in list(DTFORMAT_BY_ALIAS):
            raise Exception(f"Formato '{event['msg_body']['format']}' no valido")
        

class Trafico3g2gGenerator:
    def __init__(self, db):
        self.db = db
        self.remote_path = "/opt/airflow/tareas/estadisticas/Reporte_Evolucion"
        self.months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Setiembre", "Octubre", "Noviembre", "Diciembre"]
        self.headers = ["MES", "2G","3G","% 3G","2G","3G",'% 3G',"4G_MOVIL", "4G_LTE_TDD"]

    def execute(self, month: dt.datetime):
        params = {'fecha_ini': '01'+month.strftime('/%m/%Y'), 'fecha_fin': '01'+month.strftime('/%m/%Y')}
        self.db.callproc("PK_REPORTES_MENSUALES_MEXICO.SP_ALL(:fecha_ini, to_char(to_date(:fecha_fin, 'dd/mm/yyyy') + interval '1' month, 'dd/mm/yyyy'))", params)
        result = self.get_traffic(month)

        filename = f"{self.remote_path}/Trafico_2g_vs_3g_{month.strftime('%Y%m')}.xlsx"
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()

        header_format = workbook.add_format({'bold': True, 'bg_color': 'C0C0C0', 'border': 1, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        header_voz_format = workbook.add_format({'font_size': 12, 'bold': True, 'bg_color': '99CCFF', 'border': 1, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        header_datos_format = workbook.add_format({'font_size': 12, 'bold': True, 'bg_color': 'FF0000', 'border': 1, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        body_format = workbook.add_format({'border': 1, 'align': 'center', 'num_format': '#,##0'})
        body_porc_format = workbook.add_format({'border': 1, 'num_format': '0.0%', 'align': 'center'})
        body_total_format = workbook.add_format({'font_size': 12, 'bold': True, 'border': 1, 'align': 'center', 'num_format': '#,##0'})
        body_total_porc_format = workbook.add_format({'font_size': 12, 'bold': True, 'border': 1, 'num_format': '0.0%', 'align': 'center'})

        worksheet.merge_range(0, 2, 0, 4, 'Tráfico Voz (Miles Erlangs)', header_voz_format)
        worksheet.merge_range(0, 5, 0, 9, 'Tráfico Datos (GB)', header_datos_format)

        row = 1
        col = 1
        for header in self.headers:
            worksheet.write(row, col, header, header_format)
            worksheet.set_column(col, col, 15)
            col += 1

        # write body
        row_index = 2
        col_index = 1
        last_month = 1
        total_voz_2g = 0
        total_voz_3g = 0
        total_datos_2g = 0
        total_datos_3g = 0
        total_datos_4g_movil = 0
        total_datos_4g_lte = 0
        for row in result:
            last_month = row[0].month
            str_month = self.months[row[0].month - 1]
            # print(row_index, col_index, 1)
            worksheet.write(row_index, col_index, str_month, body_format)
            worksheet.write(row_index, col_index+1, row[1], body_format)
            worksheet.write(row_index, col_index+2, row[2], body_format)
            worksheet.write(row_index, col_index+3, row[3], body_porc_format)
            worksheet.write(row_index, col_index+4, row[4], body_format)
            worksheet.write(row_index, col_index+5, row[5], body_format)
            worksheet.write(row_index, col_index+6, row[6], body_porc_format)
            worksheet.write(row_index, col_index+7, row[7], body_format)
            worksheet.write(row_index, col_index+8, row[8], body_format)
            if row[1] is not None:
                total_voz_2g += row[1]
            if row[2] is not None:
                total_voz_3g += row[2]
            if row[4] is not None:
                total_datos_2g += row[4]
            if row[5] is not None:
                total_datos_3g += row[5]
            if row[7] is not None:
                total_datos_4g_movil += row[7]
            if row[8] is not None:
                total_datos_4g_lte += row[8]

            row_index += 1

            if row[0].month == 12:
                total_voz_porc_3g = total_voz_3g / (total_voz_2g+total_voz_3g) if (total_voz_2g+total_voz_3g) != 0 else 0
                total_datos_porc_3g = total_datos_3g / (total_datos_2g+total_datos_3g) if (total_datos_2g+total_datos_3g) != 0 else 0
                worksheet.write(row_index, col_index, f"Total {row[0].strftime('%Y')}", body_total_format)
                worksheet.write(row_index, col_index+1, total_voz_2g, body_total_format)
                worksheet.write(row_index, col_index+2, total_voz_3g, body_total_format)
                worksheet.write(row_index, col_index+3, total_voz_porc_3g, body_total_porc_format)
                worksheet.write(row_index, col_index+4, total_datos_2g, body_total_format)
                worksheet.write(row_index, col_index+5, total_datos_3g, body_total_format)
                worksheet.write(row_index, col_index+6, total_datos_porc_3g, body_total_porc_format)
                worksheet.write(row_index, col_index+7, total_datos_4g_movil, body_total_format)
                worksheet.write(row_index, col_index+8, total_datos_4g_lte, body_total_format)
                row_index += 1
                # reset acum
                total_voz_2g = 0
                total_voz_3g = 0
                total_datos_2g = 0
                total_datos_3g = 0
                total_datos_4g_movil = 0
                total_datos_4g_lte = 0

        workbook.close()
        print(f"{filename} created")

    def get_traffic(self, month):
        query = """SELECT
        MES, ROUND(VOZ_2G) VOZ_2G,
        ROUND(VOZ_3G) VOZ_3G,
        ROUND(VOZ_PORC_3G, 2) VOZ_PORC_3G,
        ROUND(DATOS_2G) DATOS_2G,
        ROUND(DATOS_3G) DATOS_3G,
        ROUND(DATOS_PORC_3G, 2) DATOS_PORC_3G,
        ROUND(DATOS_4G_MOVIL) DATOS_4G_MOVIL,
        ROUND(DATOS_4G_LTE_TDD) DATOS_4G_LTE_TDD
        FROM padm_reporte_traffic_2g_3g
        WHERE MES <= TO_DATE(:p_mes, 'yyyy-mm-dd')
        ORDER BY MES"""
        result = self.db.fetch(query, {'p_mes': month.strftime('%Y-%m-')+'01'})
        mapped_result = [row for row in result]
        last_month = result[len(result)-1][0]
        if last_month.month < 12:
            month_loop = last_month.month + 1
            while month_loop <= 12:
                str_month = last_month.strftime('%Y-')+f"{month_loop:02}"+"-01"
                mapped_result.append([dt.datetime.strptime(str_month, '%Y-%m-%d'), None, None, None, None, None, None, None, None])
                month_loop = month_loop + 1
        return mapped_result

    def event_handler(self, event):
        self.__guard(event)
        date_format = DTFORMAT_BY_ALIAS[event['msg_body']['format']]
        fecha = dt.datetime.strptime(event['msg_body']['fec_ini'], date_format)
        self.execute(fecha)

    def __guard(self, event):
        msg_body_keys = event['msg_body'].keys()
        if 'fec_ini' not in msg_body_keys or 'format' not in msg_body_keys:
            raise Exception("Error no se encontro el atributo fec_ini o format")

        if event['msg_body']['format'] not in list(DTFORMAT_BY_ALIAS):
            raise Exception(f"Formato '{event['msg_body']['format']}' no valido")


class RepMaggieGenerator:
    def __init__(self, db):
        self.db = db
        self.remote_path = "/opt/airflow/tareas/estadisticas/Reporte_Evolucion"

    def execute(self, month: dt.datetime):
        headers = ['SITE_NAME', 'SITE_ADDRESS', 'META_TRAFICO_MB_CAPACIDAD', 'OCUPACION_SITE']
        data = self.get_data(month)

        filename = f"{self.remote_path}/Capacidad_MB_HR_Sitios_{month.strftime('%Y%m')}.xlsx"
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()

        header_format = workbook.add_format({'bold': True})
        body_format = workbook.add_format({})

        row = 0
        col = 0
        for header in headers:
            worksheet.write(row, col, header, header_format)
            col += 1

        worksheet.set_column(0, 0, 15)
        worksheet.set_column(1, 1, 50)
        worksheet.set_column(2, 2, 30)
        worksheet.set_column(3, 3, 20)

        row_index = 1
        col = 0
        for row in data:
            worksheet.write(row_index, col, row[0], body_format)
            worksheet.write(row_index, col+1, row[1], body_format)
            worksheet.write_number(row_index, col+2, row[2], body_format)
            worksheet.write_number(row_index, col+3, row[3], body_format)
            row_index += 1

        workbook.close()
        print(f"{filename} created {len(data)}")

    def get_data(self, month: dt.datetime):
        year = int(month.strftime('%Y'))
        str_month = month.strftime('%Y-%m-')+'01'
        query = """
        select
            site_name,
            site_address,
            round(sum(meta_trafico_mb_capacidad)) meta_trafico_mb_capacidad,
            round(case when (case when sum(meta_trafico_mb_capacidad)>0 then sum(mac_volumen_capacidad)/sum(meta_trafico_mb_capacidad) end) > 1 then 1
                else (case when sum(meta_trafico_mb_capacidad)>0 then sum(mac_volumen_capacidad)/sum(meta_trafico_mb_capacidad) end)
            end*100,2) ocupacion_site
        from (
        select anio,semana, mbts,enodob_name,enodob_address, site_name,site_address,sector_name,
        case when sum(dl_th_kbps_den) > 0 then sum(dl_th_kbps_num)/sum(dl_th_kbps_den) end dl_th_mbps,
        case when sum(dl_prb_den) > 0 then sum(dl_prb_num)/sum(dl_prb_den) end dl_prb,
        avg(mac_volumen_capacidad) mac_volumen_capacidad,
        avg(meta_trafico_mb_capacidad) meta_trafico_mb_capacidad,
        case when sum(dl_th_kbps_den_700) > 0 then sum(dl_th_kbps_num_700)/sum(dl_th_kbps_den_700) end dl_th_mbps_700,
        case when sum(dl_th_kbps_den_1900) > 0 then sum(dl_th_kbps_num_1900)/sum(dl_th_kbps_den_1900) end dl_th_mbps_1900,
        case when sum(dl_th_kbps_den_2600) > 0 then sum(dl_th_kbps_num_2600)/sum(dl_th_kbps_den_2600) end dl_th_mbps_2600,
        case when sum(dl_th_kbps_den_2600_b38) > 0 then sum(dl_th_kbps_num_2600_b38)/sum(dl_th_kbps_den_2600_b38) end dl_th_mbps_2600_b38,
        case when sum(dl_prb_den_700) > 0 then sum(dl_prb_num_700)/sum(dl_prb_den_700) end dl_prb_700,
        case when sum(dl_prb_den_1900) > 0 then sum(dl_prb_num_1900)/sum(dl_prb_den_1900) end dl_prb_1900,
        case when sum(dl_prb_den_2600) > 0 then sum(dl_prb_num_2600)/sum(dl_prb_den_2600) end dl_prb_2600,
        case when sum(dl_prb_den_2600_b38) > 0 then sum(dl_prb_num_2600_b38)/sum(dl_prb_den_2600_b38) end dl_prb_2600_b38
        from (
        select
            anio,semana,mbts,enodob_name,enodob_address,site_name,site_address,sector_name,
            dl_th_kbps_num,
            dl_th_kbps_den,
            dl_prb_num,
            dl_prb_den,
            mac_volumen_capacidad,meta_trafico_mb_capacidad,freqband,
            case when freqband = '700 MHz' then dl_th_kbps_num end dl_th_kbps_num_700,
            case when freqband = '1900 MHz' then dl_th_kbps_num end dl_th_kbps_num_1900, 
            case when freqband = '2.6 GHz' and upper(carrier) not in ('C11','C8') then dl_th_kbps_num end dl_th_kbps_num_2600,
            case when freqband = '2.6 GHz' and upper(carrier) in ('C11','C8') then dl_th_kbps_num end dl_th_kbps_num_2600_b38,
            case when freqband = '700 MHz' then dl_th_kbps_den end dl_th_kbps_den_700,
            case when freqband = '1900 MHz' then dl_th_kbps_den end dl_th_kbps_den_1900, 
            case when freqband = '2.6 GHz' and upper(carrier) not in ('C11','C8') then dl_th_kbps_den end dl_th_kbps_den_2600,
            case when freqband = '2.6 GHz' and upper(carrier) in ('C11','C8') then dl_th_kbps_den end dl_th_kbps_den_2600_b38,          
            case when freqband = '700 MHz' then dl_prb_num end dl_prb_num_700,
            case when freqband = '1900 MHz' then dl_prb_num end dl_prb_num_1900, 
            case when freqband = '2.6 GHz' and upper(carrier) not in ('C11','C8') then dl_prb_num end dl_prb_num_2600,
            case when freqband = '2.6 GHz' and upper(carrier) in ('C11','C8') then dl_prb_num end dl_prb_num_2600_b38,
            case when freqband = '700 MHz' then dl_prb_den end dl_prb_den_700,
            case when freqband = '1900 MHz' then dl_prb_den end dl_prb_den_1900, 
            case when freqband = '2.6 GHz' and upper(carrier) not in ('C11','C8') then dl_prb_den end dl_prb_den_2600,
            case when freqband = '2.6 GHz' and upper(carrier) in ('C11','C8') then dl_prb_den end dl_prb_den_2600_b38
        from smart.SEM_BH_INDICADORES_4G
        WHERE
            anio = to_number(:p_year)
            AND semana = (select max(semana) from smmics where mes = TO_date(:p_month,'YYYY-MM-DD'))
        and tipo_bh = 'USUARIO'
        and meta_trafico_mb_capacidad is not null
        )
        group by anio,semana,
        mbts,enodob_name,enodob_address,
        site_name,site_address,sector_name
        )
        group by site_name, site_address
        """

        result = self.db.fetch(query, {'p_year': year, 'p_month': str_month})
        return result

    def event_handler(self, event):
        self.__guard(event)
        date_format = DTFORMAT_BY_ALIAS[event['msg_body']['format']]
        fecha = dt.datetime.strptime(event['msg_body']['fec_ini'], date_format)
        self.execute(fecha)

    def __guard(self, event):
        msg_body_keys = event['msg_body'].keys()
        if 'fec_ini' not in msg_body_keys or 'format' not in msg_body_keys:
            raise Exception("Error no se encontro el atributo fec_ini o format")

        if event['msg_body']['format'] not in list(DTFORMAT_BY_ALIAS):
            raise Exception(f"Formato '{event['msg_body']['format']}' no valido")


class RepBandasGenerator:
    def __init__(self, db):
        self.db = db
        self.remote_path = "/opt/airflow/tareas/estadisticas/Reporte_Evolucion"
        self.headers = ['Mes','Banda 850', 'Banda 1900','Banda 850','Banda 1900','Banda 850', 'Banda 1900', 'Banda 850', 'Banda 1900', 'Banda 850', 'Banda 1900', 'Banda 850', 'Banda 1900']
        self.months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Setiembre", "Octubre", "Noviembre", "Diciembre"]

    def execute(self, month: dt.datetime = dt.datetime.strptime('2024-11-01', '%Y-%m-%d')):
        data = self.get_data(month)

        filename = f"{self.remote_path}/Reporte_Banda(PorcentajeBanda_{month.strftime('%Y%m')}).xlsx"
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()

        header_voz_format = workbook.add_format({'font_size': 12, 'bold': True, 'bg_color': '00CDFF', 'border': 1, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        header_datos_format = workbook.add_format({'font_size': 12, 'bold': True, 'bg_color': 'FF3A00', 'border': 1, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        header_voz_format_gb = workbook.add_format({'font_size': 12, 'bold': True, 'bg_color': 'FFFF00', 'border': 1, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        header_tec = workbook.add_format({'font_size': 12, 'bold': True, 'bg_color': 'C2BEBE', 'border': 1, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1, 'valign': 'vcenter'})
        body_format = workbook.add_format({'align': 'center', 'num_format': '#,##0', 'border': 1})
        body_total_2g = workbook.add_format({'align': 'center', 'num_format': '#,##0', 'border': 1, 'bg_color': 'FFFF00'})
        body_total_3g = workbook.add_format({'align': 'center', 'num_format': '#,##0', 'border': 1, 'bg_color': 'FFBC66'})
        body_total = workbook.add_format({'align': 'center', 'num_format': '#,##0', 'bg_color': '07F01B'})
        body_porc_format = workbook.add_format({'border': 1, 'num_format': '0%', 'align': 'center'})

        worksheet.merge_range(1, 0, 3, 0, month.strftime('%Y'), header_format)

        worksheet.merge_range(1, 1, 1, 4, 'Tráfico Voz (Miles Erlangs)', header_voz_format)
        worksheet.merge_range(1, 5, 1, 8, 'Tráfico Datos (GB)', header_datos_format)
        worksheet.merge_range(1, 9, 1, 12, 'Tráfico Voz (GB)', header_voz_format_gb)
        worksheet.merge_range(1, 13, 1, 14, 'Tráfico Datos (GB)', header_voz_format_gb)

        worksheet.merge_range(2, 1, 2, 2, '2G', header_tec)
        worksheet.merge_range(2, 3, 2, 4, '3G', header_tec)
        worksheet.merge_range(2, 5, 2, 6, '2G', header_tec)
        worksheet.merge_range(2, 7, 2, 8, '3G', header_tec)
        worksheet.merge_range(2, 9, 2, 10, '2G', header_tec)
        worksheet.merge_range(2, 11, 2, 12, '3G', header_tec)
        worksheet.merge_range(2, 13, 3, 13, 'Banda 850', header_tec)
        worksheet.set_column(13, 13, 15)
        worksheet.merge_range(2, 14, 3, 14, 'Banda 1900', header_tec)
        worksheet.set_column(14, 14, 15)

        row_index = 3
        col_index = 0
        for header in self.headers:
            worksheet.write(row_index, col_index, header, header_format)
            worksheet.set_column(col_index, col_index, 15)
            col_index += 1

        row_index += 1
        col = 0
        for str_date in data.keys():
            row = data[str_date]
            worksheet.write(row_index, col, row.get('MES'), body_format)
            worksheet.write_number(row_index, col+1, row.get('2G_VOZ_BANDA 850'), body_format)
            worksheet.write_number(row_index, col+2, row.get('2G_VOZ_BANDA 1900'), body_format)
            worksheet.write_number(row_index, col+3, row.get('3G_VOZ_BANDA 850'), body_format)
            worksheet.write_number(row_index, col+4, row.get('3G_VOZ_BANDA 1900'), body_format)

            worksheet.write_number(row_index, col+5, row.get('2G_DATOS_BANDA 850'), body_format)
            worksheet.write_number(row_index, col+6, row.get('2G_DATOS_BANDA 1900'), body_format)
            worksheet.write_number(row_index, col+7, row.get('3G_DATOS_BANDA 850'), body_format)
            worksheet.write_number(row_index, col+8, row.get('3G_DATOS_BANDA 1900'), body_format)

            worksheet.write(row_index, col+9, row.get('2G_VOZ_GB_BANDA 850'), body_format)
            worksheet.write(row_index, col+10, row.get('2G_VOZ_GB_BANDA 1900'), body_format)
            worksheet.write(row_index, col+11, row.get('3G_VOZ_GB_BANDA 850'), body_format)
            worksheet.write(row_index, col+12, row.get('3G_VOZ_GB_BANDA 1900'), body_format)

            worksheet.write(row_index, col+13, row.get('DATOS_BANDA 850'), body_format)
            worksheet.write(row_index, col+14, row.get('DATOS_BANDA 1900'), body_format)
            
            row_index += 2

            worksheet.write_number(row_index, col+1, row.get('2G_VOZ'), body_total_2g)
            # worksheet.write_number(row_index, col+2, row.get('2G_VOZ_BANDA 1900'), body_format)
            worksheet.write_number(row_index, col+3, row.get('3G_VOZ'), body_total_3g)
            # worksheet.write_number(row_index, col+4, row.get('3G_VOZ_BANDA 1900'), body_format)

            worksheet.write_number(row_index, col+5, row.get('2G_DATOS'), body_total_2g)
            # worksheet.write_number(row_index, col+6, row.get('2G_DATOS_BANDA 1900'), body_format)
            worksheet.write_number(row_index, col+7, row.get('3G_DATOS'), body_total_3g)
            # worksheet.write_number(row_index, col+8, row.get('3G_DATOS_BANDA 1900'), body_format)

            worksheet.write(row_index-1, col+5, None, body_total)
            worksheet.write(row_index-1, col+6, None, body_total)
            worksheet.write(row_index-1, col+7, None, body_total)
            worksheet.write(row_index-1, col+8, None, body_total)
            worksheet.write(row_index-1, col+9, row.get('2G_VOZ_GB'), body_total)
            worksheet.write(row_index-1, col+10, None, body_total)
            worksheet.write(row_index-1, col+11, row.get('3G_VOZ_GB'), body_total)

            value = (row.get('2G_VOZ_GB') / (row.get('2G_VOZ_GB') + row.get('3G_VOZ_GB')))
            worksheet.write(row_index, col+9, value, body_porc_format)
            value = (row.get('3G_VOZ_GB') / (row.get('2G_VOZ_GB') + row.get('3G_VOZ_GB')))
            worksheet.write(row_index, col+11, value, body_porc_format)

            row_index += 1

        workbook.close()
        print(f"{filename} created {len(data)}")

    def get_data(self, month: dt.datetime):
        query = """
        select TO_CHAR(MES, 'YYYY-MM-DD') MES, TECNOLOGIA, TIPO, BANDA, trafico from mensual_bandas
        WHERE MES = TO_date(:p_month,'YYYY-MM-DD') AND TECNOLOGIA IN ('2G', '3G')
        """
        str_month = month.strftime('%Y-%m-')+'01'
        result = self.db.fetch(query, {'p_month': str_month})
        result_by_tec = {}
        for row in result:
            key = row[0]
            field_key = f"{row[1]}_{row[2]}_{row[3]}"
            if result_by_tec.get(key) is None:
                result_by_tec[key] = {field_key: row[4]}
            else:
                result_by_tec[key][field_key] = row[4]

            result_by_tec[key]['MES'] = self.months[dt.datetime.strptime(key, '%Y-%m-%d').month]
        
        for str_date in result_by_tec.keys():
            row = result_by_tec[str_date]
            result_by_tec[str_date]['2G_VOZ_GB_BANDA 850'] = ((row.get('2G_VOZ_BANDA 850')*1000)*(12.2*3600))/(8*1024*1024)
            result_by_tec[str_date]['2G_VOZ_GB_BANDA 1900'] = ((row.get('2G_VOZ_BANDA 1900')*1000)*(12.2*3600))/(8*1024*1024)
            result_by_tec[str_date]['3G_VOZ_GB_BANDA 850'] = ((row.get('3G_VOZ_BANDA 850')*1000)*(12.2*3600))/(8*1024*1024)
            result_by_tec[str_date]['3G_VOZ_GB_BANDA 1900'] = ((row.get('3G_VOZ_BANDA 1900')*1000)*(12.2*3600))/(8*1024*1024)
            result_by_tec[str_date]['DATOS_BANDA 850'] = row.get('2G_DATOS_BANDA 850') + row.get('3G_DATOS_BANDA 850')
            result_by_tec[str_date]['DATOS_BANDA 1900'] = row.get('2G_DATOS_BANDA 1900') + row.get('3G_DATOS_BANDA 1900')
            result_by_tec[str_date]['2G_VOZ'] = row.get('2G_VOZ_BANDA 850') + row.get('2G_VOZ_BANDA 1900')
            result_by_tec[str_date]['3G_VOZ'] = row.get('3G_VOZ_BANDA 850') + row.get('3G_VOZ_BANDA 1900')
            result_by_tec[str_date]['2G_DATOS'] = row.get('2G_DATOS_BANDA 850') + row.get('2G_DATOS_BANDA 1900')
            result_by_tec[str_date]['3G_DATOS'] = row.get('3G_DATOS_BANDA 850') + row.get('3G_DATOS_BANDA 1900')
            result_by_tec[str_date]['2G_VOZ_GB'] = row.get('2G_VOZ_GB_BANDA 850') + row.get('2G_VOZ_GB_BANDA 1900')
            result_by_tec[str_date]['3G_VOZ_GB'] = row.get('3G_VOZ_GB_BANDA 850') + row.get('3G_VOZ_GB_BANDA 1900')
        return result_by_tec

    def event_handler(self, event):
        self.__guard(event)
        date_format = DTFORMAT_BY_ALIAS[event['msg_body']['format']]
        fecha = dt.datetime.strptime(event['msg_body']['fec_ini'], date_format)
        self.execute(fecha)

    def __guard(self, event):
        msg_body_keys = event['msg_body'].keys()
        if 'fec_ini' not in msg_body_keys or 'format' not in msg_body_keys:
            raise Exception("Error no se encontro el atributo fec_ini o format")

        if event['msg_body']['format'] not in list(DTFORMAT_BY_ALIAS):
            raise Exception(f"Formato '{event['msg_body']['format']}' no valido")


class RepMexicoGenerator:
    def __init__(self, db):
        self.db = db
        self.remote_path = "/opt/airflow/tareas/estadisticas/Reporte_Evolucion"
        self.months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Setiembre", "Octubre", "Noviembre", "Diciembre"]

    def execute(self, month: dt.datetime):
        filename = f"{self.remote_path}/Reporte_mensual_mexico_trafico_{month.strftime('%Y%m')}.xlsx"
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()

        header_pico_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1, 'valign': 'vcenter'})
        header_operador_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1, 'valign': 'vcenter', 'bg_color': '0A0664', 'font_color': 'white'})
        header_voz_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1, 'valign': 'vcenter', 'bg_color': 'F79646', 'font_color': 'white', 'text_wrap': True})
        header_datos_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1, 'valign': 'vcenter', 'bg_color': '8064A2', 'font_color': 'white', 'text_wrap': True})
        header_voz_pico_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1, 'valign': 'vcenter', 'bg_color': 'FFD966', 'font_color': 'white'})
        header_datos_pico_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1, 'valign': 'vcenter', 'bg_color': 'A8D08D', 'font_color': 'white'})
        body_format = workbook.add_format({'align': 'center', 'num_format': '#,##0', 'border': 1})
        body_porc_format = workbook.add_format({'border': 1, 'num_format': '0.00%', 'align': 'center'})

        reportes = ['RAN', 'CORE']
        kpi_drop = self.get_kpi_drop(month)
        data_by_reporte = self.get_data(month)
        data_pico_by_reporte = self.get_data_pico(month)

        for col_index in range(8):
            worksheet.set_column(col_index, col_index, 16)

        col_index = 0
        row_index = 0

        str_mes = self.months[month.month - 1]
        mes_anio = f"{str_mes[:3]}-{month.strftime('%Y')}"

        worksheet.merge_range(row_index, col_index, row_index, col_index+1, '2G GSM', header_datos_format)
        worksheet.merge_range(row_index+1, col_index, row_index+2, col_index, 'OPERADOR', header_operador_format)
        worksheet.write(row_index+1, col_index+1, 'INACCESIBILITY (%)', header_datos_format)
        worksheet.write(row_index+1, col_index+2, 'DROP CALLS (%)', header_datos_format)

        worksheet.write(row_index+2, col_index+1, mes_anio, header_datos_format)
        worksheet.write(row_index+2, col_index+2, mes_anio, header_datos_format)

        worksheet.write(row_index+3, col_index, 'Perú', body_format)
        if kpi_drop is not None:
            worksheet.write(row_index+3, col_index+1, kpi_drop['kpi_inaccesibility'], body_porc_format)
            worksheet.write(row_index+3, col_index+2, kpi_drop['kpi_drop'], body_porc_format)
        else:
            worksheet.write(row_index+3, col_index+1, None, body_format)
            worksheet.write(row_index+3, col_index+2, None, body_format)

        row_index += 7
        
        for str_reporte in reportes:
            row = data_by_reporte[str_reporte]
            mes_anio = f"{row['mes'][:3]}-{month.strftime('%Y')}"
            
            worksheet.merge_range(row_index, col_index, row_index+1, col_index, str_reporte, header_format)
            worksheet.merge_range(row_index+2, col_index, row_index+3, col_index, 'OPERADOR', header_operador_format)

            worksheet.merge_range(row_index, col_index+1, row_index+1, col_index+3, 'VOLUMEN VOZ ( Miles Erlangs)', header_voz_format)
            worksheet.merge_range(row_index, col_index+4, row_index+1, col_index+7, 'VOLUMEN DATOS (GB)', header_datos_format)

            self.write_rows(worksheet, row_index, col_index, row, mes_anio, {'header_voz_format': header_voz_format, 'header_datos_format': header_datos_format, 'body_format': body_format})
            row_index += 9

        worksheet.write(row_index-1, col_index, 'PICO', header_pico_format)
        for str_reporte in reportes:
            row = data_pico_by_reporte[str_reporte]
            mes_anio = f"{row['mes'][:3]}-{month.strftime('%Y')}"
            
            worksheet.merge_range(row_index, col_index, row_index+1, col_index, str_reporte, header_format)
            worksheet.merge_range(row_index+2, col_index, row_index+3, col_index, 'OPERADOR', header_operador_format)

            worksheet.merge_range(row_index, col_index+1, row_index+1, col_index+3, 'VOLUMEN VOZ (Erlangs) Acumulado HORA PICO del Mes', header_voz_pico_format)
            worksheet.merge_range(row_index, col_index+4, row_index+1, col_index+7, 'VOLUMEN DATOS (Gbytes) Acumulado HORA PICO del Mes', header_datos_pico_format)

            self.write_rows(worksheet, row_index, col_index, row, mes_anio, {'header_voz_format': header_voz_pico_format, 'header_datos_format': header_datos_pico_format, 'body_format': body_format})
            worksheet.write(row_index+2, col_index+3, '4G VOLTE', header_voz_pico_format)
            row_index += 9

        workbook.close()
        print(f"{filename} created")

    def write_rows(self, worksheet, row_index, col_index, row, mes_anio, formats):
        header_voz_format = formats['header_voz_format']
        header_datos_format = formats['header_datos_format']
        body_format = formats['body_format']

        worksheet.write(row_index+2, col_index+1, '2G GSM', header_voz_format)
        worksheet.write(row_index+2, col_index+2, '3G UMTS', header_voz_format)
        worksheet.write(row_index+2, col_index+3, '4G VoLTE (Solo Comercial)', header_voz_format)
        worksheet.write(row_index+2, col_index+4, '2G GSM', header_datos_format)
        worksheet.write(row_index+2, col_index+5, '3G UMTS', header_datos_format)
        worksheet.write(row_index+2, col_index+6, '4G LTE', header_datos_format)
        worksheet.write(row_index+2, col_index+7, '5G', header_datos_format)

        worksheet.write(row_index+3, col_index+1, mes_anio, header_voz_format)
        worksheet.write(row_index+3, col_index+2, mes_anio, header_voz_format)
        worksheet.write(row_index+3, col_index+3, mes_anio, header_voz_format)
        worksheet.write(row_index+3, col_index+4, mes_anio, header_datos_format)
        worksheet.write(row_index+3, col_index+5, mes_anio, header_datos_format)
        worksheet.write(row_index+3, col_index+6, mes_anio, header_datos_format)
        worksheet.write(row_index+3, col_index+7, mes_anio, header_datos_format)

        row_index += 4

        worksheet.write(row_index, col_index, 'Perú', body_format)
        worksheet.write_number(row_index, col_index+1, row.get('VOZ_2G'), body_format)
        worksheet.write_number(row_index, col_index+2, row.get('VOZ_3G'), body_format)
        worksheet.write_number(row_index, col_index+3, row.get('VOZ_4G'), body_format)

        worksheet.write_number(row_index, col_index+4, row.get('DATOS_2G'), body_format)
        worksheet.write_number(row_index, col_index+5, row.get('DATOS_3G'), body_format)
        worksheet.write_number(row_index, col_index+6, row.get('DATOS_4G'), body_format)
        worksheet.write_number(row_index, col_index+7, row.get('DATOS_5G'), body_format)

    def get_kpi_drop(self, month: dt.datetime):
        query = """select mes, kpi_inaccesibility, kpi_drop from kpi_ina_drop where mes = to_date(:p_month, 'yyyy-mm-dd')"""
        str_month = month.strftime('%Y-%m-')+'01'
        result = self.db.fetch(query, {'p_month': str_month})
        for row in result:
            return {'mes': row[0], 'kpi_inaccesibility': row[1], 'kpi_drop': row[2]}
        return None
        
    def get_data(self, month: dt.datetime):
        query = """select
        TO_CHAR(MES, 'YYYY-MM-DD') mes, reporte, tipo, TECNOLOGIA,
        CASE TIPO WHEN 'VOZ' THEN SUM(TRAFICO_ERL_MILES) ELSE SUM(TRAFICO_DATOS_GB) END trafico
        from rss_mensuales_fi_mex where mes = to_date(:p_month, 'yyyy-mm-dd')
        GROUP BY TO_CHAR(MES, 'YYYY-MM-DD'), reporte, tipo, TECNOLOGIA
        ORDER BY reporte, tipo, tecnologia"""

        str_month = month.strftime('%Y-%m-')+'01'
        result = self.db.fetch(query, {'p_month': str_month})
        result_by_tec = self.map_data_result(result)
        return result_by_tec

    def get_data_pico(self, month: dt.datetime):
        query = """select
        TO_CHAR(MES, 'YYYY-MM-DD') mes, reporte, tipo, TECNOLOGIA,
        CASE TIPO WHEN 'VOZ' THEN SUM(trafico_erl) ELSE SUM(trafico_gb) END trafico
        from rss_mexico_picos where mes = to_date(:p_month, 'yyyy-mm-dd')
        GROUP BY TO_CHAR(MES, 'YYYY-MM-DD'), reporte, tipo, TECNOLOGIA
        ORDER BY reporte, tipo, tecnologia"""

        str_month = month.strftime('%Y-%m-')+'01'
        result = self.db.fetch(query, {'p_month': str_month})
        result_by_tec = self.map_data_result(result)
        return result_by_tec

    def map_data_result(self, result):
        result_by_tec = {}
        for row in result:
            # key = f"{row[0]}_{row[1]}"
            key = f"{row[1]}"
            field_key = f"{row[2]}_{row[3]}"
            if result_by_tec.get(key) is None:
                result_by_tec[key] = {
                    'mes': self.months[dt.datetime.strptime(row[0], '%Y-%m-%d').month - 1],
                    'reporte': row[1],
                    field_key: row[4]
                }
            else:
                result_by_tec[key][field_key] = row[4]
        return result_by_tec

    def event_handler(self, event):
        self.__guard(event)
        date_format = DTFORMAT_BY_ALIAS[event['msg_body']['format']]
        fecha = dt.datetime.strptime(event['msg_body']['fec_ini'], date_format)
        self.execute(fecha)

    def __guard(self, event):
        msg_body_keys = event['msg_body'].keys()
        if 'fec_ini' not in msg_body_keys or 'format' not in msg_body_keys:
            raise Exception("Error no se encontro el atributo fec_ini o format")

        if event['msg_body']['format'] not in list(DTFORMAT_BY_ALIAS):
            raise Exception(f"Formato '{event['msg_body']['format']}' no valido")


class AnaHandlerEventConsumer(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.1
        self.loop = False
        self.pronatel_configs = {}

        self.queue_handlers["ana.reporte_evolucion.send_file"] = {'handler': REPORTE_EVOLUCION_GENERATOR, 'callback': lambda s, e: s.event_handler(e)}
        self.queue_handlers["ana.trafico_3g2g.send_file"] = {'handler': TRAFICO_3G_2G_GENERATOR, 'callback': lambda s, e: s.event_handler(e)}
        self.queue_handlers["ana.rep_maggie.send_file"] = {'handler': REP_MAGGIE_GENERATOR, 'callback': lambda s, e: s.event_handler(e)}
        self.queue_handlers["ana.rep_bandas.send_file"] = {'handler': REP_BANDAS_GENERATOR, 'callback': lambda s, e: s.event_handler(e)}
        self.queue_handlers["ana.rep_mexico.send_file"] = {'handler': REP_MEXICO_GENERATOR, 'callback': lambda s, e: s.event_handler(e)}

        self.queue_ids = list(self.queue_handlers)
