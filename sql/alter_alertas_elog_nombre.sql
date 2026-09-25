-- Requerido para almacenar "Servidor Caido HOSTNAME IP" completo.
-- Ejecutar una vez en el esquema Oracle Smart antes de desplegar el DAG.
ALTER TABLE ALERTAS_ELOG
    MODIFY (NOMBRE VARCHAR2(255 CHAR));
