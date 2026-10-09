SELECT a.incidencia,
       a.fecha_envio AS fecha_inicio_averia,
       a.fecha_solucion,
       a.nro_documento,
       a.nombre_cliente,
       a.numero_origen AS numero_cliente
FROM CLIATC.CI_FIJA_AUDIO_AVERIA@dbl_dwo a
LEFT JOIN remedy_inc_fija c ON a.incidencia = c.incidencia
WHERE a.fecha_solucion >= SYSDATE - (6 / 24)
  AND (a.fecha_solucion IS NOT NULL OR c.estado IN ('CANCELADO', 'RESUELTO', 'CERRADO'))
  AND a.fecha_solucion IS NOT NULL
ORDER BY a.fecha_envio, a.incidencia, a.numero_origen
