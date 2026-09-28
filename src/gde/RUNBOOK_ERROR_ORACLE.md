# Runbook: propagar errores de Oracle en la carga GDE

## Objetivo

Si falla la carga de una alarma, el error no debe quedar oculto dentro de los
procedimientos PL/SQL. Debe llegar a `GdeEventConsumerFromConfig`, que marcará
el evento de cola con `estado = -1` y enviará la notificación de error.

> El consumidor captura los errores de cada evento. Por eso la cola y la
> notificación reflejan el fallo, pero la tarea Bash de Airflow puede terminar
> con código cero. Para que el DAG también quede en estado `failed`, habría
> que cambiar por separado el consumidor para que devuelva un error al terminar.

## Cambios en el paquete

Editar y recompilar el cuerpo de `PK_ALARMS_AUTIN_MN`. No ejecutar estos
fragmentos como procedimientos independientes: las rutinas pertenecen al
paquete y se deben integrar en su fuente completa.

### 1. Mantener el correo de `SP_ALARM_AUTIN_GESTOR` y propagar el error

Reemplazar sus dos manejadores actuales (el grupo de errores específicos y
`WHEN OTHERS`) por este bloque. El `send_mail` queda protegido para que un
fallo al notificar no oculte la excepción original:

```sql
EXCEPTION
  WHEN OTHERS THEN
    err_msg := SUBSTR(SQLERRM, 1, 100);
    ROLLBACK;

    BEGIN
      send_mail(
        'juan.burga',
        'juan.burga',
        'juan.burga',
        'PROBLEMAS EN PK_ALARMS_AUTIN_MN.SP_ALARM_AUTIN_GESTOR',
        'Se presento el siguiente problema : ' || err_msg,
        'SOPORTE_BD_HUAWEI'
      );
    EXCEPTION
      WHEN OTHERS THEN
        NULL; -- Preservar el error original si falla el envío del correo.
    END;

    RAISE;
END SP_ALARM_AUTIN_GESTOR;
```

### 2. Mantener el correo de `SP_ALARM_AUTIN_LOAD` y devolver el error al cliente

Reemplazar sus dos manejadores actuales por este bloque. El manejador interior
evita que un problema en `send_mail` sustituya el error original:

```sql
EXCEPTION
  WHEN OTHERS THEN
    err_msg := SUBSTR(SQLERRM, 1, 100);
    ROLLBACK;

    BEGIN
      send_mail(
        'daniel.munante',
        'daniel.munante',
        'daniel.munante',
        'PROBLEMAS EN PK_ALARMS_AUTIN_MN.SP_ALARM_AUTIN_LOAD',
        'Se presento el siguiente problema : ' || err_msg,
        'SOPORTE_BD_HUAWEI'
      );
    EXCEPTION
      WHEN OTHERS THEN
        NULL; -- Preservar el error original si falla el envío del correo.
    END;

    RAISE;
END SP_ALARM_AUTIN_LOAD;
```

`RAISE;` dentro de un manejador vuelve a lanzar la excepción actual al
procedimiento que hizo la llamada. Así, el error atraviesa
`SP_ALARM_AUTIN_LOAD` y llega al driver Oracle de Python.

Con esta opción, un error en el gestor genera un correo desde cada
procedimiento: `SP_ALARM_AUTIN_GESTOR` notifica y relanza; luego
`SP_ALARM_AUTIN_LOAD` recibe ese error, notifica y también lo relanza.

## Transacciones y `COMMIT`

`SP_ALARM_AUTIN_GESTOR` tiene `COMMIT` después del `UPDATE`, del `DELETE` y del
`INSERT`. Un `ROLLBACK` posterior no revierte operaciones ya confirmadas.
Si se requiere que la actualización de `AUTIN_ALARM_GESTOR` sea atómica,
revisar primero todos los llamadores del procedimiento y, si ninguno depende
de esos commits, retirarlos para que el llamador confirme la transacción al
terminar correctamente. El wrapper Oracle del proyecto hace `COMMIT` cuando
la llamada PL/SQL retorna sin error.

La limpieza e inserción de `gde_alarm_aux` ocurren antes de llamar a estos
procedimientos y ya están confirmadas por el proceso Python; el `ROLLBACK`
del procedimiento no restaura el contenido auxiliar anterior.

## Compilación y verificación

1. Aplicar el cambio en un ambiente de pruebas y recompilar el `PACKAGE BODY`.
2. Confirmar que no existan errores de compilación:

   ```sql
   SELECT name, type, line, position, text
   FROM user_errors
   WHERE name = 'PK_ALARMS_AUTIN_MN'
   ORDER BY type, sequence;
   ```

3. Provocar una falla controlada en pruebas durante la carga.
4. Confirmar que el evento GDE quede con `estado = -1`, que lleguen los
   correos de ambos procedimientos si falló el gestor y que el log del
   consumidor contenga el error Oracle original.
5. En producción, revisar que una ejecución correcta siga marcando el evento
   como procesado.

### Consultas para validar una ejecución

El log de ejemplo del 28/09/2026 procesó el evento `280262701` para el
intervalo de archivo 10:20–10:30, hora de Lima. En ese log, la API informó y
el proceso recibió 12 214 filas por `firstoccurrence` y 12 731 por
`clearalarmfirstreceivetime`. Para otras ejecuciones, sustituir el ID y la
fecha por los valores del log de Airflow.

1. Revisar el resultado del evento en la cola:

   ```sql
   SELECT id, queue_id, estado, fecha_registro,
          fecha_ini_exec, fecha_fin_exec,
          SUBSTR(message, 1, 2000) AS mensaje
   FROM padm_queue_events
   WHERE id = 280262701
     AND queue_id = 'gde.alarm';
   ```

   `ESTADO = 1` indica evento procesado; `-1`, fallido; `2`, en proceso; y
   `0`, pendiente. Para esa corrida debe quedar en `1` y con `FECHA_FIN_EXEC`.
   Para buscar errores por hora de ejecución, filtrar por `FECHA_INI_EXEC` y
   `FECHA_FIN_EXEC` del consumidor.

2. Revisar las dos filas de control de carga:

   ```sql
   SELECT proyecto, archivo, registros_cargados, registros_totales,
          inicio, fin, estado, n_errors, mensaje
   FROM padm_carga_control
   WHERE proyecto = 'gde.alarm'
     AND fecha_archivo = TO_DATE('202609281020', 'YYYYMMDDHH24MI')
   ORDER BY archivo;
   ```

   Deben aparecer los archivos `gde_alarm_202609281020_1.json` y
   `gde_alarm_202609281020_2.json`, en estado `CARGADO`, con conteos
   `12214/12214` y `12731/12731`. `N_ERRORS` es un contador histórico que se
   incrementa con los errores y no se reinicia al cargar correctamente; para
   validar esta corrida, usar `ESTADO` y comparar `REGISTROS_CARGADOS` con
   `REGISTROS_TOTALES`.

3. Confirmar alarmas concretas en la tabla final con identificadores tomados
   de las respuestas API de ese intervalo:

   ```sql
   SELECT alarmserialnumber, alarmid, node, firstoccurrence,
          cleartime_fecha, severity
   FROM autin_alarm_gestor
   WHERE alarmserialnumber IN ('SERIAL_API_1', 'SERIAL_API_2')
   ORDER BY alarmserialnumber;
   ```

Los conteos de control validan las filas procesadas desde las respuestas, pero
no prueban por sí solos que cada alarma esté en la tabla final. Para validar
esa parte, comparar los `alarmserialnumber` de la API con el resultado de la
última consulta. Las dos consultas API pueden contener alarmas repetidas, así
que no sumar sus conteos para esperar esa misma cantidad de filas únicas en la
tabla final.

La documentación de Oracle confirma que `RAISE;` relanza la excepción actual
desde un manejador:
[PL/SQL Error Handling](https://docs.oracle.com/en/database/oracle/19/lnpls/raising-exceptions-explicitly.html).
