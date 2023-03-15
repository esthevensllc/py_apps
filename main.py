import sys
import datetime
import calendar
from src.shared.app.AppContainer import AppContainer
# from src.shared.database.MysqlDB import MysqlDB
# from src.shared.database.OracleDB import OracleDB

service_to_exec = sys.argv[1]

start_time = datetime.datetime.now()

app_container = AppContainer()
# databases
mysql_db = app_container.getInstance('dbmysql')
oracle_db = app_container.getInstance('dboracle')

if service_to_exec == 'load_PM_IG7511_from_oracle_diario':
    from src.PM_IG7511.services.Load_PM_IG7511_from_oracle import Load_PM_IG7511_from_oracle
    from src.PM_IG7511.services.LoadResumenDetalle_PM_IG7511 import LoadResumenDetalle_PM_IG7511

    mysql_db.useConnection('U2000')
    service = Load_PM_IG7511_from_oracle(mysql_db, oracle_db)
    load_resumen_service = LoadResumenDetalle_PM_IG7511(oracle_db)

    # ejecucion cada dia a los 10 min de las 5am
    # carga dia anterior
    
    # fecha_ini = datetime.datetime.strptime('02/01/2022', '%d/%m/%Y')
    # fecha_fin = datetime.datetime.strptime('03/01/2022', '%d/%m/%Y')
    fecha_ini = datetime.datetime.now() - datetime.timedelta(days=1)
    fecha_fin = fecha_ini + datetime.timedelta(days=1)

    service.execute(fecha_ini, fecha_fin)

    days_of_month = calendar.monthrange(int(fecha_fin.strftime('%Y')), int(fecha_fin.strftime('%m')))[1]
    fecha_fin = fecha_fin + datetime.timedelta(days=days_of_month)

    load_resumen_service.execute(fecha_ini, fecha_fin)
elif service_to_exec == 'load_ubicacion_usuarios':
    import src.PSO_19.PSO_19_6748.services.load_ubicacion_usuarios.load_ubicacion_usuarios
    from src.PSO_19.PSO_19_6748.repository import PSO_19_6748_Repository
    repository = PSO_19_6748_Repository(oracle_db)
    service = load_ubicacion_usuarios(repository)
    service.execute()
elif service_to_exec == 'create_geojson_planos_duplicados':
    from src.PSO_19.PSO_19_6748.services.create_geojson_planos_duplicados import create_geojson_planos_duplicados
    from src.PSO_19.PSO_19_6748.repository import PSO_19_6748_Repository
    repository = PSO_19_6748_Repository(oracle_db)
    service = create_geojson_planos_duplicados(repository)
    service.execute()
elif service_to_exec == 'load_alarmas_u2000':
    from src.U2000.alarmas.services.U2000AlarmasAppProvider import (LOAD_ALARMAS_U2000)
    service = app_container.getInstance(LOAD_ALARMAS_U2000)
    fecha = datetime.datetime.strptime('13/01/2022 00:05', '%d/%m/%Y %H:%M')
    service.execute(fecha)
elif service_to_exec == 'load_alarmas_u2000_consumer':
    from src.U2000.alarmas.services.U2000AlarmasAppProvider import (ALARMAS_U2000_COMSUMER)
    service = app_container.getInstance(ALARMAS_U2000_COMSUMER)
    # fecha = datetime.datetime.strptime('13/01/2022 00:05', '%d/%m/%Y %H:%M')
    service.execute()
elif service_to_exec == 'load_u2000_cpu_occ_prof_consumer':
    from src.U2000.cpu_occ_profile.services.U2000CPU_OCC_ProfileAppProvider import (CPU_OCC_PROF_CONSUMER)
    service = app_container.getInstance(CPU_OCC_PROF_CONSUMER)
    service.execute()
elif service_to_exec == 'load_u2000_mem_occ_prof_consumer':
    from src.U2000.mem_occ_profile.services.U2000MEM_OCC_ProfileAppProvider import (MEM_OCC_PROF_CONSUMER)
    service = app_container.getInstance(MEM_OCC_PROF_CONSUMER)
    service.execute()
elif service_to_exec == 'load_u2000_slot_temp_prof_consumer':
    from src.U2000.slot_temp_profile.services.U2000SlotTempProfileAppProvider import (SLOT_TEMP_PROF_CONSUMER)
    service = app_container.getInstance(SLOT_TEMP_PROF_CONSUMER)
    service.execute()
elif service_to_exec == 'load_u2000_board_report_consumer':
    from src.U2000.board_report.services.U2000BoardReportAppProvider import (BOARD_REPORT_CONSUMER)
    service = app_container.getInstance(BOARD_REPORT_CONSUMER)
    service.execute()
elif service_to_exec == 'load_u2000_subrack_report_consumer':
    from src.U2000.subrack_report.services.U2000SubrackReportAppProvider import SUBRACK_REPORT_CONSUMER
    service = app_container.getInstance(SUBRACK_REPORT_CONSUMER)
    service.execute()
elif service_to_exec == 'load_u2000_ne_report_consumer':
    from src.U2000.ne_report.services.U2000NeReportAppProvider import NE_REPORT_CONSUMER
    service = app_container.getInstance(NE_REPORT_CONSUMER)
    service.execute()
elif service_to_exec == 'app_async_event_consumer':
    service = app_container.getInstance('async_event_consumer')
    service.execute()
elif service_to_exec == 'test':
    import time
    from concurrent.futures import ThreadPoolExecutor
    from src.U2000.alarmas.services.U2000AlarmasAppProvider import ALARMAS_U2000_PRODUCER
    from src.U2000.cpu_occ_profile.services.U2000CPU_OCC_ProfileAppProvider import CPU_OCC_PROF_PRODUCER
    from src.U2000.mem_occ_profile.services.U2000MEM_OCC_ProfileAppProvider import MEM_OCC_PROF_PRODUCER
    from src.U2000.slot_temp_profile.services.U2000SlotTempProfileAppProvider import SLOT_TEMP_PROF_PRODUCER
    from src.U2000.board_report.services.U2000BoardReportAppProvider import BOARD_REPORT_PRODUCER
    from src.U2000.subrack_report.services.U2000SubrackReportAppProvider import SUBRACK_REPORT_PRODUCER
    from src.U2000.ne_report.services.U2000NeReportAppProvider import NE_REPORT_PRODUCER

    executor = ThreadPoolExecutor(max_workers=7)
    service1 = app_container.getInstance(ALARMAS_U2000_PRODUCER)
    service2 = app_container.getInstance(CPU_OCC_PROF_PRODUCER)
    service3 = app_container.getInstance(MEM_OCC_PROF_PRODUCER)
    service4 = app_container.getInstance(SLOT_TEMP_PROF_PRODUCER)
    service5 = app_container.getInstance(BOARD_REPORT_PRODUCER)
    service6 = app_container.getInstance(SUBRACK_REPORT_PRODUCER)
    service7 = app_container.getInstance(NE_REPORT_PRODUCER)

    # executor.submit(service1.execute)
    # time.sleep(1)
    # executor.submit(service2.execute)
    # time.sleep(1)
    # executor.submit(service3.execute)
    # time.sleep(1)
    # executor.submit(service4.execute)
    # time.sleep(1)
    # executor.submit(service5.execute)
    # time.sleep(1)
    # executor.submit(service6.execute)
    # time.sleep(1)
    service7.execute()

    # service1.execute()
    # from src.U2000.alarmas.services.U2000AlarmasEventProducer import U2000AlarmasEventProducer
    # remote_connect = app_container.getInstance('remote_connect')
    # control_carga_repo = app_container.getInstance('control_carga_repo')
    # remote_connect.useConnection('default')
    # service = U2000AlarmasEventProducer(queue_service, remote_connect, control_carga_repo)
    # resp = service.exec_command("ls /opt/oss/server/var/neftpboot/ftproot -lt")
    # resp = remote_connect.exec_command("ls /opt/oss/server/var/neftpboot/ftproot -lt --time-style=long-iso | grep Board | awk '{print $6\"_\" $7, $8}'")
    # archivos = []
    # for index in range(len(resp)):
    #     archivos.append({'updated': resp[index][0:16], 'file': resp[index][17:len(resp[index])]})
    # print(archivos)
else:
    try:
        def get_params():
            args = sys.argv.copy()
            if len(args) > 2:
                return args[2:len(args)]
            return []

        extra_params = get_params()

        service = app_container.getInstance(service_to_exec)
        service.execute(*extra_params)
    except BaseException as error:
        import traceback
        notification_service = app_container.getInstance('notification_service')
        subject = f"Error en la ejecucion de {service_to_exec}"
        message = f"Se presento el siguiente problema: {error}\n" + traceback.format_exc()
        if len(message) > 4000:
            message = message[0:4000]
        notification_service.send_notification(subject, message, 'ALARMA_CARGAS')
        raise error

# oracle_db.__disconnect__()

app_container.close_connections()

end_time = datetime.datetime.now()
print("Fecha (inicio - fin) ejecucion ({} - {})".format(start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S')))