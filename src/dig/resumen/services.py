import datetime as dt

class DigCgnatResumenConsumer:
    def __init__(self, ch_db, queue_service, control_repo):
        self.ch_db = ch_db
        self.queue_service = queue_service
        self.control_repo = control_repo
        self.queue_id = "dig.resumen_ch"
        self.max_number_of_messages = 100

    def execute(self):
        print(f"{self.queue_id}")
        print("max_number_of_messages", self.max_number_of_messages)
        reload_maestro = False

        # while True:
        events = self.queue_service.receive_message(self.queue_id, self.max_number_of_messages)
        if len(events) == 0:
            print(f"no hay mas eventos a procesar")
            return 1

        print(f"procesando {len(events)} eventos")
        
        for row in events:
            fecha_ini = dt.datetime.now()
            event_error = None
            try:
                self.consume_event(row['msg_body'])
            except BaseException as error:
                event_error = error
            
            fecha_fin = dt.datetime.now()
            event_result = {
                'id': row['id'],
                'estado': 1 if event_error is None else -1,
                'message': str(event_error) if event_error is not None else None,
                'fecha_ini_exec': fecha_ini.strftime('%d/%m/%Y %H:%M:%S'),
                'fecha_fin_exec': fecha_fin.strftime('%d/%m/%Y %H:%M:%S'),
            }
            self.queue_service.updateResultOfEvent(event_result)

            proyect_name = row['msg_body'].get('proyect_name')
            # server_name = event_message.get('server_name')
            filename = row['msg_body'].get('filename')
            str_fecha = row['msg_body'].get('fec_ini')
            dt_fecha = dt.datetime.strptime(str_fecha, '%Y-%m-%d %H:%M')

            self.control_repo.save_carga(
                f"{proyect_name}.ok",
                filename,
                1,
                1,
                fecha_ini,
                fecha_fin,
                'CARGADO' if event_error is None else 'ERROR',
                str(event_error) if event_error is not None else None,
                dt_fecha
            )
            if event_error is None:
                print(f"archivo {filename} procesado correctamente")
            else:
                print(f"archivo {filename} procesado con error:", str(event_error))
    def consume_event(self, event_message):
        server_name = event_message.get('server_name')
        str_fecha = event_message.get('fec_ini')
        dt_fecha = dt.datetime.strptime(str_fecha, '%Y-%m-%d %H:%M')
        str_month = dt_fecha.strftime('%Y%m')

        str_query = f"""insert into dr_transporte_kpi.rss_tx_medicion_dig(
        fecha, ip_address, tipo_ip, dominio, dns, query_time_1, query_time_2, query_time_3, servidor
        )
        SELECT
        fecha, ip_address, tipo_ip, dominio, dns, query_time_1, query_time_2, query_time_3, servidor
        from dr_transporte_kpi.TX_MEDICION_DIG_{str_month}
        where fecha = toDateTime({{fecha:String}}) and servidor = upper({{server_name:String}})
        and (servidor, fecha, ip_address) not in (
            select servidor, fecha, ip_address from dr_transporte_kpi.rss_tx_medicion_dig
            where fecha >= now() - interval '7' day and servidor = upper({{server_name2:String}})
            group by servidor, fecha, ip_address
        )
        """
        self.ch_db.query(str_query, {'fecha': dt_fecha.strftime('%Y-%m-%d %H:%M:%S'), 'server_name': server_name, 'server_name2': server_name})