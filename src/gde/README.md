# Alarmas GDE

El DAG `gde_alarm` corre cada cinco minutos. `event_producer` genera eventos
para intervalos de diez minutos del último día y `event_consumer` los procesa
después. En el contenedor de la aplicación, las claves `src.gde.stats.*` son
alias registrados por `GdeAppProvider`; las implementaciones están en
`src/gde/alarms/`.

Por cada intervalo se hacen dos GET a
`https://1at0-mx.teleows.com/adc-intg/api/rest/v1/Alarm_WS/Alarm_WS/alarm_ws_integration/alarm/alarm_get`.
Ambos envían `date=YYYY-MM-DD HH:MM:SS`, `substract_minutes=20`,
`limit=30000` y `start=0`. El primero envía
`configured_field=firstoccurrence`; el segundo envía
`configured_field=clearalarmfirstreceivetime`. La autenticación es HTTP Basic
con `PYAPP_GDE_USER` y `PYAPP_GDE_PASSWORD`.

El consumidor descarga todas las páginas de cada GET usando `total` y `start`.
Registra `GDE_API_PAGE` y `GDE_API_COMPLETE` con fecha, campo consultado,
cantidad recibida y total. Si la API devuelve una página vacía antes de
completar el total, la carga falla. Los datos se transforman en archivos JSON
temporales dentro de `PYAPP_STORAGE_DIR/gde/<uuid>/`; el cargador los elimina
al terminar. No se conserva una copia permanente de la respuesta original.

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

Busque en los logs `GDE_API_PAGE` del intervalo de `firstoccurrence` y de
`clearalarmfirstreceivetime`. Una alarma puede aparecer en cualquiera de las
dos consultas. Luego verifique su `alarmserialnumber`, `alarmid`, `node`,
`emsname` y `firstoccurrence` en `AUTIN_ALARM_GESTOR`. La tabla auxiliar es
transitoria: la siguiente carga la vacía.

Al desplegar `dags/gde_alarm.py`, sustituya la definición anterior del DAG
con el mismo `dag_id`; dos archivos que definan `gde_alarm` causarían un
conflicto de registro en Airflow.
