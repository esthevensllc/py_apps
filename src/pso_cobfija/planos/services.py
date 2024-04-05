import requests
import json
import cx_Oracle
from src.shared.config import (STORAGE_DIR)
from src.shared.queue.SimpleEventConsumer import SimpleEventConsumer
from src.pso_cobfija.shared.services import (CREATE_GEOJSON_FROMDB)

class LoadgeojsonPlanos:
    def __init__(self, repository):
        self.repository = repository
        # self.geojson_url="http://172.17.27.157/portalmonitoreo/assets/map/map_19_6748.json"
        self.geojson_path = f"{STORAGE_DIR}pso_cobfija/map_19_6748.json"

    def execute(self):
        #geojson = requests.get(self.geojson_url)
        #geojson = geojson.json()
        #geojson_features = geojson['features']
        print(f"Cargando planos")
        duplicados = {}
        try:
            file = open(self.geojson_path, 'r', encoding="utf-8")
            geojson = json.loads(file.read())
            file.close()
            geojson_features = geojson['features']
            planos = []
            # carga planos en array
            for index in range(len(geojson_features)):
                plano_to_add = {}
                for propIndex in geojson_features[index]['properties']:
                    plano_to_add[propIndex.lower()] = geojson_features[index]['properties'][propIndex]
                if 'geometry' not in geojson_features[index].keys():
                    print(geojson_features[index])
                    plano_to_add['geometry'] = None
                else:
                    plano_to_add['geometry'] = json.dumps(geojson_features[index]['geometry'])
                planos.append(plano_to_add)

                if duplicados.get(plano_to_add['nombre']) is None:
                    duplicados[plano_to_add['nombre']] = 0
                duplicados[plano_to_add['nombre']] += 1
            
            self.repository.delete_all()
            self.repository.insert_from_array(planos)

            self.repository.delete_all_backup()
            self.repository.insert_backup()
            print(f"planos cargados: {len(planos)}")

            # genera geojson duplicados
            duplicados = list(filter(lambda name: duplicados[name] > 1, list(duplicados)))
            print(f"duplicados: {len(duplicados)}")
            geojson['features'] = list(filter(lambda index: index['properties']['Nombre'] in duplicados, geojson_features))
            file = open(self.geojson_path.replace('.json', '_duplicados.json'), 'w')
            file.write(json.dumps(geojson))
            file.close()
        except BaseException as e:
            self.repository.delete_all()
            self.repository.insert_from_backup()
            print(f"planos cargados desde backup")
            raise e

        self.repository.exec_procedure('PSO_INSERTBASE_19.SP_PLANOS_MAESTRO')
        import src.pso_cobfija.planos.extra.load_ubigeos_faltantes
        self.repository.exec_procedure('PSO_INSERTBASE_19.SP_PLANOS_MAESTRO_ADD_UBIGEO_DATA')


class CreateGeojsonFromDB:
    def __init__(self, db, sftp_service):
        self.db = db
        self.sftp_service = sftp_service
        self.geojson_path = f"{STORAGE_DIR}pso_cobfija/map_19_6748.json"
        self.web_path = f"/var/www/html"

    def execute(self):
        print("create-geojson-fromdb")
        self.db.query("alter session set NLS_NUMERIC_CHARACTERS = '.,'")
        geojson = {"type": "FeatureCollection", "features": []}
        planos = self._get_planos()
        counter = 0
        for row in planos:
            counter=counter+1
            try:
                centroide = json.loads(row[3].read()) if row[3] is not None else None
                centroide_longitud = None
                centroide_latitud = None
                if centroide is not None:
                    centroide_longitud = centroide["coordinates"][0]
                    centroide_latitud = centroide["coordinates"][1]
                feature = {
                    "type": "Feature",
                    "properties": {"ID": row[0], "NOMBRE": row[1], "centroide_longitud": centroide_longitud, "centroide_latitud": centroide_latitud, "departamento": row[4], "provincia": row[5], "distrito": row[6], "tecnologia": row[7], "overlap": row[8]},
                    "geometry": json.loads(row[2].read())
                }
                geojson["features"].append(feature)
            except:
                print(f"[{counter}] id:{row[0]}, nombre: {row[1]}")
                raise Exception("Ocurrio un erro al formatear el geojson")
        
        file = open(self.geojson_path, 'w')
        file.write(json.dumps(geojson))
        file.close()

        print(f"planos: {len(planos)}")
        
        print("copy geojson to web server")
        self.sftp_service.useConnection("portales")
        self.sftp_service.connect()
        
        sftp = self.sftp_service.getReference()
        sftp.put(self.geojson_path, f"{self.web_path}/portalmonitoreov2/public/map/map_19_6748.json")
        sftp.put(self.geojson_path, f"{self.web_path}/portalmonitoreov1/assets/map/map_19_6748.json")
        sftp.put(self.geojson_path, f"{self.web_path}/portalmonitoreo/assets/map/map_19_6748.json")
    
    def _get_planos(self):
        cur = self.db.connection.cursor()
        params = [cur.var(cx_Oracle.CURSOR)]
        cur.callproc("PSO_INSERTBASE_19.SP_GET_PLANOS_GEOMETRY", params)
        cursor = params[0].getvalue()
        result = []
        for row in cursor:
            result.append(row)
        return result

    def event_handler(self, event):
        self.execute()


class GeojsonConsumer(SimpleEventConsumer):
    def __init__(self, queue_service, app_container, notification_service):
        super().__init__(queue_service, app_container, notification_service)
        self.sleep_time_in_work = 0.1
        self.loop = False

        self.queue_handlers["pso.create_geojson_fija"] = {
            'handler': CREATE_GEOJSON_FROMDB,
            'callback': lambda s, e: s.event_handler(e)
        }

        self.queue_ids = list(self.queue_handlers)
