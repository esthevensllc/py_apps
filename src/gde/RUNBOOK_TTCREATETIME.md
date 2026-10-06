# Almacenar `ttcreatetime` de GDE

## Orden de despliegue

1. Ejecutar [`sql/add_gde_alarm_ttcreatetime.sql`](../../sql/add_gde_alarm_ttcreatetime.sql)
   en el esquema dueño de `GDE_ALARM_AUX` y `AUTIN_ALARM_GESTOR`.
2. Editar y recompilar el cuerpo de `PK_ALARMS_AUTIN_MN`. En el `INSERT INTO
   AUTIN_ALARM_GESTOR (...) SELECT DISTINCT ... FROM GDE_ALARM_AUX` de
   `SP_ALARM_AUTIN_GESTOR`, añadir `TTCREATETIME` a la lista de columnas destino
   y `A.TTCREATETIME` a la misma posición de la lista `SELECT`. Por ejemplo,
   inmediatamente después de `FIRSTOCCURRENCE` en ambas listas:

   ```sql
   -- Lista INSERT:
   FIRSTOCCURRENCE,
   TTCREATETIME,
   EMSTYPE,

   -- Lista SELECT:
   A.FIRSTOCCURRENCE,
   A.TTCREATETIME,
   A.EMSTYPE,
   ```

   Conservar el resto del procedimiento y su manejo de errores. El paquete
   completo no está versionado en este repositorio, por lo que este paso se
   realiza en la fuente Oracle del ambiente.
3. Confirmar que `USER_ERRORS` no reporte errores de compilación del paquete.
4. Desplegar el código Python y el DAG de GDE.

## Comprobación

```sql
SELECT table_name, column_name, data_type, nullable
FROM user_tab_columns
WHERE table_name IN ('GDE_ALARM_AUX', 'AUTIN_ALARM_GESTOR')
  AND column_name = 'TTCREATETIME'
ORDER BY table_name;
```

Después de una carga nueva, comparar el `ttcreatetime` de una alarma de la API
con la tabla final:

```sql
SELECT alarmserialnumber, firstoccurrence, ttcreatetime, severity
FROM autin_alarm_gestor
WHERE alarmserialnumber = 'SERIAL_DE_LA_API';
```

Las filas anteriores a este cambio conservarán `TTCREATETIME = NULL` hasta que
sean recargadas desde la API. `TTCREATETIME = NULL` es un valor posible de la
fuente y no debe sustituirse con `FIRSTOCCURRENCE`.
