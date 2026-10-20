-- Fechas de auditoria en hora Lima (UTC-5). No seleccionar el bearer de la cache.
SELECT id_auth, account_key, motivo, estado, fecha_solicitud, fecha_registro,
       fecha_finalizacion, fecha_renovacion, fecha_vencimiento,
       http_status, error_codigo, error_detalle
FROM AIVO_AUTH_HISTORY
ORDER BY fecha_solicitud DESC;

-- Intentos reservados y tokens recibidos confirmados desde el despliegue.
-- MIGRADO se excluye: es un antecedente, no una solicitud nueva.
-- INICIADO no confirma si /auth llego a recibir la solicitud.
SELECT account_key, TRUNC(fecha_solicitud) AS dia_lima,
       COUNT(*) AS intentos_reservados,
       SUM(CASE WHEN estado IN ('GENERADO', 'GENERADO_SIN_CACHE') THEN 1 ELSE 0 END) AS tokens_recibidos,
       SUM(CASE WHEN estado = 'ERROR_AUTH' THEN 1 ELSE 0 END) AS errores,
       SUM(CASE WHEN estado = 'INICIADO' THEN 1 ELSE 0 END) AS sin_resultado_confirmado
FROM AIVO_AUTH_HISTORY
WHERE estado <> 'MIGRADO'
GROUP BY account_key, TRUNC(fecha_solicitud)
ORDER BY dia_lima DESC, account_key;

-- Datos invalidos observados. Pueden repetirse en distintas ejecuciones.
SELECT id_invalido, id_ejecucion, fecha_registro, modo, id_prueba, plantilla,
       incidencia, numero_cliente, numero_destino, estado, intentos, motivo,
       DBMS_LOB.SUBSTR(datos_origen_json, 4000, 1) AS datos_origen
FROM AIVO_WHATSAPP_INVALID_LOG
ORDER BY fecha_registro DESC;
