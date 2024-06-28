import os
import sys
import datetime
import calendar
from dotenv import load_dotenv
load_dotenv()
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

    try:
        mysql_db.useConnection('U2000')
        mysql_db.fetch("select now()")
    except:
        mysql_db.useConnection('U2000_standby')
        print("Carga desde base de datos en espera")
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
        if os.getenv("APP_ENV", "prod") == "prod":
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