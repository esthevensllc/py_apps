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
└── README.md         # Esta documentación
```

Archivos relacionados fuera de la carpeta:

- DAG: `dags/ips_spam_uceprotect.py`
- DDL: `sql/create_ips_spam.sql`
- Configuración: `.env` y `.env.example` en la raíz del repositorio

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

La versión nueva se publica con `EXCHANGE TABLES` solamente después de descargar,
interpretar y cargar correctamente la fuente. Esto permite:

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
- Ejecutable `rsync` disponible para el usuario que ejecuta Python y para los
  workers de Airflow.
- Salida DNS y TCP 873 hacia `rsync-mirrors.uceprotect.net`.
- Salida HTTPS/TCP 443 hacia `www.uceprotect.net` para la tabla ASN.
- Acceso HTTP de ClickHouse desde Airflow hacia `172.19.242.107:8123`.
- Base `spam` con motor `Atomic`, necesaria para la publicación mediante
  `EXCHANGE TABLES`.

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

Toda la configuración permanece en el único archivo `.env` de la raíz. No se
debe crear otro `.env` dentro de `src/ips_spam`.

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
UCEPROTECT_STORAGE_DIR=/opt/airflow/tareas/py_apps/files/uceprotect
UCEPROTECT_BATCH_SIZE=10000

UCEPROTECT_AUDIT_TABLE=spam.UCEPRTC_AUDITORIA
UCEPROTECT_TABLE_LVL1=spam.UCEPRTC_LVL1
UCEPROTECT_TABLE_LVL2=spam.UCEPRTC_LVL2
UCEPROTECT_TABLE_LVL3=spam.UCEPRTC_LVL3
UCEPROTECT_TABLE_BACKSCATTER=spam.UCEPRTC_LST_BCK
UCEPROTECT_TABLE_WHITELIST=spam.UCEPRCT_LST_WHT
UCEPROTECT_TABLE_ASN=spam.UCEPRTC_ASN
```

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

Si la base `spam` ya existe, confirmar que utiliza motor `Atomic`:

```sql
SELECT name, engine
FROM system.databases
WHERE name = 'spam';
```

## Ejecución directa y prueba inicial con escritura

Las siguientes pruebas se ejecutan desde la raíz de `py_apps` en la máquina
remota. Antes de comenzar se debe:

1. Crear las tablas con `sql/create_ips_spam.sql`.
2. Completar `DB_CH_SPAM_USERNAME` y `DB_CH_SPAM_PASSWORD` en el `.env` raíz.
3. Confirmar que `UCEPROTECT_STORAGE_DIR` apunta a una carpeta escribible en la
   máquina remota. Si se elimina esa variable, se utiliza
   `files/uceprotect` dentro del repositorio.
4. Tener acceso desde esa máquina a las fuentes y a
   `172.19.242.107:8123`.

La prueba inicial recomendada descarga Level 1 y **guarda directamente** en
`spam.UCEPRTC_LVL1`:

```bash
python -m src.ips_spam --source lvl1 --full-download
```

Esta ejecución también registra el resultado en
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

Cuando Level 1 haya terminado correctamente, cargar las seis fuentes y sus
tablas ClickHouse:

```bash
python -m src.ips_spam --source all --full-download
```

La ejecución diaria directa, que utiliza la transferencia incremental de
rsync y actualiza las tablas, es:

```bash
python -m src.ips_spam
```

### Diagnóstico opcional sin escritura

El modo `--extract-only` sirve únicamente para comprobar descarga y formato. No
crea una conexión a ClickHouse y no modifica ninguna tabla.

```bash
python -m src.ips_spam \
  --extract-only \
  --source lvl1 \
  --sample-size 5

python -m src.ips_spam \
  --extract-only \
  --source asn \
  --sample-size 5

python -m src.ips_spam --extract-only --source all
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

Un resultado correcto presenta mensajes `RSYNC_OK` o `HTTP_OK`, luego un
`SOURCE_RESULT` por fuente y finalmente `LOAD_RESULT`.

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
2. Completar las variables anteriores en el `.env` existente.
3. Instalar `rsync` dentro de todos los workers que puedan ejecutar el DAG.
4. Crear las tablas con `sql/create_ips_spam.sql`.
5. Copiar o sincronizar `dags/ips_spam_uceprotect.py` hacia el directorio de
   DAGs si el despliegue no lo realiza automáticamente.
6. Confirmar que `/opt/airflow/tareas/py_apps` está disponible en cada worker.
7. Esperar a que Airflow registre `ips_spam_uceprotect`.
8. Ejecutar manualmente primero con `source=lvl1` y `full_download=true`.
9. Validar tabla y auditoría.
10. Ejecutar manualmente con `source=all` y `full_download=true`.
11. Habilitar el DAG.

El DAG se ejecuta diariamente a las **06:00 America/Lima**, tiene un máximo de
una ejecución simultánea, dos reintentos con diez minutos de espera y un timeout
de dos horas. Los parámetros manuales son:

- `source`: `all` o una fuente específica.
- `full_download`: `true` para forzar nuevamente todos los bytes por rsync.

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

- Si rsync o HTTPS fallan, se conserva la tabla vigente y el DAG reintenta.
- Si el parser no encuentra registros, no publica una tabla vacía.
- Si falla una carga, revisar `DETALLE_ERROR` en `UCEPRTC_AUDITORIA` y el log de
  la tarea `load_uceprotect`.
- Para repetir sin descargar, usar `--skip-download` en ejecución directa.
- Para reconstruir el espejo local, usar `--full-download`.
- No ejecutar dos procesos manuales simultáneos porque comparten tablas técnicas.
