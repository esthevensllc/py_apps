SELECT a.incidencia,
       a.fecha_envio AS fecha_inicio_averia,
       a.fecha_requerida AS fecha_estimada_solucion,
       a.nro_documento,
       a.nombre_cliente,
       a.numero_origen AS numero_cliente
FROM CLIATC.CI_FIJA_AUDIO_AVERIA@dbl_dwo a
LEFT JOIN remedy_inc_fija c ON a.incidencia = c.incidencia
WHERE a.fecha_peticion >= :fecha_desde
  AND (a.fecha_solucion IS NULL OR c.estado NOT IN ('CANCELADO', 'RESUELTO', 'CERRADO'))
  AND a.fecha_requerida IS NOT NULL
  AND (a.fecha_requerida - a.fecha_envio) * 24 <= 5
ORDER BY a.fecha_envio, a.incidencia, a.numero_origen
