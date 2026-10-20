-- Ejecutar UNA SOLA VEZ en el esquema compartido que ya tiene AIVO_AUTH_CACHE.
-- Pausar el DAG y las pruebas manuales antes de migrar y actualizar el codigo.
-- No recrear tablas ni modificar tokens, claves, bloqueos o tiempos de renovacion.
ALTER TABLE AIVO_AUTH_CACHE ADD (FECHA_REGISTRO DATE);

-- GENERATED_AT contiene segundos UTC desde epoch. Oracle DATE guardara Lima
-- (UTC-5). Recuperar la fecha conocida sin generar otro token ni usar SYSDATE
-- como fecha ficticia para los registros existentes.
UPDATE AIVO_AUTH_CACHE
SET FECHA_REGISTRO = DATE '1970-01-01' + (GENERATED_AT / 86400) - (5 / 24)
WHERE FECHA_REGISTRO IS NULL AND GENERATED_AT IS NOT NULL;

COMMENT ON COLUMN AIVO_AUTH_CACHE.FECHA_REGISTRO IS
    'Registro del ultimo token obtenido correctamente, hora Lima UTC-5. Cambia al renovar, no al reutilizar.';

COMMIT;
