# WhatsApp mediante Aivo y Oracle

Proceso para leer averías de Oracle, reservar cada envío en la base de datos y
solicitar mensajes con las plantillas `averia_diagnosticada` y
`averia_solucionada`. La autenticación y el envío usan POST y el proxy corporativo.
No se creó un DAG; `run_batch(...)` es el punto de entrada para la futura tarea.

La etapa actual es de prueba: el destino está fijado a `999876502` y se permite
como máximo un intento por plantilla en ese número. Las tablas se crean vacías,
sin registros iniciales: la primera ejecución con candidatos válidos podrá
solicitar un diagnóstico y una solución; la segunda debe omitir ambos.

## Instalación y configuración

Desde la raíz del repositorio:

```bash
python3 -m pip install -r src/aivo_whatsapp/requirements-oracle.txt
```

Si `cx_Oracle` ya está instalado en Airflow, puede utilizarse ese driver sin
instalar otro. En caso contrario se utiliza `python-oracledb`. Si este último
requiere modo thick, configurar `AIVO_ORACLE_CLIENT_LIB_DIR` con la carpeta de
Instant Client. La conexión es dedicada y tiene autocommit desactivado.

Para una instalación nueva, copiar `.env.example` a `.env` dentro de
`src/aivo_whatsapp`. En una instalación existente, agregar las variables nuevas
SIN sobrescribir las credenciales actuales:

```dotenv
AIVO_USER=
AIVO_PASSWORD=
AIVO_X_TOKEN=
AIVO_HTTP_PROXY=http://claro-proxy
AIVO_HTTPS_PROXY=http://claro-proxy
AIVO_TIMEOUT=30
AIVO_ORACLE_USER=
AIVO_ORACLE_PASSWORD=
AIVO_ORACLE_DSN=host:1521/servicio
AIVO_ORACLE_CLIENT_LIB_DIR=
```

La cuenta Oracle debe acceder a `CLIATC.CI_FIJA_AUDIO_AVERIA@dbl_dwo`,
`remedy_inc_fija` y las tablas de control. Todos los procesos y futuros workers
deben compartir las mismas tablas en el mismo esquema. El `.env` está ignorado
por Git. Las variables del entorno tienen prioridad; `--env-file` permite
seleccionar otro archivo. No se carga el `.env` raíz automáticamente.

`AIVO_HTTPS_PROXY` indica el destino HTTPS, pero su valor es `http://claro-proxy`
porque el proxy se contacta por HTTP y establece un túnel CONNECT hacia Aivo.
TLS con Aivo permanece habilitado. Si las variables AIVO de proxy están vacías,
Requests utiliza las variables estándar del entorno. Si infraestructura indica
un puerto, incluirlo explícitamente en la URL.
Ver [documentación de proxies de urllib3](https://urllib3.readthedocs.io/en/stable/advanced-usage.html#http-and-https-proxies).

`AIVO_TIMEOUT` limita la espera de conexión y lectura de cada POST, no la
operación completa. `/auth` devuelve `{"Authorization": "Bearer <token>"}`:
se retira el prefijo y se construye el header una sola vez. No se imprime ni
se guarda el token. Si cambia el campo, puede indicarse una ruta mediante
`AIVO_AUTH_TOKEN_FIELD`; también se admiten `token`, `access_token`, `data.token`
y `data.access_token` por compatibilidad.

## Creación de tablas

Ejecutar COMPLETO, una sola vez y en el mismo esquema utilizado por el proceso,
el script [create_aivo_whatsapp_log.sql](../../sql/create_aivo_whatsapp_log.sql).
Desde SQL*Plus, con el repositorio como directorio actual:

```sql
@sql/create_aivo_whatsapp_log.sql
```

El script crea:

- `AIVO_WHATSAPP_LOG`: reserva, datos de origen, JSON solicitado, respuesta del
  envío, código HTTP, fechas, estado y contador de intentos.
- `AIVO_WA_TEST_GUARD`: bloqueo por plantilla y destino. Se crea vacío y el
  proceso inserta la reserva en la misma transacción que el log antes de enviar.

No borrar filas, recrear las tablas ni deshabilitar sus claves. Antes de
procesar mensajes se comprueba que las claves estén habilitadas y validadas.
Si falta una tabla, clave, commit o permiso, no se autoriza continuar con el POST.
No insertar bloqueos manuales para esta prueba. Las reservas se crean durante
el primer intento y se conservan para las siguientes ejecuciones.

## Protección contra duplicados

La clave del evento es `numero_cliente + fecha_inicio_averia + plantilla`.
`fecha_inicio_averia` proviene de `a.fecha_envio`, con fecha, hora, segundos y
microsegundos; no se sustituye por la hora estimada ni por la hora de ejecución.
El celular de origen se normaliza: `999876502` y `+51 999 876 502` generan la
misma clave. Incidencia y documento quedan para auditoría; cambiar la incidencia
o la fecha estimada no habilita otro intento para el mismo evento.

El control adicional de prueba permite una sola reserva por plantilla y
`999876502`, aunque las consultas devuelvan clientes diferentes. La reserva del
evento y la del destino se insertan en una misma transacción con claves únicas,
y se confirman ANTES de autenticar. Una reserva duplicada se omite sin llamar a
Aivo. Antes del POST se confirma `ENVIANDO` con `intentos=1`.

| Estado | Significado |
|---|---|
| `RESERVADO` | Reserva confirmada antes de autenticar |
| `ENVIANDO` | Intento registrado antes del POST; puede indicar una interrupción |
| `ACEPTADO` | Aivo respondió 2xx; no confirma entrega al celular |
| `ERROR_AUTH` | Falló la autenticación; no se solicitó el envío |
| `ERROR_HTTP` | El POST de envío respondió con error HTTP |
| `INCIERTO` | Timeout, desconexión o respuesta inválida después de iniciar el envío |

TODOS los estados bloquean futuros intentos. No hay reintentos ni reapertura
automática, incluso si Airflow reinicia la tarea. Si Aivo recibe el mensaje y
falla el guardado del resultado, permanece `ENVIANDO` y tampoco se repite.
Esto prioriza evitar un segundo POST: puede dejar un mensaje sin enviar si el
proceso muere entre el commit previo y la llamada. No garantiza entrega ni
controla posibles duplicaciones internas del proveedor.

## Consultas y parámetros

Las consultas proporcionadas están en `src/aivo_whatsapp/sql/`, con columnas
calificadas y fecha mínima enviada como bind DATE para evitar depender de
`NLS_DATE_FORMAT`.

- Diagnóstico: fecha de petición desde `2026-10-08`, fecha requerida no nula y
  duración menor o igual a cinco horas, conservando las condiciones originales.
  `nombre_cliente` es el primer parámetro. `fecha_requerida` aporta hora y AM/PM
  en formato de 12 horas de Lima: 20:00 produce `08:00` y `PM`.
- Solución: se mantiene `fecha_solucion >= SYSDATE - (6/24)` y
  `fecha_solucion IS NOT NULL`. Solo utiliza `nombre_cliente` como parámetro.

Se conservaron los `OR` proporcionados. Una incidencia puede aparecer en ambas
consultas si fecha de solución y estado Remedy no coinciden. No se cambió la
regla de negocio para resolver ese posible solapamiento.

Se conservan el namespace `c44af9b7_3008_4b30_b7e8_070c35442389`,
`type=template`, `recipient_type=individual` y `language.policy=deterministic`.
Diagnóstico usa campaña `69f45f6b-31d3-4337-b6d5-b0f31997aef5` e idioma `es_PE`;
solución usa campaña `a8a6350f-898a-4077-a20e-8b96e3731786` e idioma `en`.

## Ejecución

Vista previa: consulta Oracle y valida las tablas, pero no reserva filas ni
llama a Aivo. Solo requiere credenciales Oracle:

```bash
python3 -m src.aivo_whatsapp --from-oracle --dry-run --limit 1
```

Procesar el diagnóstico con control de duplicados:

```bash
python3 -m src.aivo_whatsapp --from-oracle --plantilla averia_diagnosticada --fecha-desde 2026-10-08 --limit 100
```

Procesar la solución:

```bash
python3 -m src.aivo_whatsapp --from-oracle --plantilla averia_solucionada --limit 100
```

Sin `--plantilla` procesa ambas en ese orden. `--limit` limita las filas
consultadas por plantilla, no la protección del número. El resumen informa
`candidatos`, `aceptados`, `bloqueados`, `invalidos` y `errores`. Filas sin celular,
nombre o fecha confiable se omiten. La salida es `1` por errores, datos inválidos
o configuración incorrecta; omitir un duplicado es esperado y devuelve `0`.
Las respuestas se guardan como CLOB, ocultando tokens y credenciales.

Con tablas vacías, la primera ejecución puede aceptar dos solicitudes, una por
plantilla, siempre que ambas consultas devuelvan candidatos válidos y Aivo
responda correctamente. Al repetirla, `aceptados` debe ser cero y los candidatos
válidos se contabilizan como `bloqueados`. Para habilitar destinatarios reales se
necesitará otra modificación de código y restricciones. No hay una opción para
activar producción ni para eliminar los bloqueos.

El envío manual con `--to`, `--nombre`, `--hora` y `--periodo` está deshabilitado
salvo con `--dry-run`, porque no utiliza el control persistente. La operación
`AivoClient.send_message(...)` queda como API de bajo nivel; no invocarla en un
DAG ni en el proceso operativo, pues no consulta las reservas.

## Comprobar autenticación y conexión

```bash
python3 -m src.aivo_whatsapp --check-auth
```

Realiza solo el POST de autenticación, sin mensajes ni impresión del token.
Los errores muestran la causa de conexión con credenciales ocultas. Para probar
el esquema HTTP del proxy sin modificar `.env`:

```bash
AIVO_HTTPS_PROXY=http://claro-proxy python3 -m src.aivo_whatsapp --check-auth
```

Si falla la verificación del certificado, instalar las CA confiables en el
contenedor o establecer `REQUESTS_CA_BUNDLE` con la ruta del archivo PEM.
Si falla el proxy, revisar las variables AIVO y las estándar `HTTPS_PROXY`,
`HTTP_PROXY` y `NO_PROXY`. No se deshabilita TLS.

## Uso desde una futura tarea Airflow

Dentro de la ejecución de la tarea, nunca al importar el DAG:

```python
from pathlib import Path
from dotenv import load_dotenv
from src.aivo_whatsapp import AivoClient, AivoSettings, run_batch
from src.aivo_whatsapp.repository import OracleRepository, connect_oracle

load_dotenv(Path("src/aivo_whatsapp/.env"))
client = AivoClient(AivoSettings.from_environment())
connection, driver = connect_oracle()
try:
    resumen = run_batch(OracleRepository(connection, driver), client)
finally:
    connection.close()
```

Las credenciales deben estar disponibles en el worker. También puede pasarse
una conexión dedicada al repositorio y la configuración Aivo desde Airflow.
El flujo omite reservas existentes aunque la tarea vuelva a ejecutarse. Un
fallo de persistencia después del POST interrumpe el lote y conserva el bloqueo.

## Verificación y pruebas sin envíos reales

```bash
python3 -m unittest discover -s tests/aivo_whatsapp -v
```

Las pruebas de transacciones y concurrencia usan conexiones SQLite separadas
como simulador de Oracle y respuestas Aivo simuladas. No sustituyen la
validación del DDL, permisos y consultas en Oracle real.

Consultar las reservas generadas y el log:

```sql
SELECT plantilla, numero_destino, motivo, id_envio, fecha_registro
FROM AIVO_WA_TEST_GUARD
ORDER BY plantilla;

SELECT id_envio, plantilla, incidencia, numero_cliente, numero_destino,
       fecha_inicio_averia, estado, intentos, http_status,
       fecha_registro, fecha_actualizacion,
       DBMS_LOB.SUBSTR(respuesta_json, 4000, 1) AS respuesta
FROM AIVO_WHATSAPP_LOG
ORDER BY fecha_registro DESC;
```

Tras el primer intento deben existir las reservas de las plantillas procesadas,
con `id_envio` vinculado al log. Repetir la ejecución debe mantener esas reservas
y producir cero POST nuevos. También quedan bloqueados los fallos y estados
inciertos; una segunda ejecución no intenta recuperar ni repetir el mensaje.
