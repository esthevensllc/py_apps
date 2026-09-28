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

### 1. Hacer que `SP_ALARM_AUTIN_GESTOR` propague la excepción

Reemplazar sus dos manejadores actuales (el grupo de errores específicos y
`WHEN OTHERS`) por uno que revierta y relance el error. La notificación se
envía una sola vez en `SP_ALARM_AUTIN_LOAD`:

```sql
EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    RAISE;
END SP_ALARM_AUTIN_GESTOR;
```

### 2. Notificar en `SP_ALARM_AUTIN_LOAD` y devolver el error al cliente

Reemplazar sus manejadores actuales por este bloque. El manejador interior
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
4. Confirmar que el evento GDE quede con `estado = -1`, que llegue la
   notificación y que el log del consumidor contenga el error Oracle original.
5. En producción, revisar que una ejecución correcta siga marcando el evento
   como procesado.

La documentación de Oracle confirma que `RAISE;` relanza la excepción actual
desde un manejador:
[PL/SQL Error Handling](https://docs.oracle.com/en/database/oracle/19/lnpls/raising-exceptions-explicitly.html).
