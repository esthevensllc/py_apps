# Alarmas GDE

El DAG `gde_alarm` corre cada cinco minutos. `event_producer` genera eventos
para intervalos de diez minutos del último día, `event_consumer` los procesa y
después `metadata_updater` actualiza los datos de gestión de las alarmas ya
cargadas. En el contenedor de la aplicación, las claves `src.gde.stats.*` son
alias registrados por `GdeAppProvider`; las implementaciones están en
`src/gde/alarms/`.

La recarga puntual desde el 1 de octubre de 2026 usa eventos marcados como
históricos. Cada evento hace un GET de 180 minutos por `ttcreatetime` y tres
GET de 60 minutos por `clearalarmfirstreceivetime`, y se procesa
con menor prioridad que la carga normal. Consulte
[RUNBOOK_RECARGA_20261001.md](RUNBOOK_RECARGA_20261001.md).

Todas las solicitudes realizadas con `GdeApi`, incluidas las páginas y las
actualizaciones de metadatos, pasan por un límite de tres consultas por minuto
(separación mínima de 21 segundos). Los procesos comparten el archivo
`PYAPP_STORAGE_DIR/gde/.api_rate_limit`; todos los trabajadores deben usar el
mismo archivo compartido. Puede configurarse con `PYAPP_GDE_RATE_LIMIT_FILE`.
Las llamadas realizadas fuera de `GdeApi` no están coordinadas por ese límite.

Por cada intervalo se hacen dos GET a
`https://1at0-mx.teleows.com/adc-intg/api/rest/v1/Alarm_WS/Alarm_WS/alarm_ws_integration/alarm/alarm_get`.
Ambos envían `date=YYYY-MM-DD HH:MM:SS`, `substract_minutes=20`,
`limit=30000` y `start=0`. El primero envía
`configured_field=ttcreatetime`; el segundo envía
`configured_field=clearalarmfirstreceivetime`. La autenticación es HTTP Basic
con `PYAPP_GDE_USER` y `PYAPP_GDE_PASSWORD`.

`ttcreatetime` se almacena como `DATE` en `GDE_ALARM_AUX` y en
`AUTIN_ALARM_GESTOR`. Antes de desplegar el código, aplicar la migración y el
cambio del paquete Oracle descritos en [el runbook de `ttcreatetime`](RUNBOOK_TTCREATETIME.md).
La API puede devolver `ttcreatetime = null`; esas alarmas no entrarán por la
primera consulta basada en ese campo. Se mantiene la consulta de limpiezas,
pero no se debe interpretar como una cobertura de las alarmas activas sin
ticket.

El consumidor descarga todas las páginas de cada GET usando `total` y `start`.
Registra `GDE_API_PAGE` y `GDE_API_COMPLETE` con fecha, campo consultado,
cantidad recibida y total. Si la API devuelve menos filas de las declaradas
o una página vacía antes de completar el total, la carga falla. Si devuelve
más filas que `total`, registra `GDE_API_TOTAL_MISMATCH` y procesa todas las
filas recibidas. Cuando una página trae menos filas que `limit` pero todavía
faltan filas según `total`, hace una consulta adicional. Si esta trae por sí
sola el total declarado, utiliza esa respuesta completa sin sumarla a la
primera. En caso contrario reinicia desde `start=0` hasta tres veces.
Los datos se transforman en archivos JSON
temporales dentro de `PYAPP_STORAGE_DIR/gde/<uuid>/`; el cargador los elimina
al terminar. No se conserva una copia permanente de la respuesta original.

Al terminar el consumidor, `metadata_updater` toma una sola fecha actual para
dos GET secuenciales al mismo endpoint. El primero usa
`configured_field=last_remark_update_time` y el segundo
`configured_field=last_remedy_update_time`; ambos envían
`substract_minutes=180`, `limit=30000` y paginan con `start`. La primera
respuesta actualiza solamente `REMARK` y la segunda solamente `REMEDY_ID` en
`AUTIN_ALARM_GESTOR`. La búsqueda usa `alarmserialnumber`, `alarmname`,
`alarmid`, `node`, `emsname` y `firstoccurrence`, la misma identidad del
procedimiento de carga. Las alarmas que aún no existen en la tabla final no se
insertan durante esta etapa. Se descargan y validan las dos respuestas antes
de escribir en Oracle; los dos grupos de actualizaciones se confirman juntos.
Los logs `GDE_METADATA_PAGE` y `GDE_METADATA_COMPLETE` permiten revisar las
filas recibidas y las filas encontradas en la tabla final. Si falla la etapa,
la tarea `metadata_updater` queda en error en Airflow.
Esta etapa también acepta filas adicionales a `total`, registrando
`GDE_METADATA_TOTAL_MISMATCH`, y reinicia desde `start=0` cuando una página
corta no alcanza el total declarado.

Para cada evento, el cargador elimina el contenido de `gde_alarm_aux`, inserta
las filas de las dos consultas y ejecuta
`pk_alarms_autin_mn.sp_alarm_autin_load`. El control de carga marca `CARGADO`
solo después de que esa llamada termina sin error. El procedimiento llama a
`SP_ALARM_AUTIN_GESTOR`, que copia las filas a `AUTIN_ALARM_GESTOR`.

## Errores de Oracle

Los procedimientos Oracle originales capturan sus excepciones sin relanzarlas.
Consulta el [runbook de propagación de errores](RUNBOOK_ERROR_ORACLE.md) para
actualizar `SP_ALARM_AUTIN_GESTOR` y `SP_ALARM_AUTIN_LOAD`, recompilar el
paquete y verificar que los fallos lleguen al consumidor GDE.

## Seguimiento de una alarma

Busque en los logs `GDE_API_PAGE` del intervalo de `ttcreatetime` y de
`clearalarmfirstreceivetime`. Una alarma puede aparecer en cualquiera de las
dos consultas. Luego verifique su `alarmserialnumber`, `alarmid`, `node`,
`emsname` y `firstoccurrence` en `AUTIN_ALARM_GESTOR`. La tabla auxiliar es
transitoria: la siguiente carga la vacía.

Al desplegar `dags/gde_alarm.py`, sustituya la definición anterior del DAG
con el mismo `dag_id`; dos archivos que definan `gde_alarm` causarían un
conflicto de registro en Airflow.
