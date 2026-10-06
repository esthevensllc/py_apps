# Recarga GDE desde el 1 de octubre de 2026

Este procedimiento vuelve a consultar la API con `ttcreatetime` y
`clearalarmfirstreceivetime` desde el **01/10/2026 00:00**, hora de Lima,
hasta el último intervalo completo de diez minutos en el momento de ejecutar
el SQL. El DAG normal continuará cargando los intervalos nuevos.

## Antes de publicar eventos

1. Confirmar que el código de GDE con `configured_field=ttcreatetime` está
   desplegado en el servidor de Airflow.
2. Aplicar la migración y el cambio del paquete Oracle de
   [RUNBOOK_TTCREATETIME.md](RUNBOOK_TTCREATETIME.md). El SQL de recarga
   comprueba que existan las dos columnas, pero no puede comprobar que
   `SP_ALARM_AUTIN_GESTOR` copie el valor entre tablas.
3. Confirmar que `PK_ALARMS_AUTIN_MN` esté válido y que sus excepciones se
   propaguen al consumidor según [RUNBOOK_ERROR_ORACLE.md](RUNBOOK_ERROR_ORACLE.md).
4. Desplegar el consumidor GDE actualizado, que atiende como máximo dos
   eventos por corrida. Mantener un solo DAG `gde_alarm` activo. No ejecutar
   un segundo `event_consumer` al mismo tiempo: ambos compartirían
   `GDE_ALARM_AUX`, que se vacía antes de cada carga.

## Publicar y consumir

Desde `/opt/airflow/tareas/py_apps`, se puede comprobar primero que la API
acepta las cuatro solicitudes de la ventana histórica sin escribir en Oracle.
`GdeApi` espera lo necesario para respetar tres consultas por minuto:

```bash
python - <<'PY'
from dotenv import load_dotenv
from src.gde.shared.services import GdeApi

load_dotenv('.env')
api = GdeApi()
uri = 'adc-intg/api/rest/v1/Alarm_WS/Alarm_WS/alarm_ws_integration/alarm/alarm_get'
queries = [('ttcreatetime', '12', 180)] + [
    ('clearalarmfirstreceivetime', hour, 60) for hour in ('10', '11', '12')
]
for field, hour, minutes in queries:
    params = {
        'date': f'2026-10-06 {hour}:00:00',
        'substract_minutes': minutes,
        'configured_field': field,
        'limit': 30000,
        'start': 0,
    }
    result = api.get(uri, params).json()
    print(field, 'total=', result.get('total'),
          'primera_pagina=', len(result.get('results', [])))
PY
```

Primero ejecutar
[sql/requeue_gde_alarm_pilot_20261006.sql](../../sql/requeue_gde_alarm_pilot_20261006.sql).
Publica solo el evento con `fec_ini=2026-10-06 12:00`, que consulta el tramo
09:00-12:00 del 6 de octubre e incluye el `ttcreatetime` de la alarma
`05102026_CUSCO_URUBAMBA`. Esperar a que el evento termine con `ESTADO=1` y
comprobar en el log `GDE_API_COMPLETE` para los dos campos, el conteo de filas
del control de carga y la presencia de la alarma en `AUTIN_ALARM_GESTOR`.
Registrar también la duración y el volumen de filas: una respuesta de 180
minutos puede ser mucho mayor que la respuesta normal de 20 minutos. Si el
piloto falla, revisar la causa antes de publicar el resto.

Cuando el piloto termine correctamente, ejecutar
[sql/requeue_gde_alarm_from_20261001.sql](../../sql/requeue_gde_alarm_from_20261001.sql)
en Oracle con el esquema de `PADM_QUEUE_EVENTS`. Se inserta **un evento por
intervalo de 180 minutos**. Hace un GET de `ttcreatetime` con
`substract_minutes=180` y tres GET de `clearalarmfirstreceivetime` con
`substract_minutes=60`, cubriendo las tres horas completas. La fecha `fec_ini` del evento es el extremo **final**
de la ventana de API: el primer evento, `2026-10-01 03:00`, consulta desde
`2026-10-01 00:00`. Si el corte no cae exactamente en una hora múltiplo de
tres, se agrega un último evento hasta el último intervalo completo de diez
minutos; esa última consulta puede solaparse con la anterior.
Los eventos llevan `backfill_id=gde-20261001-ttcreatetime` y prioridad `-1`.
Los eventos nuevos del DAG usan prioridad `0` y se atienden antes. Si se ejecuta
otra vez el SQL, omite los intervalos ya publicados con ese identificador.
El productor normal ignora los eventos marcados como recarga al decidir si
debe publicar una ventana actual; un evento histórico pendiente no bloquea
la carga normal de esa misma hora.
Si hay eventos publicados previamente con el mismo identificador y
`granularity` distinta de `180`, el SQL se detiene para evitar mezclar las
dos estrategias.
No hace falta borrar ni cambiar los registros `CARGADO` de
`PADM_CARGA_CONTROL`: el consumidor puede procesar un evento publicado
directamente aunque ese intervalo figure como cargado.

Dejar que el DAG existente procese la cola. `event_consumer` atiende como
máximo dos eventos por corrida, con un segundo de espera entre eventos;
después se ejecuta `metadata_updater` y la siguiente corrida vuelve a
publicar las alarmas actuales. Si una corrida tarda más de cinco minutos,
la siguiente empezará al terminar la actual (`max_active_runs=1`); las
alarmas nuevas pueden llegar con retraso, pero siguen dentro de la ventana
normal de búsqueda de un día. No iniciar otro consumidor en paralelo.

Si el corte fuese el 06/10/2026 17:00 en Lima, se publicarían unas 46
ventanas históricas. Para terminar antes del 07/10/2026 08:00, se necesitan
algo más de tres eventos por hora. **Cada evento puede traer muchas más filas
que uno de veinte minutos** y paginar varias veces; por eso la duración debe
medirse en la primera ventana antes de confiar en una hora de término. Si la
API o la inserción falla por tamaño o tiempo, no reintentar todas las ventanas
sin revisar primero ese límite.

## Seguimiento en Oracle

Para la ventana piloto, la prueba de API devolvió 1 634 filas de tickets y
25 404 + 32 143 + 30 491 = 88 038 filas de limpiezas. La API ignoró `limit=30000`
en dos respuestas; el consumidor acepta esas respuestas completas y registra
`GDE_API_OVERSIZED_PAGE`. Estos valores corresponden a esa prueba y pueden
cambiar si se vuelve a consultar. Falta medir la duración de inserción y del
procedimiento Oracle; los cinco minutos de las consultas no incluyen esa carga.

Para seguir el piloto y medir su duración:

```sql
SELECT id, estado, fecha_ini_exec, fecha_fin_exec, message
FROM padm_queue_events
WHERE queue_id = 'gde.alarm'
  AND JSON_VALUE(msg_body, '$.backfill_id') = 'gde-20261001-ttcreatetime'
  AND JSON_VALUE(msg_body, '$.fec_ini') = '2026-10-06 12:00'
ORDER BY id DESC;
```

```sql
SELECT estado, COUNT(*) AS eventos
FROM padm_queue_events
WHERE queue_id = 'gde.alarm'
  AND JSON_VALUE(msg_body, '$.backfill_id') = 'gde-20261001-ttcreatetime'
GROUP BY estado
ORDER BY estado;
```

Medir cuántos eventos de recarga terminaron en cada hora. Para llegar a la
mañana siguiente desde la tarde del 6 de octubre, la cifra debe superar
unos tres eventos por hora y dejar margen para errores:

```sql
SELECT TRUNC(fecha_fin_exec, 'HH24') AS hora,
       COUNT(*) AS ventanas_terminadas
FROM padm_queue_events
WHERE queue_id = 'gde.alarm'
  AND JSON_VALUE(msg_body, '$.backfill_id') = 'gde-20261001-ttcreatetime'
  AND estado = 1
GROUP BY TRUNC(fecha_fin_exec, 'HH24')
ORDER BY hora DESC;
```

`ESTADO=1` indica evento terminado; `0` pendiente, `2` en curso y `-1`
fallido. Para ver los fallidos:

```sql
SELECT id,
       JSON_VALUE(msg_body, '$.fec_ini') AS ventana,
       message
FROM padm_queue_events
WHERE queue_id = 'gde.alarm'
  AND JSON_VALUE(msg_body, '$.backfill_id') = 'gde-20261001-ttcreatetime'
  AND estado = -1
ORDER BY id;
```

Después de corregir la causa de un fallo, se puede volver a poner en cola
**solo el evento fallido identificado por su `ID`**:

```sql
UPDATE padm_queue_events
SET estado = 0, message = NULL
WHERE id = :id_evento
  AND queue_id = 'gde.alarm'
  AND estado = -1
  AND JSON_VALUE(msg_body, '$.backfill_id') = 'gde-20261001-ttcreatetime';
COMMIT;
```

Verificar la alarma que motivó el cambio:

```sql
SELECT alarmserialnumber, alarmid, node, firstoccurrence,
       ttcreatetime, severity, remedy_id
FROM autin_alarm_gestor
WHERE alarmserialnumber = '05102026_CUSCO_URUBAMBA';
```

Revisar asimismo los registros de control de los dos archivos por ventana
(`..._1.json` y `..._2.json`) y comparar las alarmas recibidas por la API
con `AUTIN_ALARM_GESTOR`. El GET de tickets abarca 180 minutos hacia atrás;
los tres GET de limpiezas abarcan 60 minutos cada uno. Alarmas con `ttcreatetime` nulo no entrarán
por la primera consulta.
