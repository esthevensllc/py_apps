-- Ejecutar una sola vez en el esquema Oracle que posee ambas tablas,
-- antes de desplegar el código Python que inserta TTCREATETIME en GDE_ALARM_AUX.
-- La columna queda nullable: la API puede devolver ttcreatetime = null.

ALTER TABLE GDE_ALARM_AUX
    ADD (TTCREATETIME DATE);

ALTER TABLE AUTIN_ALARM_GESTOR
    ADD (TTCREATETIME DATE);

-- Los registros históricos quedan en NULL. No copiar FIRSTOCCURRENCE:
-- representa la ocurrencia de la alarma, no la creación del ticket.
