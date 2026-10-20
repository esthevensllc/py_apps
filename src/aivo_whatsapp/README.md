# WhatsApp mediante Aivo y Oracle

El proceso consulta averías y envía las plantillas al celular `numero_origen`
obtenido de Oracle. Ya no reemplaza el destino por el número usado en la prueba.
El DAG `aivo_whatsapp` ejecuta ambas plantillas cada 15 minutos, de 08:00 a 22:45
en America/Lima.

El diagnóstico consulta las últimas 24 horas mediante `SYSDATE - 1`. Al actualizar
esta versión, desplegar tanto el módulo Python como `dags/aivo_whatsapp.py` y
esperar a que Airflow cargue la nueva definición antes de iniciar otra ejecución.
Se retiró `--fecha-desde` y el parámetro `fecha_desde` del DAG. Este ajuste no
requiere crear tablas ni migrar el log de envíos.

## Historial de autenticación y auditoría de inválidos

Pausar el DAG y las pruebas manuales y ejecutar una sola vez
[create_aivo_audit_logs.sql](../../sql/create_aivo_audit_logs.sql) en el esquema
compartido antes de activar este código. Requiere `AIVO_AUTH_CACHE` existente;
para una instalación nueva, ejecutar primero `create_aivo_auth_cache.sql`.
Si todavía falta `FECHA_REGISTRO` en la caché, aplicar también la migración de
fecha indicada en la siguiente sección. No recrear tablas ni borrar su contenido.

`AIVO_AUTH_CACHE` conserva el token utilizable actual y su control de renovación.
`AIVO_AUTH_HISTORY` conserva una fila por intento de autenticación; las renovaciones
agregan filas sin reemplazar las anteriores. La reutilización de un token, consultar
`--auth-status` o una espera de seguridad no crean un nuevo intento. Guarda motivo,
estado, código HTTP y fechas Oracle `DATE` en hora de Lima: solicitud, registro,
finalización, próxima renovación y vencimiento. Guarda una huella SHA-256 del token
recibido; el historial no contiene Bearer reutilizables ni credenciales.

| Estado del historial | Significado |
|---|---|
| INICIADO | Reserva persistida antes de `/auth`; resultado aún no confirmado |
| GENERADO | Token recibido y caché/historial confirmados en la misma transacción |
| GENERADO_SIN_CACHE | Token válido recibido, pero falló guardar la caché; conserva metadatos de recepción si Oracle lo permite |
| ERROR_AUTH | No se confirmó un token utilizable; revisar código y detalle |
| MIGRADO | Último token reconstruido desde la caché al instalar la auditoría |

El motivo distingue `INICIAL`, `RENOVACION_PREVENTIVA`, `VENCIMIENTO`, `HTTP_401`
y `RECUPERACION`. Si falta el historial o falla guardar la reserva de autenticación,
no se llama a `/auth`. Las esperas y bloqueos de cuenta siguen vigentes. Ante una
interrupción, `INICIADO` no prueba que la API haya recibido el POST ni que haya creado
un token. Los conteos de recepción confirmada usan `GENERADO` y `GENERADO_SIN_CACHE`.

La instalación recupera solo el último token que todavía tenga metadatos y contenido
en la caché, marcado `MIGRADO`. Las creaciones anteriores sobrescritas no pueden
reconstruirse. Los conteos históricos completos empiezan al activar esta auditoría.

`AIVO_WHATSAPP_INVALID_LOG` guarda cada observación inválida sin intentar el envío:
ejecución, modo, ronda de prueba, plantilla, incidencia, celulares disponibles,
motivo, datos de origen JSON y fecha de registro en Lima. Sus campos admiten valores
nulos o inválidos que no caben en el log de reservas, evitando inventar destinatarios
o fechas. El estado es `INVALIDO` con `INTENTOS=0`. Si el origen se corrige después,
el evento vuelve a evaluarse y puede enviarse con la reserva habitual.

El resumen de cada lote incluye `id_ejecucion`. Cada inválido emite una advertencia
`INVALIDO` con ejecución, ID del registro, plantilla, incidencia y motivo; los datos
completos quedan en Oracle. Puede repetirse una observación en diferentes ejecuciones;
ese conteo representa observaciones, no clientes únicos. Un error al persistir la
auditoría detiene el lote y muestra `registro=sin_confirmar`. No se continúa perdiendo
evidencia. El estado de Airflow sigue dependiendo de si ya hubo mensajes aceptados.

En `--dry-run` se muestran las advertencias con `registro=vista_previa`, sin persistir
inválidos ni reservar mensajes. Un lote con solo inválidos sigue siendo correcto si
no hubo fallos de ejecución. Las reservas de envíos y los estados inciertos conservan
sus protecciones contra duplicados.

Consultas para revisar fechas, contar creaciones y ver motivos de inválidos:
[query_aivo_audit.sql](../../sql/query_aivo_audit.sql).

## Actualizar el resultado del lote y la fecha de registro del token

Para una instalación que ya tiene `AIVO_AUTH_CACHE`, pausar el DAG y las pruebas
manuales y ejecutar una sola vez
[migrate_aivo_auth_cache_fecha_registro.sql](../../sql/migrate_aivo_auth_cache_fecha_registro.sql)
antes de desplegar el nuevo código en todos los workers. La migración agrega
`FECHA_REGISTRO DATE` y recupera su valor a partir de `GENERATED_AT`, si existe.
No requiere generar otro token ni cambiar la clave Fernet. No recrear las tablas.
Para instalaciones nuevas, `create_aivo_auth_cache.sql` ya incluye la columna.

`FECHA_REGISTRO` contiene la fecha y hora de Lima (UTC-5) del último token
obtenido y guardado correctamente. Cambia cuando se renueva el token y se conserva
al reutilizarlo, rechazarlo o fallar una renovación. Puede ser nula si aún no se
ha obtenido un token o no existe una fecha anterior recuperable. Los campos epoch
UTC siguen controlando el vencimiento y los intervalos de autenticación.

Consulta directa, sin seleccionar el token cifrado:

```sql
SELECT account_key, fecha_registro, blocked, last_error_code
FROM AIVO_AUTH_CACHE;
```

El código de salida del proceso determina el estado de la tarea Airflow:

| Resultado del lote | Estado de la tarea |
|---|---|
| Uno o más mensajes aceptados, incluso con errores o inválidos | Correcto |
| Todos inválidos, duplicados o sin candidatos; sin errores de ejecución/envío | Correcto |
| Errores de ejecución/envío y ningún mensaje aceptado | Error |
| Fallo de configuración, Oracle o autenticación antes de enviar | Error |

Los contadores `errores`, `invalidos` y los registros de cada envío se conservan
para revisión aunque la tarea termine correctamente. Si un fallo posterior a
algún aceptado obliga a detener el lote, el resumen agrega `interrumpido=true` y
`error_proceso`; la tarea queda correcta por el éxito parcial. Ese resultado no
autoriza repetir mensajes reservados ni inciertos. La vista previa omite los
datos inválidos y solo falla ante errores del proceso, por ejemplo al leer Oracle.

## Actualizar la autenticación antes de reactivar el DAG

1. Pausar el DAG y detener ejecuciones manuales o versiones anteriores que usen
   la misma cuenta. La versión anterior autenticaba por mensaje y podía hacer
   tres intentos consecutivos; esa conducta se retiró.
2. Actualizar el código e instalar las dependencias de `requirements-oracle.txt`
   en todos los workers. Ahora se requiere `cryptography`.
3. Ejecutar una sola vez, en el mismo esquema Oracle de todas las ejecuciones,
   [create_aivo_auth_cache.sql](../../sql/create_aivo_auth_cache.sql). Crea
   `AIVO_AUTH_CACHE` y `AIVO_AUTH_GUARD`; no modifica el log de mensajes.
4. Generar una sola clave Fernet y guardar su valor como
   `AIVO_TOKEN_ENCRYPTION_KEY`, idéntico en todos los workers y pruebas manuales.
   Puede usarse el gestor de secretos del despliegue o el `.env` con acceso
   restringido. La clave se conserva entre ejecuciones; no es el Bearer de Aivo.
5. Revisar `--auth-status` y luego ejecutar `--check-auth` una vez. Al repetir
   `--check-auth` se reutiliza el token, sin otro inicio de sesión mientras esté
   vigente. Reactivar el DAG tras comprobar el esquema y las dependencias.

Generar la clave **una sola vez** en el servidor y guardar la salida:

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

No versionar esa salida ni regenerarla al iniciar el DAG. Si hay un token
almacenado y la clave no coincide, el proceso se detiene sin autenticarse de nuevo.
Las tres conexiones Oracle del lote son dedicadas: log de mensajes, caché y
exclusión de cuenta; las dos últimas también se necesitan para `--check-auth`.

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
AIVO_TOKEN_ENCRYPTION_KEY=
AIVO_TOKEN_REFRESH_HOURS=9
AIVO_AUTH_MIN_INTERVAL=900
AIVO_ORACLE_USER=
AIVO_ORACLE_PASSWORD=
AIVO_ORACLE_DSN=host:1521/servicio
AIVO_ORACLE_CLIENT_LIB_DIR=
```

La cuenta debe acceder al DB link `CLIATC.CI_FIJA_AUDIO_AVERIA@dbl_dwo`,
`remedy_inc_fija`, `AIVO_WHATSAPP_LOG`, `AIVO_AUTH_CACHE` y `AIVO_AUTH_GUARD`. Todos los workers y ejecuciones manuales
deben compartir el mismo esquema. El `.env` no se versiona; las variables del
entorno tienen prioridad y `--env-file` selecciona otro archivo de configuración.
No se carga el `.env` raíz automáticamente.

Ambos POST usan el proxy corporativo. La dirección del proxy es HTTP también
para destinos HTTPS: Requests crea un túnel CONNECT y mantiene TLS con Aivo.
Si se requiere una CA corporativa, establecer `REQUESTS_CA_BUNDLE` con su PEM.
La autenticación usa el campo `Authorization` de la respuesta y no duplica
`Bearer`. El token se guarda cifrado con Fernet en Oracle; no se imprime ni se
incluye en el log de mensajes. `AIVO_AUTH_TOKEN_FIELD` puede quedar vacío: es la
ruta de un campo JSON, no un token. Se busca `Authorization` y los campos
alternativos conocidos sin distinguir mayúsculas y minúsculas.

El token se obtiene cuando existe el primer mensaje por enviar o se ejecuta
`--check-auth`. Las siguientes ejecuciones de 15 minutos lo reutilizan desde
Oracle, aunque cambie el proceso o el worker. Se conservan generación, próxima
renovación y vencimiento. La renovación preventiva ocurre a las nueve horas,
o cinco minutos antes de `exp` si el JWT vence antes. La vigencia máxima asumida
es de diez horas; la validación criptográfica del JWT corresponde a Aivo.
Si no hay candidatos, el DAG no solicita un token. Las fechas se calculan con
el reloj UTC de Oracle, compartido por todos los workers.

Cada renovación hace **un solo POST a `/auth`**. Se retiraron los reintentos
consecutivos: `AIVO_AUTH_ATTEMPTS` y `AIVO_AUTH_RETRY_DELAY` ya no se leen y
pueden eliminarse del `.env`. Antes del POST se confirma en Oracle la hora del
intento y una espera mínima de 900 segundos (`AIVO_AUTH_MIN_INTERVAL`). Es una
salvaguarda de esta aplicación, no el límite oficial del proveedor. Si `/auth`
falla, hay timeout, falta el token o se interrumpe el proceso, otra ejecución
no puede iniciar sesión durante esa espera. El lote se detiene y registra el
error; el estado de la tarea depende de si ya hubo mensajes aceptados.

Ante el primer HTTP 401 del mensaje se invalida ese token para la renovación,
se obtiene uno nuevo y se reintenta el mismo mensaje una sola vez, dentro de
la misma reserva. Si otro proceso ya renovó el token rechazado, se reutiliza
el nuevo. Si el 401 afecta a un token recién generado, la espera mínima prevalece:
se detiene el lote sin otro login consecutivo. Un segundo 401 también detiene
el lote. No se renueva ni repite el mensaje por 403, 429, 5xx, timeout,
desconexión, JSON inválido ni error funcional con HTTP 200; se conserva el
control contra duplicados y la revisión manual de estados inciertos.

Los cuerpos JSON se revisan además del código HTTP: `error`, `errors`,
`exception`, `success=false`, estados de error y nombres de excepción se
consideran fallos. Un token presente junto a una excepción no se acepta.
El contrato completo de éxito del endpoint de plantillas debe confirmarse con
el proveedor; `ACEPTADO` significa 2xx sin esos indicadores, no entrega al celular.

`UserBlockedException`, incluso con HTTP 200, activa `BLOCKED=1` en Oracle,
borra el token utilizable y detiene los lotes. Las siguientes ejecuciones no
llaman a `/auth` hasta intervención explícita. Se emite `ALERTA AIVO` en el log
y se registra el motivo. La tarea termina con error si no hubo mensajes aceptados;
si ya hubo aceptados, termina correctamente como éxito parcial y la alerta sigue
en los logs. No configura avisos por correo externos.

`AIVO_AUTH_GUARD` mantiene un bloqueo real de fila Oracle durante todo el lote,
en una conexión separada que no confirma transacciones mientras se envía. Por
eso los commits de tokens y mensajes no abren una segunda ejecución simultánea
de la misma cuenta. Las llamadas son secuenciales y el DAG sigue con
`max_active_runs=1`, `retries=0`. El control abarca esta versión del proceso;
otros servicios, esquemas o versiones anteriores que usen la cuenta deben
coordinarse aparte. No es posible enumerar desde este repositorio los procesos
que estén ejecutándose en el servidor Airflow.

Las reglas de `hash/id` por cliente y cierre de conversación de la documentación
corresponden a los endpoints conversacionales `/conversation/messages` y
`/conversation/close`. Este proceso utiliza
`/conversation-whatsapp-native-templates`, cuyo payload suministrado no incluye
`hash/id` ni un identificador de sesión para cerrar. No se agregan campos ni
llamadas de cierre sin que el proveedor confirme el contrato para este endpoint.

Referencias: [mapeo de errores de Aivo](https://helpaivoes.aivohelp.com/article/mapeo-de-errores-y-consideraciones-tecnicas-de-la-api-de-mensajeria/926701)
y [buenas prácticas de Aivo](https://helpaivoes.aivohelp.com/article/5e-api/74069/faqs-y-buenas-practicas-sobre-la-api-de-mensajeria/926668).

## Revisar y rehabilitar una cuenta bloqueada

Consultar fechas UTC, espera y bloqueo, sin llamar al gateway ni mostrar el Bearer:

```bash
python3 -m src.aivo_whatsapp --auth-status
```

También puede revisarse el control sin seleccionar `TOKEN_ENCRYPTED`:

```sql
SELECT account_key, blocked, last_error_code,
       fecha_registro AS ultimo_token_lima,
       TIMESTAMP '1970-01-01 00:00:00' + NUMTODSINTERVAL(generated_at, 'SECOND') AS generado_utc,
       TIMESTAMP '1970-01-01 00:00:00' + NUMTODSINTERVAL(refresh_at, 'SECOND') AS renovar_utc,
       TIMESTAMP '1970-01-01 00:00:00' + NUMTODSINTERVAL(expires_at, 'SECOND') AS vence_utc,
       TIMESTAMP '1970-01-01 00:00:00' + NUMTODSINTERVAL(next_auth_at, 'SECOND') AS proximo_auth_utc
FROM AIVO_AUTH_CACHE;
```

Solo después de que el proveedor confirme el desbloqueo, con el DAG pausado y
sin ejecuciones manuales, rehabilitar **la cuenta específica** identificada en
la consulta anterior. No borrar filas ni reiniciar `LAST_AUTH_AT/NEXT_AUTH_AT`:

```sql
UPDATE AIVO_AUTH_CACHE
SET blocked = 0, last_error_code = NULL, token_encrypted = NULL,
    generated_at = NULL, refresh_at = NULL, expires_at = NULL
WHERE account_key = :account_key AND blocked = 1;
COMMIT;
```

Revisar que haya terminado la espera de seguridad antes de usar `--check-auth`.
El desbloqueo del proveedor no modifica por sí solo este control local.

## Destinatarios y parámetros

El celular de destino proviene de `numero_origen`. Se eliminan espacios, signos
`+`, paréntesis y guiones, conservando los dígitos que aporta Oracle para el POST.
Para deduplicar, el celular peruano local de nueve dígitos se normaliza con `51`:
`999000001` y `+51 999 000 001` identifican al mismo cliente. Esa normalización
de la clave no agrega automáticamente un prefijo al destino del mensaje.

Las consultas conservan `SELECT DISTINCT` y las reglas de negocio recibidas:

- Diagnóstico: peticiones de las últimas 24 horas (`a.fecha_peticion >= SYSDATE - 1`),
  fecha requerida no nula, duración menor o igual a ocho horas y las condiciones
  originales sobre solución/estado.
  `nombre_cliente` es el primer parámetro; `fecha_requerida` aporta hora y AM/PM
  de Lima. Las 20:00 producen `08:00` y `PM`.
- Solución: `fecha_solucion >= SYSDATE - (6/24)` y fecha de solución no nula.
  Utiliza únicamente `nombre_cliente` como parámetro.

Oracle calcula la ventana móvil con su propio reloj; no se envía un bind de fecha
ni se depende de `NLS_DATE_FORMAT`.
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
| ACEPTADO | Aivo respondió 2xx sin indicadores de error funcional; no confirma entrega |
| ERROR_AUTH | Falló la autenticación; con intentos=0 no hubo POST de mensaje |
| ERROR_HTTP | El POST respondió con error HTTP o funcional, incluso con HTTP 200 |
| INCIERTO | Timeout, desconexión o respuesta inválida durante el envío |

Los estados bloquean nuevos intentos, salvo `ERROR_AUTH` con `intentos=0`: esa
reserva nunca llegó al POST de mensajes y puede recuperarse en la siguiente
ejecución si el evento sigue siendo elegible en las consultas. La recuperación
es atómica y conserva el ID del registro; solo una ejecución puede obtenerla.
No hay recuperación automática de `ERROR_AUTH` con intentos=1, `ENVIANDO`,
`INCIERTO`, `ERROR_HTTP` ni `ACEPTADO`.

`INTENTOS` cuenta la reserva lógica del mensaje (0 antes de autenticar y 1 al
iniciar el envío). La única repetición HTTP permitida dentro de esa reserva es
la renovación tras un 401 explícito. Si se completa, `ERROR_DETALLE` puede incluir
una nota informativa de renovación aunque el estado sea `ACEPTADO`.
Si falla la persistencia después del POST, queda ENVIANDO y no se
repite. Esto prioriza evitar envíos duplicados y puede dejar un mensaje sin enviar
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
`--plantilla averia_solucionada`. El diagnóstico siempre usa `SYSDATE - 1`;
ya no recibe una fecha manual. El límite admite 1 a 1000 registros por plantilla.
La salida resume candidatos, aceptados, bloqueados, inválidos y errores.
Los errores individuales no hacen fallar la tarea si hubo al menos un aceptado;
los registros inválidos por sí solos tampoco hacen fallar la tarea.
Normalmente una ejecución posterior muestra cero candidatos para eventos ya
reservados; `bloqueados` identifica colisiones de reserva en el lote.

El envío directo por CLI sigue deshabilitado. `AivoClient.send_message(...)`
es de bajo nivel y no debe usarse como entrada operativa ni dentro del DAG.

Comprobar disponibilidad del token (reutiliza la caché; renueva solo si corresponde):

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
no vuelve a enviarlos. Las reservas se confirman antes del POST y bloquean
los timeouts y estados inciertos. Un `ERROR_AUTH` con cero intentos sí puede
recuperarse al repetir la prueba porque nunca solicitó el mensaje.
La clave es ronda + plantilla + destino
normalizado: usar después el prefijo `51` no evita el bloqueo.

Solo para una nueva ronda deliberada, cambiar `--test-id`, por ejemplo
`prueba_03`. No borrar registros. Los ID admiten letras, dígitos, guiones y
guiones bajos, hasta 64 caracteres. Las respuestas y reservas de prueba no
bloquean los mensajes de producción a los clientes originales.

El DAG no incluye estos argumentos y continúa enviando a los celulares Oracle.

## DAG Airflow

Archivo: [dags/aivo_whatsapp.py](../../dags/aivo_whatsapp.py).

- ID: `aivo_whatsapp`; horario `*/15 8-22 * * *`, de 08:00 a 22:45,
  en los minutos 00, 15, 30 y 45.
- Zona: America/Lima; `catchup=False` y `max_active_runs=1`.
- Se crea pausado para aplicar primero la migración; después se activa en Airflow.
- Una tarea ejecuta el módulo desde `/opt/airflow/tareas/py_apps`.
- Sin reintentos automáticos; límite de ejecución de 14 minutos.
- Parámetros: `batch_size=100`, `dry_run=false`.
- Credenciales, proxies y la misma clave de cifrado deben estar disponibles en todos los workers.
- Crear también `AIVO_AUTH_CACHE` y `AIVO_AUTH_GUARD` antes de activar esta versión.
- Si se interrumpe por timeout del DAG, las reservas confirmadas siguen bloqueadas.
- Errores de envío sin aceptados hacen fallar la tarea; con aceptados, el resultado
  es parcial correcto. Todos inválidos, duplicados o sin pendientes terminan correctamente.

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
y respuestas Aivo simuladas. Cubren reutilización entre workers, renovación,
espera persistente, bloqueo por cuenta y errores funcionales. Los bloqueos de
fila y permisos del nuevo DDL deben comprobarse en Oracle. Las pruebas del DAG verifican su construcción con
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
