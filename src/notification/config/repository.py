from src.shared.carga.repository import InMemoryConfigRepository

class InMemoryNotificationConfigRepository(InMemoryConfigRepository):
    def __init__(self, db):
        self.db = db
        self.config_by_id = {
            "1": {
                "id": "1",
                "name": "Timeout de Encolamiento",
                "type_id": "db",
                "query": "SELECT QUEUE_ID, MIN(FECHA_REGISTRO), COUNT(*) FROM PADM_QUEUE_EVENTS WHERE ESTADO=0 AND FECHA_REGISTRO < SYSDATE - INTERVAL '1' HOUR GROUP BY QUEUE_ID",
                "range_minutes": 60,
                "asunto": "Notificación Procesos - Timeout de Encolamiento",
                "group_id": "ALARMA_CARGAS",
                "template": """<table>
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
                    <td>{{ row[1] }}</td>
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
            }
        }