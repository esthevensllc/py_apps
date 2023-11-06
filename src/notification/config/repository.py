from src.shared.carga.repository import InMemoryConfigRepository

class InMemoryNotificationConfigRepository(InMemoryConfigRepository):
    def __init__(self, db):
        self.db = db
        self.config_by_id = {
            "1": {
                "id": "1",
                "name": "Timeout de Encolamiento",
                "type_id": "db",
                "query": """SELECT QUEUE_ID, MIN(FECHA_REGISTRO), COUNT(*) FROM PADM_QUEUE_EVENTS A
                INNER JOIN PADM_QUEUE_CONFIG B ON B.ID = A.QUEUE_ID
                WHERE a.ESTADO=0 AND FECHA_REGISTRO < SYSDATE - nvl(b.timeout_min, 5)/(24*60)
                GROUP BY QUEUE_ID""",
                "range_minutes": 60,
                "asunto": "Notificación Procesos - Timeout de Encolamiento",
                "group_id": "ALARMA_CARGAS",
                "template": """<table border="1" cellspacing="0" cellpadding="0">
                <thead>
                <tr>
                    <th>QUEUE_ID</th>
                    <th>FECHA_REGISTRO_MIN</th>
                    <th>COUNT</th>
                </tr>
                </thead>
                <tbody>
                {% for row in data %}
                    <tr>
                    <td>{{ row[0] }}</td>
                    <td>{{ row[1] }}</td>
                    <td>{{ row[2] }}</td>
                    </tr>
                {% endfor %}
                </tbody>
                </table>""",
                "fields": []
            },
            "2": {
                "id": "2",
                "name": "Health Check Airflow",
                "type_id": "fetch",
                "api": "http://172.19.245.139:8080/health",
                "rules": "{% if data.metadatabase.status != 'healthy' or data.scheduler.status != 'healthy' %}true{% endif %}",
                "range_minutes": 30,
                "asunto": "Notificación Procesos - Health Airflow",
                "group_id": "ALARMA_CARGAS",
                "template": "Hay un problema con la plataforma airflow por favor revisar",
                "fields": [],
            },
            "3": {
                "id": "3",
                "name": "SoporteClientes Diario",
                "type_id": "db",
                "query": """
                select
                to_char(a.fecha, 'yyyy-mm-dd') fecha,
                b.id proyecto,
                to_char(c.fecha_archivo, 'yyyy-mm-dd') fecha_archivo,
                case when c.id is null then 'NO EXISTE' else 'CON ERROR' end estado
                from (
                    select
                    trunc(fecha , 'dd') fecha
                    from tiempo
                    where trunc(sysdate - 15, 'dd') <= fecha and fecha < trunc(sysdate -1, 'dd')
                    group by trunc(fecha , 'dd')
                ) a
                inner join (
                    select * from padm_queue_config
                    where group_id = 'soportecli_diario'
                ) b
                on 1=1
                left join padm_carga_control c
                on c.proyecto = b.id and c.fecha_archivo = a.fecha
                where c.id is null or c.estado != 'CARGADO'
                ORDER BY b.id, a.fecha desc""",
                "range_minutes": 60*24,
                "asunto": "Notificación Procesos - SoporteClientes Diario",
                "group_id": "ALARMA_CARGAS",
                "template": """<p style='margin-top: 0px;'>Archivos no cargados en los ultimos 15 días</p>
                <table border="1" cellspacing="0" cellpadding="0">
                <thead>
                <tr>
                    <th>FECHA</th>
                    <th>PROYECTO</th>
                    <th>FECHA_ARCHIVO</th>
                    <th>ESTADO</th>
                </tr>
                </thead>
                <tbody>
                {% for row in data %}
                    <tr>
                        <td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td>
                    </tr>
                {% endfor %}
                </tbody>
                </table>""",
                "fields": []
            },
            "4": {
                "id": "4",
                "name": "SoporteClientes Semanal",
                "type_id": "db",
                "query": """select
                to_char(a.fecha, 'yyyy-mm-dd') fecha,
                b.id proyecto,
                to_char(c.fecha_archivo, 'yyyy-mm-dd') fecha_archivo,
                case when c.id is null then 'NO EXISTE' else 'CON ERROR' end estado
                from (
                    select
                    trunc(fecha , 'ww') fecha, min(fecha), max(fecha)
                    from tiempo
                    where trunc(sysdate - 30, 'dd') <= fecha and fecha < trunc(sysdate - 2, 'dd')
                    group by trunc(fecha , 'ww')
                ) a
                inner join (
                    select * from padm_queue_config
                    where group_id = 'soportecli_semanal'
                ) b
                on 1=1
                left join padm_carga_control c
                on c.proyecto = b.id and trunc(c.fecha_archivo, 'ww') = a.fecha
                where c.id is null or c.estado != 'CARGADO'""",
                "range_minutes": 60*24*3,
                "asunto": "Notificación Procesos - SoporteClientes Semanal",
                "group_id": "ALARMA_CARGAS",
                "template": """<p style='margin-top: 0px;'>Archivos no cargados en los ultimos 30 días</p>
                <table border="1" cellspacing="0" cellpadding="0">
                <thead>
                <tr>
                    <th>FECHA</th>
                    <th>PROYECTO</th>
                    <th>FECHA_ARCHIVO</th>
                    <th>ESTADO</th>
                </tr>
                </thead>
                <tbody>
                {% for row in data %}
                    <tr>
                        <td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td>
                    </tr>
                {% endfor %}
                </tbody>
                </table>""",
                "fields": []
            },
        }