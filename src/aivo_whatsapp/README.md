# WhatsApp mediante Aivo y Oracle

El proceso consulta averías y envía las plantillas al celular `numero_origen`
obtenido de Oracle. Ya no reemplaza el destino por el número usado en la prueba.
El DAG `aivo_whatsapp` ejecuta ambas plantillas cada 15 minutos, en America/Lima.

## Actualizar una instalación que ya hizo la prueba

1. Mantener pausadas las ejecuciones mientras se actualiza el código.
2. Actualizar el repositorio en `/opt/airflow/tareas/py_apps`.
3. Ejecutar UNA SOLA VEZ en el mismo esquema del log el script
   [migrate_aivo_whatsapp_production.sql](../../sql/migrate_aivo_whatsapp_production.sql).
4. Verificar una vista previa y los errores de importación de Airflow.
5. Activar el DAG `aivo_whatsapp` en Airflow.

En SQL*Plus, desde la raíz del repositorio:

```sql
@sql/migrate_aivo_whatsapp_production.sql
```

La migración conserva todas las filas y agrega `MODO`. Los registros existentes
se identifican como `PRUEBA`, pues fueron enviados al número de prueba y no al
cliente de origen. Las nuevas reservas son `PRODUCCION`. Así la prueba no bloquea
mensajes que los clientes reales todavía no recibieron.

Se retiran únicamente las restricciones que fijaban el destino y limitaban a
un mensaje por plantilla para todo el número de prueba. La clave de producción
es `MODO + NUMERO_CLIENTE + FECHA_INICIO_AVERIA + PLANTILLA`.
`AIVO_WA_TEST_GUARD` se conserva como historial y deja de utilizarse.
No recrear las tablas ni borrar registros para pasar a producción.

Para una instalación nueva, ejecutar solamente
[create_aivo_whatsapp_log.sql](../../sql/create_aivo_whatsapp_log.sql), que ya
crea el log de producción. No ejecutar la migración sobre una instalación nueva.

## Dependencias y configuración

```bash
python3 -m pip install -r src/aivo_whatsapp/requirements-oracle.txt
```

Si el servidor ya tiene `cx_Oracle`, se utiliza ese driver. De lo contrario se
utiliza `python-oracledb`; si requiere modo thick, indicar la carpeta Instant
Client en `AIVO_ORACLE_CLIENT_LIB_DIR`. La conexión del log es dedicada y tiene
autocommit desactivado.

Mantener en `src/aivo_whatsapp/.env` las credenciales y proxies existentes:

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

La cuenta debe acceder al DB link `CLIATC.CI_FIJA_AUDIO_AVERIA@dbl_dwo`,
`remedy_inc_fija` y `AIVO_WHATSAPP_LOG`. Todos los workers y ejecuciones manuales
deben compartir el mismo esquema. El `.env` no se versiona; las variables del
entorno tienen prioridad y `--env-file` selecciona otro archivo de configuración.
No se carga el `.env` raíz automáticamente.

Ambos POST usan el proxy corporativo. La dirección del proxy es HTTP también
para destinos HTTPS: Requests crea un túnel CONNECT y mantiene TLS con Aivo.
Si se requiere una CA corporativa, establecer `REQUESTS_CA_BUNDLE` con su PEM.
La autenticación usa el campo `Authorization` de la respuesta y no duplica
`Bearer`. No se imprime ni se guarda el token.

## Destinatarios y parámetros

El celular de destino proviene de `numero_origen`. Se eliminan espacios, signos
`+`, paréntesis y guiones, conservando los dígitos que aporta Oracle para el POST.
Para deduplicar, el celular peruano local de nueve dígitos se normaliza con `51`:
`999000001` y `+51 999 000 001` identifican al mismo cliente. Esa normalización
de la clave no agrega automáticamente un prefijo al destino del mensaje.

Las consultas conservan `SELECT DISTINCT` y las reglas de negocio recibidas:

- Diagnóstico: peticiones desde `2026-10-08`, fecha requerida no nula, duración
  menor o igual a cinco horas y las condiciones originales sobre solución/estado.
  `nombre_cliente` es el primer parámetro; `fecha_requerida` aporta hora y AM/PM
  de Lima. Las 20:00 producen `08:00` y `PM`.
- Solución: `fecha_solucion >= SYSDATE - (6/24)` y fecha de solución no nula.
  Utiliza únicamente `nombre_cliente` como parámetro.

La fecha mínima se envía como bind DATE, evitando depender de `NLS_DATE_FORMAT`.
Se mantienen los `OR`: una incidencia puede aparecer en ambas consultas si las
fechas y el estado Remedy no coinciden. No se cambió esa regla de negocio.

Antes del límite del lote, el proceso excluye eventos ya reservados en
PRODUCCION. Así los siguientes lotes avanzan a nuevos clientes, sin quedarse
consultando únicamente los primeros cien registros procesados.

## Control contra duplicados

El log registra modo, incidencia, cliente, destino, fecha de inicio de avería,
fechas de solución, JSON solicitado, respuesta, código HTTP y estado.
`fecha_inicio_averia` es `a.fecha_envio`, con fecha/hora completa y microsegundos.
Cambiar la incidencia, nombre o fecha estimada no habilita repetir el mismo evento.

La reserva se inserta con una clave única y se confirma ANTES de autenticar.
Antes del POST se confirma `ENVIANDO` e `intentos=1`. Incluso con dos procesos
simultáneos, solo el que obtiene la reserva puede solicitar el mensaje.
Cada cliente puede recibir un diagnóstico y una solución por avería. Una nueva
fecha de inicio permite notificar una avería nueva al mismo cliente.

| Estado | Significado |
|---|---|
| RESERVADO | Reserva confirmada antes de autenticar |
| ENVIANDO | Intento confirmado antes del POST; también puede indicar interrupción |
| ACEPTADO | Aivo respondió 2xx; no confirma entrega al celular |
| ERROR_AUTH | Falló la autenticación y no se solicitó el envío |
| ERROR_HTTP | El POST respondió con error HTTP |
| INCIERTO | Timeout, desconexión o respuesta inválida durante el envío |

Todos los estados bloquean nuevos intentos. No hay reintentos ni reapertura
automática. Si falla la persistencia después del POST, queda ENVIANDO y no se
repite. Esto prioriza evitar un segundo POST y puede dejar un mensaje sin enviar
si la ejecución se interrumpe entre el commit previo y la llamada. No garantiza
entrega ni controla duplicaciones internas del proveedor.

El proceso comprueba las restricciones antes de consultar candidatos. Si el
esquema todavía tiene las restricciones de prueba o no tiene la nueva clave,
se interrumpe antes de enviar. También verifica que el payload corresponda al
cliente y datos obtenidos de Oracle.

## Comandos manuales

Vista previa sin reservar ni llamar a Aivo, después de migrar el esquema:

```bash
python3 -m src.aivo_whatsapp --from-oracle --dry-run --limit 5
```

Enviar ambos tipos con control persistente, a los destinatarios reales:

```bash
python3 -m src.aivo_whatsapp --from-oracle --limit 100
```

Puede filtrarse con `--plantilla averia_diagnosticada` o
`--plantilla averia_solucionada`. La fecha de diagnóstico se ajusta mediante
`--fecha-desde YYYY-MM-DD`. El límite admite 1 a 1000 registros por plantilla.
La salida resume candidatos, aceptados, bloqueados, inválidos y errores.
Normalmente una ejecución posterior muestra cero candidatos para eventos ya
reservados; `bloqueados` identifica colisiones de reserva en el lote.

El envío directo por CLI sigue deshabilitado. `AivoClient.send_message(...)`
es de bajo nivel y no debe usarse como entrada operativa ni dentro del DAG.

Comprobar solo autenticación:

```bash
python3 -m src.aivo_whatsapp --check-auth
```

## Prueba manual a un único número

Para repetir una prueba como la realizada con el número personal, ejecutar una
sola vez [create_aivo_whatsapp_test_log.sql](../../sql/create_aivo_whatsapp_test_log.sql)
en el esquema Oracle. Crea `AIVO_WHATSAPP_TEST_LOG`, separado del log de
producción; no modifica sus registros ni requiere cambiar el DAG.

La prueba lee los mismos datos Oracle, incluso si el número de destino no
aparece en las consultas. Las dos plantillas se redirigen a `--test-to`.
Primero se puede revisar el JSON sin enviar:

```bash
python3 -m src.aivo_whatsapp --from-oracle --test-to 999876502 --test-id prueba_02 --limit 1 --dry-run
```

Solicitar los mensajes de esa ronda:

```bash
python3 -m src.aivo_whatsapp --from-oracle --test-to 999876502 --test-id prueba_02 --limit 1
```

Sin `--plantilla`, permite como máximo un diagnóstico y una solución, si hay
datos válidos en ambas consultas. Repetir el mismo comando con el mismo ID
no vuelve a enviarlos. Las reservas se confirman antes del POST y también
bloquean los errores y timeouts. La clave es ronda + plantilla + destino
normalizado: usar después el prefijo `51` no evita el bloqueo.

Solo para una nueva ronda deliberada, cambiar `--test-id`, por ejemplo
`prueba_03`. No borrar registros. Los ID admiten letras, dígitos, guiones y
guiones bajos, hasta 64 caracteres. Las respuestas y reservas de prueba no
bloquean los mensajes de producción a los clientes originales.

El DAG no incluye estos argumentos y continúa enviando a los celulares Oracle.

## DAG Airflow

Archivo: [dags/aivo_whatsapp.py](../../dags/aivo_whatsapp.py).

- ID: `aivo_whatsapp`; horario `*/15 * * * *`, minutos 00, 15, 30 y 45.
- Zona: America/Lima; `catchup=False` y `max_active_runs=1`.
- Se crea pausado para aplicar primero la migración; después se activa en Airflow.
- Una tarea ejecuta el módulo desde `/opt/airflow/tareas/py_apps`.
- Sin reintentos automáticos; límite de ejecución de 14 minutos.
- Parámetros: `fecha_desde=2026-10-08`, `batch_size=100`, `dry_run=false`.
- Credenciales y proxies deben estar disponibles en todos los workers.
- Si se interrumpe por timeout del DAG, las reservas confirmadas siguen bloqueadas.

Antes de activarlo, comprobar en el servidor:

```bash
airflow dags list-import-errors
```

Para una ejecución manual de inspección, usar `dry_run=true`. El tamaño de lote
se puede ajustar dentro del rango permitido. La frecuencia es cada 15 minutos;
una ejecución no se superpone con la anterior.

## Verificación

```bash
python3 -m unittest discover -s tests/aivo_whatsapp -v
```

Las pruebas de persistencia y concurrencia usan SQLite como simulador de Oracle
y respuestas Aivo simuladas. Las pruebas del DAG verifican su construcción con
interfaces simuladas; el import real debe comprobarse en Airflow.

Consultar el log:

```sql
SELECT id_envio, modo, plantilla, incidencia, numero_cliente, numero_destino,
       fecha_inicio_averia, estado, intentos, http_status,
       fecha_registro, fecha_actualizacion,
       DBMS_LOB.SUBSTR(respuesta_json, 4000, 1) AS respuesta
FROM AIVO_WHATSAPP_LOG
ORDER BY fecha_registro DESC;
```
