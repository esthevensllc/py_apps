# Runbook: servidor puente UCEPROTECT

## Objetivo

Configurar `192.168.195.247` para descargar diariamente las fuentes UCEPROTECT
y publicar una instantánea; luego el DAG de Airflow en `10.96.167.139` la
recolecta por SFTP y ejecuta el cargador existente para ClickHouse.

El servidor puente no se conecta a ClickHouse. La descarga pública se ejecuta
solo en `.247`; el parser, sincronización, auditoría y carga permanecen en
Airflow en `.139`.

## Alcance

El procedimiento descarga:

- UCEPROTECT Level 1: `dnsbl-1.uceprotect.net`.
- UCEPROTECT Level 2: `dnsbl-2.uceprotect.net`.
- UCEPROTECT Level 3: `dnsbl-3.uceprotect.net`.
- Backscatter: `ips.backscatterer.org`.
- Whitelist: `ips.whitelisted.org`.
- Tabla ASN: `https://www.uceprotect.net/de/l3charts.php`.

## Servidores y rutas

| Elemento | Valor |
|---|---|
| Servidor de descarga temporal | `192.168.195.247` |
| Servidor Airflow destino | `LIMQREDSHV02` |
| Directorio de publicación | `/opt/uceprotect_manual/current` |
| Directorio local de Airflow | valor de `UCEPROTECT_STORAGE_DIR` en `.139` |
| Módulo rsync | `rsync-mirrors.uceprotect.net::RBLDNS-ALL` |
| URL ASN | `https://www.uceprotect.net/de/l3charts.php` |

## Requisitos

- Acceso por terminal a `192.168.195.247`.
- Ejecutables `rsync`, `curl`, `tar` y `sha256sum`.
- Salida TCP/873 hacia `rsync-mirrors.uceprotect.net`.
- Salida HTTPS/TCP 443 hacia `www.uceprotect.net`.
- Espacio suficiente en `/opt`.
- En `.139`, acceso SSH/TCP 22 hacia `.247` y paquete Python `paramiko` dentro
  del worker.
- Usuario y contraseña SSH autorizados para lectura, y host key verificada.

Si el servidor requiere el proxy corporativo Claro, definir antes de descargar:

```bash
export RSYNC_PROXY=claro-proxy:80
export https_proxy=http://claro-proxy:80
```

`RSYNC_PROXY` requiere que el proxy permita `CONNECT` hacia TCP/873. La variable
`https_proxy` se utiliza para descargar la página ASN. No usar
`https://claro-proxy:80` salvo confirmación de Redes de que ese puerto acepta
TLS hacia el proxy.

Validar los ejecutables sin descargar información:

```bash
command -v rsync
command -v curl
command -v tar
command -v sha256sum
```

## Instalación de descarga diaria en 192.168.195.247

Copiar el script `src/ips_spam/ops/bridge_refresh.sh` desde el repositorio al
servidor y registrarlo:

```bash
sudo install -o root -g root -m 0755 bridge_refresh.sh \
  /usr/local/sbin/uceprotect-bridge-refresh
sudo mkdir -p /opt/uceprotect_manual/snapshots
```

El script descarga `RBLDNS-ALL` en una sola sesión rsync, obtiene la página
ASN, valida la presencia de todas las fuentes y publica la instantánea mediante
un cambio atómico de `current`. Si la descarga o validación falla, se conserva
la instantánea previamente publicada.

Instalar los archivos systemd del repositorio:

```bash
sudo install -o root -g root -m 0644 uceprotect-bridge.service \
  /etc/systemd/system/uceprotect-bridge.service
sudo install -o root -g root -m 0644 uceprotect-bridge.timer \
  /etc/systemd/system/uceprotect-bridge.timer
sudo systemctl daemon-reload
```

Configurar lectura para la cuenta de recolección. El servidor debe crear antes
el usuario técnico y agregarlo al grupo `uceprotect-readers`; luego:

```bash
sudo groupadd --force uceprotect-readers
id -u uceprotect_reader >/dev/null 2>&1 || \
  sudo useradd --system --gid uceprotect-readers --create-home \
    --shell /bin/bash uceprotect_reader
sudo usermod -aG uceprotect-readers uceprotect_reader
sudo mkdir -p /opt/uceprotect_manual/snapshots
sudo chgrp uceprotect-readers /opt/uceprotect_manual \
  /opt/uceprotect_manual/snapshots
sudo chmod 2750 /opt/uceprotect_manual \
  /opt/uceprotect_manual/snapshots
```

El servicio publica los archivos con el grupo `uceprotect-readers` y permisos
de lectura y recorrido para ese grupo. La cuenta no necesita permiso de
escritura sobre las descargas.

Ejecutar una carga inicial y revisar su resultado antes de activar el horario:

```bash
sudo systemctl start uceprotect-bridge.service
sudo systemctl status uceprotect-bridge.service --no-pager
sudo journalctl -u uceprotect-bridge.service -n 100 --no-pager
```

Activar el horario diario a las 05:00 (hora local configurada en `.247`):

```bash
sudo systemctl enable --now uceprotect-bridge.timer
sudo systemctl list-timers uceprotect-bridge.timer
```

Para probar después de un cambio:

```bash
sudo systemctl start uceprotect-bridge.service
sudo readlink -f /opt/uceprotect_manual/current
test -s /opt/uceprotect_manual/current/html/l3charts.html
test -s /opt/uceprotect_manual/current/READY
```

## Configurar recolección en 10.96.167.139

En `src/ips_spam/.env` del servidor Airflow, ajustar estos valores:

```dotenv
UCEPROTECT_STORAGE_DIR=/opt/airflow/tareas/py_apps/files/uceprotect
UCEPROTECT_BRIDGE_HOST=192.168.195.247
UCEPROTECT_BRIDGE_USER=<USUARIO_SSH>
UCEPROTECT_BRIDGE_PASSWORD=<PASSWORD_SSH>
UCEPROTECT_BRIDGE_PORT=22
UCEPROTECT_BRIDGE_STORAGE_DIR=/opt/uceprotect_manual/current
UCEPROTECT_BRIDGE_KNOWN_HOSTS=/opt/airflow/.ssh/known_hosts
UCEPROTECT_BRIDGE_TIMEOUT_SECONDS=180
UCEPROTECT_BRIDGE_MAX_AGE_SECONDS=86400
```

La contraseña se mantiene únicamente en `src/ips_spam/.env`, que no se versiona;
el proceso la usa mediante `paramiko`. No se requiere `sshpass` ni llave privada.
Registrar la host key SSH
de `.247` en `UCEPROTECT_BRIDGE_KNOWN_HOSTS` después de verificar su huella con
el administrador del servidor.

El flujo del DAG es:

```text
05:00 .247: uceprotect-bridge.timer descarga y publica current
06:00 .139: collect_uceprotect_bridge trae la instantánea a UCEPROTECT_STORAGE_DIR
06:00 .139: load_uceprotect procesa --skip-download y carga ClickHouse
```

La recolección instala en el staging local, valida las cinco carpetas de listas,
`html/l3charts.html` y `READY` (máximo 24 horas), y solo entonces reemplaza la
carpeta local vigente. Una transferencia incompleta o vencida no llega al paso
de carga.

Validar manualmente desde un worker, antes de habilitar el DAG:

```bash
sudo docker exec -u 50000:0 airflow-airflow-worker-1 \
  python -m src.ips_spam --collect-bridge
sudo docker exec -u 50000:0 airflow-airflow-worker-1 \
  python -m src.ips_spam --skip-download --extract-only --source all
```

`--collect-bridge` solo recolecta y valida archivos. El segundo comando solo
valida parsing y no escribe ClickHouse. La carga real se ejecuta con el DAG o
con `python -m src.ips_spam --skip-download --source all`.

## Alternativa de descarga manual y empaquetado

Usar el procedimiento manual siguiente cuando el timer de `.247` no esté
instalado o sea necesario recuperar una instantánea puntual.

### Procedimiento manual de descarga

### 1. Ingresar como root

```bash
sudo -i
```

Si la sesión ya utiliza `root`, no es necesario ejecutar este comando.

### 2. Crear una instantánea de trabajo

Cada ejecución utiliza una carpeta fechada para no sobrescribir una descarga
anterior incompleta.

```bash
BASE=/opt/uceprotect_manual/manual_runs
STAMP=$(date +%Y%m%d_%H%M%S)
SNAPSHOT="$BASE/snapshots/$STAMP"
STORAGE="$SNAPSHOT/storage"

mkdir -p "$SNAPSHOT/raw"
mkdir -p "$STORAGE/rsync/lvl1"
mkdir -p "$STORAGE/rsync/lvl2"
mkdir -p "$STORAGE/rsync/lvl3"
mkdir -p "$STORAGE/rsync/backscatter"
mkdir -p "$STORAGE/rsync/whitelist"
mkdir -p "$STORAGE/html"
mkdir -p "$BASE/logs"
```

Mantener la misma sesión de terminal hasta terminar el procedimiento, porque
las variables anteriores se utilizan en los siguientes comandos.

### 3. Descargar el módulo rsync completo

Realizar una sola sincronización externa. No ejecutar una descarga separada
por cada lista, para reducir el número de conexiones hacia UCEPROTECT.

```bash
rsync -avz \
  --partial \
  --delay-updates \
  --timeout=180 \
  rsync-mirrors.uceprotect.net::RBLDNS-ALL/ \
  "$SNAPSHOT/raw/" \
  2>&1 | tee "$BASE/logs/rsync_$STAMP.log"
```

Confirmar el código de salida de `rsync`, no solamente el de `tee`:

```bash
test "${PIPESTATUS[0]}" -eq 0
```

El comando no debe mostrar ningún mensaje. Un código distinto de cero indica
que la descarga no debe distribuirse ni cargarse.

### 4. Validar las cinco listas requeridas

```bash
for archivo in \
  dnsbl-1.uceprotect.net \
  dnsbl-2.uceprotect.net \
  dnsbl-3.uceprotect.net \
  ips.backscatterer.org \
  ips.whitelisted.org
do
  if [ -e "$SNAPSHOT/raw/$archivo" ]; then
    echo "OK: $archivo"
  else
    echo "ERROR: falta $archivo"
  fi
done
```

Los cinco elementos deben presentar `OK`. Si falta alguno, detener el
procedimiento y revisar el log `rsync_$STAMP.log`.

### 5. Construir la estructura esperada por el proyecto

```bash
cp -a "$SNAPSHOT/raw/dnsbl-1.uceprotect.net" \
  "$STORAGE/rsync/lvl1/"
cp -a "$SNAPSHOT/raw/dnsbl-2.uceprotect.net" \
  "$STORAGE/rsync/lvl2/"
cp -a "$SNAPSHOT/raw/dnsbl-3.uceprotect.net" \
  "$STORAGE/rsync/lvl3/"
cp -a "$SNAPSHOT/raw/ips.backscatterer.org" \
  "$STORAGE/rsync/backscatter/"
cp -a "$SNAPSHOT/raw/ips.whitelisted.org" \
  "$STORAGE/rsync/whitelist/"
```

### 6. Descargar la tabla ASN

Descargar primero hacia un archivo temporal, de modo que una respuesta
incompleta no sea considerada válida.

```bash
curl -fL \
  --retry 3 \
  --connect-timeout 20 \
  --max-time 120 \
  -A "py_apps-ips-spam/1.0" \
  -o "$STORAGE/html/l3charts.html.tmp" \
  "https://www.uceprotect.net/de/l3charts.php"
```

Validar que el archivo no esté vacío y que contenga elementos esperados:

```bash
test -s "$STORAGE/html/l3charts.html.tmp"
grep -Eqi "UCEPROTECT|Spam-Score|Provider" \
  "$STORAGE/html/l3charts.html.tmp"
```

Si ambos comandos terminan correctamente, publicar el archivo:

```bash
mv "$STORAGE/html/l3charts.html.tmp" \
  "$STORAGE/html/l3charts.html"
```

### 7. Revisar la estructura final

```bash
find "$STORAGE" -maxdepth 4 -type f -printf '%p %s bytes\n' | sort
```

La estructura mínima debe ser:

```text
storage/
├── READY
├── html/
│   └── l3charts.html
└── rsync/
    ├── backscatter/
    │   └── ips.backscatterer.org
    ├── lvl1/
    │   └── dnsbl-1.uceprotect.net
    ├── lvl2/
    │   └── dnsbl-2.uceprotect.net
    ├── lvl3/
    │   └── dnsbl-3.uceprotect.net
    └── whitelist/
        └── ips.whitelisted.org
```

Los elementos recibidos por rsync podrían ser archivos o directorios. Esto es
válido porque el parser del proyecto procesa recursivamente su contenido.

### 8. Empaquetar y generar checksum

```bash
PACKAGE="$BASE/uceprotect_$STAMP.tar.gz"

tar -C "$SNAPSHOT" -czf "$PACKAGE" storage
sha256sum "$PACKAGE" | tee "$PACKAGE.sha256"
ls -lh "$PACKAGE" "$PACKAGE.sha256"
```

Conservar juntos el archivo `.tar.gz` y su `.sha256`.

## Transferencia futura hacia LIMQREDSHV02

Cuando se autorice la transferencia, copiar ambos archivos a
`LIMQREDSHV02`. En el servidor destino, verificar primero la integridad:

```bash
sha256sum -c uceprotect_YYYYMMDD_HHMMSS.tar.gz.sha256
```

Extraer en un directorio temporal:

```bash
mkdir -p /tmp/uceprotect_import
tar -xzf uceprotect_YYYYMMDD_HHMMSS.tar.gz \
  -C /tmp/uceprotect_import
```

Copiar el contenido de `storage` al directorio configurado en
`UCEPROTECT_STORAGE_DIR`. Para Airflow, el valor actualmente documentado es:

```text
/opt/airflow/tareas/py_apps/files/uceprotect
```

Ejemplo, ajustando la ruta si la configuración vigente es diferente:

```bash
mkdir -p /opt/airflow/tareas/py_apps/files/uceprotect
rsync -a --delete \
  /tmp/uceprotect_import/storage/ \
  /opt/airflow/tareas/py_apps/files/uceprotect/
```

No ejecutar este paso sobre una ruta diferente sin comprobar antes el valor de
`UCEPROTECT_STORAGE_DIR`, porque `--delete` elimina archivos sobrantes en el
directorio destino.

## Carga posterior en ClickHouse

Desde la raíz de `py_apps` en `LIMQREDSHV02`, procesar los archivos ya
descargados sin intentar acceder a Internet:

```bash
python -m src.ips_spam --skip-download --source all
```

Este comando sí escribe en las tablas ClickHouse y en
`spam.UCEPRTC_AUDITORIA`. No agregar `--extract-only` si se requiere guardar la
información.

Para validar solamente el formato, sin escribir en ClickHouse:

```bash
python -m src.ips_spam \
  --extract-only \
  --skip-download \
  --source all
```

## Validación posterior en ClickHouse

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

Revisar la última auditoría:

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
LIMIT 10;
```

## Frecuencia y precauciones

- Ejecutar como máximo una descarga completa durante la operación manual
  planificada.
- No lanzar dos descargas simultáneas desde la misma IP.
- No reutilizar una instantánea cuya descarga o validación haya fallado.
- No modificar manualmente los archivos dentro de `storage`.
- Conservar el log y el checksum junto al paquete entregado.
- Registrar fecha, operador, nombre del paquete y resultado de la carga.

## Diagnóstico de errores

### `Connection refused` o código rsync 10

El servidor no logra establecer la conexión TCP/873 con el mirror. Confirmar
que el comando se ejecuta realmente en `192.168.195.247` y remitir el log a
Redes si el problema continúa.

### `Connection timed out`

Revisar la ruta de red y la habilitación TCP/873 o HTTPS/443, según la fuente
que falle.

### HTTP 403, 429 o página sin filas ASN

No cargar el archivo. Conservar la tabla ClickHouse vigente y revisar si
UCEPROTECT cambió la protección o estructura de `l3charts.php`.

### El checksum no coincide

No extraer ni procesar el paquete. Transferir nuevamente el `.tar.gz` y repetir
`sha256sum -c`.

### Falla la carga con `--skip-download`

Confirmar que el contenido fue copiado directamente dentro de
`UCEPROTECT_STORAGE_DIR` y que existen las carpetas `rsync/lvl1`,
`rsync/lvl2`, `rsync/lvl3`, `rsync/backscatter`, `rsync/whitelist` y el archivo
`html/l3charts.html`.
