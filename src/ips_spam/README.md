# IPs Spam: UCEPROTECT hacia ClickHouse

Este proyecto mantiene en ClickHouse la información vigente de UCEPROTECT para
la detección de IPs Spam. Se ejecuta directamente como módulo Python o mediante
el DAG `ips_spam_uceprotect`.

## Componentes

```text
src/ips_spam/
├── __main__.py       # Entrada para python -m src.ips_spam
├── cli.py            # Argumentos y configuración
├── extractors.py     # Descarga rsync, descarga HTML y parsers
├── models.py         # Modelos de datos y métricas
├── repositories.py  # Sincronización y auditoría en ClickHouse
├── service.py        # Orquestación de las fuentes
├── .env.example      # Plantilla de configuración del proyecto
├── .env              # Configuración real, no versionada
├── bridge.py         # Recolección validada desde el servidor puente
├── ops/              # Script y unidades systemd para el servidor puente
├── RUNBOOK_DESCARGA_MANUAL.md # Operación del puente y alternativa manual
└── README.md         # Esta documentación
```

Archivos relacionados fuera de la carpeta:

- DAG: `dags/ips_spam_uceprotect.py`
- DDL: `sql/create_ips_spam.sql`
- Configuración: `src/ips_spam/.env`

El servidor `192.168.195.247` descarga y publica diariamente una instantánea
local. Airflow en `10.96.167.139` la recoge por SFTP y ejecuta el mismo
cargador ClickHouse con `--skip-download`. El
[`RUNBOOK_DESCARGA_MANUAL.md`](RUNBOOK_DESCARGA_MANUAL.md) contiene el
procedimiento de instalación y una alternativa de transferencia manual.

## Fuentes y tablas

| Fuente | Extracción | Tabla ClickHouse |
|---|---|---|
| UCEPROTECT Level 1 | rsync `dnsbl-1.uceprotect.net` | `spam.UCEPRTC_LVL1` |
| UCEPROTECT Level 2 | rsync `dnsbl-2.uceprotect.net` | `spam.UCEPRTC_LVL2` |
| UCEPROTECT Level 3 | rsync `dnsbl-3.uceprotect.net` | `spam.UCEPRTC_LVL3` |
| Backscatter | rsync `ips.backscatterer.org` | `spam.UCEPRTC_LST_BCK` |
| Whitelist | rsync `ips.whitelisted.org` | `spam.UCEPRCT_LST_WHT` |
| Level 3 Charts | HTTPS `l3charts.php` | `spam.UCEPRTC_ASN` |

Se conserva el nombre solicitado `UCEPRCT_LST_WHT`, aunque su prefijo no
coincide con `UCEPRTC` utilizado por las demás tablas.

Las cinco listas rsync almacenan `VALOR`, `FECHA_INSERCION` y
`FECHA_MODIFICACION`. La tabla ASN almacena:

- `POSICION`
- `TENDENCIA`: `UP`, `DOWN`, `SAME` o `UNKNOWN`
- `SPAM_SCORE`
- `IMPACTOS`
- `PROVEEDOR`
- `ASN`
- `FECHA_INSERCION`
- `FECHA_MODIFICACION`

## Funcionamiento

La primera descarga puede forzarse con `--full-download`. En las ejecuciones
siguientes rsync transfiere únicamente las diferencias, pero el contenido
recibido se procesa como una fotografía completa de la información vigente.

Cada tabla posee dos tablas técnicas:

- `__INCOMING`: recibe el contenido extraído.
- `__NEXT`: construye la siguiente versión conservando las fechas originales
  de los registros sin cambios.

La versión nueva se publica con `ALTER TABLE ... REPLACE PARTITION ID 'all'`
desde `__NEXT`, solamente después de descargar, interpretar y cargar
correctamente la fuente. Las tablas `MergeTree` de este proyecto no tienen
partición explícita, por lo que sus datos pertenecen a `all`. El reemplazo es
atómico y funciona aunque la base `spam` existente tenga motor `Ordinary`.
Esto permite:

- Ignorar repetidos.
- Insertar registros nuevos.
- Actualizar cambios de posición, tendencia, score, impactos o proveedor ASN.
- Eliminar registros ausentes en la nueva fuente.
- Evitar reemplazar una tabla vigente con una descarga vacía o inválida.

En las listas de una sola columna, un cambio de valor se representa como la
eliminación del valor anterior y la inserción del nuevo. No se conserva histórico.

Las fuentes se publican de forma independiente. Si una fuente falla después de
que otra terminó, las ya publicadas permanecen vigentes y la fallida conserva su
versión anterior.

## Requisitos

- Python 3.10 o superior.
- Paquetes `clickhouse-connect` y `python-dotenv`, ya utilizados por el proyecto.
- En `192.168.195.247`: `rsync` y `curl`, con salida a las fuentes UCEPROTECT.
- En workers Airflow de `10.96.167.139`: paquete Python `paramiko`, utilizado
  también por los otros proyectos con puente SFTP.
- Acceso SSH/TCP 22 de `10.96.167.139` a `192.168.195.247` con un usuario y
  contraseña autorizados para lectura.
- Acceso HTTP de ClickHouse desde Airflow hacia `172.19.242.107:8123`.
- Permiso `ALTER TABLE` sobre las tablas destino para reemplazar su partición
  vigente; se conservan los permisos ya necesarios de lectura, inserción y `TRUNCATE`.
- Tablas finales y `__NEXT` con la misma estructura y claves `MergeTree`, sin
  `PARTITION BY` explícito, como en `sql/create_ips_spam.sql`.

Instalación de rsync en una distribución basada en RHEL:

```bash
sudo dnf install -y rsync
rsync --version
```

En una distribución basada en Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y rsync
rsync --version
```

## Configuración

Toda la configuración de este proyecto se mantiene en
`src/ips_spam/.env`. El módulo no lee las variables de IPs Spam desde el `.env`
de la raíz.

Crear el archivo real a partir de la plantilla:

```bash
cp src/ips_spam/.env.example src/ips_spam/.env
chmod 600 src/ips_spam/.env
```

Luego completar en `src/ips_spam/.env`:

```dotenv
DB_CH_SPAM_HOST=172.19.242.107
DB_CH_SPAM_PORT=8123
DB_CH_SPAM_DATABASE=spam
DB_CH_SPAM_USERNAME=<USUARIO_CLICKHOUSE>
DB_CH_SPAM_PASSWORD=<PASSWORD_CLICKHOUSE>

UCEPROTECT_RSYNC_BASE=rsync-mirrors.uceprotect.net::RBLDNSD-ALL
UCEPROTECT_RSYNC_BINARY=rsync
UCEPROTECT_RSYNC_TIMEOUT_SECONDS=180
UCEPROTECT_ASN_URL=https://www.uceprotect.net/de/l3charts.php
UCEPROTECT_HTTP_TIMEOUT_SECONDS=60
UCEPROTECT_HTTP_USER_AGENT=py_apps-ips-spam/1.0
UCEPROTECT_PROXY_URL=http://claro-proxy:80
UCEPROTECT_STORAGE_DIR=/opt/airflow/tareas/py_apps/files/uceprotect
UCEPROTECT_BATCH_SIZE=10000

UCEPROTECT_AUDIT_TABLE=spam.UCEPRTC_AUDITORIA
UCEPROTECT_TABLE_LVL1=spam.UCEPRTC_LVL1
UCEPROTECT_TABLE_LVL2=spam.UCEPRTC_LVL2
UCEPROTECT_TABLE_LVL3=spam.UCEPRTC_LVL3
UCEPROTECT_TABLE_BACKSCATTER=spam.UCEPRTC_LST_BCK
UCEPROTECT_TABLE_WHITELIST=spam.UCEPRCT_LST_WHT
UCEPROTECT_TABLE_ASN=spam.UCEPRTC_ASN

UCEPROTECT_BRIDGE_HOST=192.168.195.247
UCEPROTECT_BRIDGE_USER=<USUARIO_SSH>
UCEPROTECT_BRIDGE_PASSWORD=<PASSWORD_SSH>
UCEPROTECT_BRIDGE_PORT=22
UCEPROTECT_BRIDGE_STORAGE_DIR=/opt/uceprotect_manual/current
UCEPROTECT_BRIDGE_TIMEOUT_SECONDS=180
UCEPROTECT_BRIDGE_MAX_AGE_SECONDS=86400
```

La recolección usa `paramiko.Transport` con el usuario y la contraseña del
`.env`, igual que `SFTPConnect` en el resto del repositorio. No requiere
`sshpass`, llave privada ni `known_hosts`. Este método no verifica la identidad
del servidor mediante una host key.

SFTP transfiere la instantánea completa en cada ejecución. Si el volumen crece,
ajustar `UCEPROTECT_BRIDGE_TIMEOUT_SECONDS` y el tiempo máximo del task
`collect_uceprotect_bridge` según la duración observada en Airflow.

### Proxy corporativo

Para utilizar el proxy corporativo Claro, configurar una sola variable:

```dotenv
UCEPROTECT_PROXY_URL=http://claro-proxy:80
```

El mismo proxy se utiliza para HTTP, HTTPS y rsync. Aunque la fuente ASN usa
HTTPS, el proxy indicado sigue siendo `http://claro-proxy:80`: el cliente crea
un túnel HTTP `CONNECT` hacia el sitio HTTPS final. No usar
`https://claro-proxy:80` salvo que Redes confirme explícitamente que el proxy
acepta TLS en ese puerto.

Si alguna conexión requiere una ruta distinta, se pueden reemplazar de manera
independiente:

```dotenv
UCEPROTECT_RSYNC_PROXY=claro-proxy:80
UCEPROTECT_HTTP_PROXY=http://claro-proxy:80
UCEPROTECT_HTTPS_PROXY=http://claro-proxy:80
```

El proxy se aplica solamente a UCEPROTECT y no a ClickHouse. Para rsync se
configura la variable de proceso `RSYNC_PROXY`; el proxy debe permitir el método
`CONNECT` hacia `rsync-mirrors.uceprotect.net:873`. Si ese túnel no está
permitido, la descarga ASN funcionará por proxy, pero Redes deberá habilitar
TCP/873 o proporcionar un mirror rsync interno.

En el flujo puente, estas variables de proxy se configuran en el servidor
`192.168.195.247` si son necesarias. Airflow en `10.96.167.139` no usa el proxy
para traer los datos: conecta por SFTP al servidor puente.

Para una prueba ejecutada fuera de Airflow, `UCEPROTECT_STORAGE_DIR` debe apuntar
a un directorio escribible de la máquina de prueba. Si se elimina esa variable,
el programa utiliza `files/uceprotect` dentro del repositorio.

## Creación de tablas

El script `sql/create_ips_spam.sql` crea la base, las seis tablas finales, las
tablas técnicas y la auditoría. Ejecutarlo una sola vez con un usuario que tenga
permisos DDL:

```bash
clickhouse-client \
  --host 172.19.242.107 \
  --port 9000 \
  --user '<USUARIO_CLICKHOUSE>' \
  --password \
  --multiquery < sql/create_ips_spam.sql
```

Si la base `spam` ya existe, el DDL no modifica su motor. Puede ser `Ordinary`
o `Atomic`; la publicación usa la partición `all` de las tablas definidas por
este proyecto:

```sql
SELECT name, engine
FROM system.databases
WHERE name = 'spam';
```

## Ejecución directa y prueba inicial con escritura

Las siguientes ejecuciones se realizan desde la raíz de `py_apps` en
`LIMQREDSHV02` o dentro de un worker Airflow. La descarga pública ya debe estar
publicada en `.247`, y las variables SSH del puente configuradas en el `.env`.
Antes de comenzar se debe:

1. Crear las tablas con `sql/create_ips_spam.sql`.
2. Completar `DB_CH_SPAM_USERNAME` y `DB_CH_SPAM_PASSWORD` en
   `src/ips_spam/.env`.
3. Confirmar que `UCEPROTECT_STORAGE_DIR` apunta a una carpeta escribible en la
   máquina remota. Si se elimina esa variable, se utiliza
   `files/uceprotect` dentro del repositorio.
4. Tener acceso SSH a `.247` y acceso ClickHouse a `172.19.242.107:8123`.

Recolectar la instantánea y probar inicialmente Level 1. El primer comando no
escribe en ClickHouse; el segundo carga los datos y los audita:

```bash
python -m src.ips_spam --collect-bridge
python -m src.ips_spam --source lvl1 --skip-download
```

La ejecución de carga registra el resultado en
`spam.UCEPRTC_AUDITORIA`. No se debe agregar `--extract-only`, porque esa opción
deshabilita intencionalmente la conexión y escritura en ClickHouse.

Validar la carga inicial:

```sql
SELECT count() FROM spam.UCEPRTC_LVL1;

SELECT *
FROM spam.UCEPRTC_AUDITORIA
WHERE FUENTE = 'lvl1'
ORDER BY FECHA_INICIO DESC
LIMIT 1;
```

Cuando Level 1 haya terminado correctamente, recolectar nuevamente la
instantánea y cargar las seis fuentes y sus tablas ClickHouse:

```bash
python -m src.ips_spam --collect-bridge
python -m src.ips_spam --source all --skip-download
```

La ejecución diaria automática la realiza el DAG. Para una ejecución manual
directa, primero recolectar y luego cargar:

```bash
python -m src.ips_spam --collect-bridge
python -m src.ips_spam --skip-download --source all
```

### Diagnóstico opcional sin escritura

El modo `--extract-only` comprueba parsing sin conectarse a ClickHouse ni
modificar tablas. Primero recolectar la instantánea desde `.247`.

```bash
python -m src.ips_spam --collect-bridge
python -m src.ips_spam --extract-only --skip-download --source all --sample-size 5
```

Para volver a interpretar archivos ya descargados sin acceder a las URLs:

```bash
python -m src.ips_spam \
  --extract-only \
  --skip-download \
  --source all
```

Valores permitidos para `--source`:

```text
all, lvl1, lvl2, lvl3, backscatter, whitelist, asn
```

En el DAG, la recolección debe terminar con `BRIDGE_COLLECT_OK`; después, cada
fuente presenta `SOURCE_RESULT` y el proceso final `LOAD_RESULT`. El modo directo
de descarga presenta `RSYNC_OK` o `HTTP_OK`.

## Validación en ClickHouse

```sql
SELECT 'LVL1' fuente, count() cantidad FROM spam.UCEPRTC_LVL1
UNION ALL
SELECT 'LVL2', count() FROM spam.UCEPRTC_LVL2
UNION ALL
SELECT 'LVL3', count() FROM spam.UCEPRTC_LVL3
UNION ALL
SELECT 'BACKSCATTER', count() FROM spam.UCEPRTC_LST_BCK
UNION ALL
SELECT 'WHITELIST', count() FROM spam.UCEPRCT_LST_WHT
UNION ALL
SELECT 'ASN', count() FROM spam.UCEPRTC_ASN;
```

Últimas ejecuciones auditadas:

```sql
SELECT
    FECHA_INICIO,
    FUENTE,
    ESTADO,
    REGISTROS_FUENTE,
    INSERTADOS,
    ACTUALIZADOS,
    ELIMINADOS,
    SIN_CAMBIOS,
    DETALLE_ERROR
FROM spam.UCEPRTC_AUDITORIA
ORDER BY FECHA_INICIO DESC
LIMIT 50;
```

## Despliegue en Airflow

1. Actualizar el repositorio en el servidor Airflow.
2. Crear `src/ips_spam/.env` desde su plantilla y completar las variables.
3. Confirmar que `paramiko` está disponible dentro de los workers que ejecuten
   el DAG.
4. Crear las tablas con `sql/create_ips_spam.sql`.
5. Completar `UCEPROTECT_BRIDGE_HOST`, `UCEPROTECT_BRIDGE_USER`,
   `UCEPROTECT_BRIDGE_PASSWORD` y las rutas puente en `src/ips_spam/.env`.
6. Copiar o sincronizar `dags/ips_spam_uceprotect.py` hacia el directorio de
   DAGs si el despliegue no lo realiza automáticamente.
7. Confirmar que `/opt/airflow/tareas/py_apps` está disponible en cada worker.
8. Confirmar que el timer del servidor puente publica antes de las 06:00.
9. Esperar a que Airflow registre `ips_spam_uceprotect`.
10. Ejecutar manualmente con `source=lvl1`, revisar carga y auditoría, y luego
    ejecutar `source=all`.
11. Habilitar el DAG.

El DAG se ejecuta diariamente a las **06:00 America/Lima**, tiene un máximo de
una ejecución simultánea, dos reintentos con diez minutos de espera y un timeout
de dos horas. Los parámetros manuales son:

- `source`: `all` o una fuente específica.

Cada corrida recolecta una instantánea validada del puente antes de procesar la
fuente solicitada. `full_download` ya no aplica en este DAG porque la descarga
externa ocurre en el servidor puente.

## Auditoría

Cada fuente registra una fila en `spam.UCEPRTC_AUDITORIA` con:

- Identificador de ejecución.
- Fuente y tabla destino.
- Fecha de inicio y fin.
- Estado `SUCCESS` o `ERROR`.
- Registros recibidos, insertados, actualizados, eliminados y sin cambios.
- Detalle del error.

El modo `--extract-only` no registra auditoría porque no establece una conexión
con ClickHouse.

## Recuperación ante errores

- Si falla la descarga en `.247`, no se publica la instantánea incompleta y se
  conserva `current` anterior.
- Si falla SFTP o la instantánea tiene más de 24 horas, el
  DAG no ejecuta la carga y reintenta.
- Si falla la descarga o recolección, las tablas vigentes de ClickHouse se
  conservan.
- Si el parser no encuentra registros, no publica una tabla vacía.
- Si falla una carga, revisar `DETALLE_ERROR` en `UCEPRTC_AUDITORIA` y el log de
  la tarea `load_uceprotect`.
- Para repetir manualmente el flujo completo, ejecutar primero
  `python -m src.ips_spam --collect-bridge` y después
  `python -m src.ips_spam --skip-download --source all`.
- No ejecutar dos procesos manuales simultáneos porque comparten tablas técnicas.
