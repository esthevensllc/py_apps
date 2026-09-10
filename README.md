# Py Apps

Repositorio común de procesos Python e integraciones programadas mediante
Apache Airflow. Cada proyecto se encuentra dentro de `src/` y los DAG que lo
ejecutan se mantienen en `dags/`.

## Estructura general

```text
py_apps/
├── dags/             # DAG registrados por Airflow
├── files/            # Archivos temporales y de trabajo
├── shell/            # Utilidades de sistema
├── sql/              # Scripts DDL y consultas de despliegue
├── src/              # Proyectos Python
├── tests/            # Pruebas disponibles por proyecto
├── .env              # Configuración real, no versionada
├── .env.example      # Plantilla común de configuración
├── main.py           # Ejecutor general heredado
└── main_unique.py    # Ejecutor de cargas que requieren instancia única
```

El directorio utilizado actualmente en el servidor Airflow es:

```text
/opt/airflow/tareas/py_apps
```

Toda la configuración de los proyectos se centraliza en un único archivo
`.env` en la raíz. No se deben crear archivos `.env` dentro de `src/`.

## Proyectos

| Proyecto | Descripción breve | Documentación |
|---|---|---|
| `alertas_elog` | Réplica de alertas y métricas CGNAT desde ClickHouse hacia Oracle Smart. | Pendiente de separar |
| `ana` | Procesos e integraciones identificados como ANA. | Pendiente |
| `apic` | Recolección e integración de información Cisco APIC. | Pendiente |
| `arbor_os` | Procesamiento de información proveniente de Arbor. | Pendiente |
| `cdr` | Procesamiento de registros CDR. | Pendiente |
| `clickhouse` | Servicios compartidos de carga y réplica para ClickHouse. | Pendiente |
| `cmd_huawei` | Ejecución y procesamiento de comandos Huawei. | Pendiente |
| `control_carga` | Control, resumen y seguimiento de procesos de carga. | Pendiente |
| `densidad_sites` | Procesamiento de indicadores de densidad de sitios. | Pendiente |
| `dig` | Procesamiento de consultas y resultados DNS mediante dig. | Pendiente |
| `factibilidad_fija` | Procesos asociados a factibilidad de red fija. | Pendiente |
| `fping` | Procesamiento de mediciones y resultados de fping. | Pendiente |
| `gde` | Integraciones y cargas asociadas a GDE. | Pendiente |
| `gmyd` | Procesos de datos identificados como GMYD. | Pendiente |
| `ips_spam` | Carga vigente de listas UCEPROTECT hacia ClickHouse para detección de IPs Spam. | [Ver README](src/ips_spam/README.md) |
| `ipt` | Procesos e integraciones identificados como IPT. | Pendiente |
| `mariadb` | Extracción y carga de información desde MariaDB. | Pendiente |
| `med_huawei2` | Procesamiento de mediciones Huawei. | Pendiente |
| `mmltask` | Automatización y procesamiento de tareas MML. | Pendiente |
| `nce` | Carga periódica de archivos y métricas provenientes de Huawei NCE. | Pendiente de separar |
| `nce_recarga` | Recarga histórica manual de archivos NCE mediante SFTP. | Pendiente de separar |
| `neteco` | Integraciones con la plataforma Huawei NetEco. | Pendiente |
| `nfa` | Procesos e integraciones identificados como NFA. | Pendiente |
| `notification` | Servicios comunes para envío de notificaciones. | Pendiente |
| `osiptel` | Procesamiento de información y reportes relacionados con OSIPTEL. | Pendiente |
| `pm` | Procesamiento por lotes de archivos de performance management. | Pendiente |
| `PM_IG7511` | Carga específica de mediciones PM IG7511. | Pendiente |
| `pronatel` | Procesos de carga y mantenimiento asociados a Pronatel. | Pendiente |
| `prtltx` | Procesos e integraciones identificados como PRTLTX. | Pendiente |
| `PSO_19` | Procesamiento específico del flujo PSO 19. | Pendiente |
| `pso_cobfija` | Procesos PSO para cobertura fija. | Pendiente |
| `san` | Integraciones con almacenamiento o servicios SAN. | Pendiente |
| `shared` | Código común de configuración, bases de datos y utilidades. | Interno |
| `speedtest` | Procesamiento de mediciones de velocidad. | Pendiente |
| `syslog` | Recepción y procesamiento de registros syslog. | Pendiente |
| `traceroute` | Procesamiento de mediciones traceroute. | Pendiente |
| `U2000` | Integraciones con la plataforma Huawei U2000. | Pendiente |
| `webacs` | Integraciones con Cisco Prime/WebACS. | Pendiente |
| `weplan_analytics` | Procesamiento de información de WePlan Analytics. | Pendiente |
| `zte` | Procesamiento de archivos y métricas de equipos ZTE. | Pendiente |

Las descripciones pendientes se completarán progresivamente en un `README.md`
dentro de la carpeta de cada proyecto.

## Convención de ejecución

Los proyectos nuevos deben poder ejecutarse como módulo Python:

```bash
python -m src.<proyecto>
```

Cada proceso programado debe tener su DAG correspondiente dentro de `dags/`.
El DAG debe establecer como directorio de trabajo la raíz desplegada de
`py_apps`, para que Python pueda resolver el paquete `src`.

## Configuración

La plantilla de variables se encuentra en `.env.example`. Para una instalación
nueva:

```bash
cp .env.example .env
```

Después se deben completar únicamente las credenciales y rutas aplicables al
servidor. El archivo `.env` real no se publica en Git.

## Despliegue general

Actualizar el repositorio en el servidor:

```bash
cd /opt/airflow/tareas/py_apps
git pull origin main
```

Luego se deben seguir las instrucciones del `README.md` perteneciente al
proyecto que se va a instalar. Los DAG deben ser visibles desde el directorio
configurado en Airflow.

## Documentación

La documentación detallada debe mantenerse junto al código correspondiente:

```text
src/<proyecto>/README.md
```

El README raíz funciona únicamente como presentación, inventario e índice del
repositorio.
