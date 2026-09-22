# Runbook: descarga manual de UCEPROTECT

## Objetivo

Descargar manualmente las fuentes de UCEPROTECT desde el servidor
`192.168.195.247`, que actualmente sí dispone de salida a Internet, y generar
un paquete con la estructura que espera el proyecto `src.ips_spam`.

Este procedimiento es temporal. No inserta información en ClickHouse desde
`192.168.195.247`. La carga se realizará posteriormente en `LIMQREDSHV02`
mediante `python -m src.ips_spam --skip-download`.

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
| Directorio de trabajo recomendado | `/opt/uceprotect_manual` |
| Módulo rsync | `rsync-mirrors.uceprotect.net::RBLDNSD-ALL` |
| URL ASN | `https://www.uceprotect.net/de/l3charts.php` |

## Requisitos

- Acceso por terminal a `192.168.195.247`.
- Ejecutables `rsync`, `curl`, `tar` y `sha256sum`.
- Salida TCP/873 hacia `rsync-mirrors.uceprotect.net`.
- Salida HTTPS/TCP 443 hacia `www.uceprotect.net`.
- Espacio suficiente en `/opt`.

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

## Procedimiento de descarga

### 1. Ingresar como root

```bash
sudo -i
```

Si la sesión ya utiliza `root`, no es necesario ejecutar este comando.

### 2. Crear una instantánea de trabajo

Cada ejecución utiliza una carpeta fechada para no sobrescribir una descarga
anterior incompleta.

```bash
BASE=/opt/uceprotect_manual
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
  rsync-mirrors.uceprotect.net::RBLDNSD-ALL/ \
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
