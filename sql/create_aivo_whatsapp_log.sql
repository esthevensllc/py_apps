-- Ejecutar una sola vez en el MISMO esquema usado por el proceso de envío.
-- Instalación nueva en producción. Para tablas existentes usar la migración.
-- No borrar registros ni deshabilitar las restricciones: permiten el bloqueo
-- incluso si el POST terminó con timeout o el proceso se interrumpió.
CREATE TABLE AIVO_WHATSAPP_LOG
(
    ID_ENVIO                  VARCHAR2(36 CHAR)             NOT NULL,
    MODO                      VARCHAR2(12 CHAR)
                              DEFAULT 'PRODUCCION'          NOT NULL,
    PLANTILLA                 VARCHAR2(40 CHAR)             NOT NULL,
    INCIDENCIA                VARCHAR2(128 CHAR)            NOT NULL,
    FECHA_INICIO_AVERIA        TIMESTAMP(6)                  NOT NULL,
    FECHA_ESTIMADA_SOLUCION    TIMESTAMP(6),
    FECHA_SOLUCION             TIMESTAMP(6),
    NRO_DOCUMENTO             VARCHAR2(64 CHAR),
    NOMBRE_CLIENTE            VARCHAR2(256 CHAR)            NOT NULL,
    NUMERO_CLIENTE            VARCHAR2(20 CHAR)             NOT NULL,
    NUMERO_DESTINO            VARCHAR2(20 CHAR)             NOT NULL,
    ESTADO                    VARCHAR2(20 CHAR)             NOT NULL,
    INTENTOS                  NUMBER(1) DEFAULT 0           NOT NULL,
    HTTP_STATUS               NUMBER(3),
    SOLICITUD_JSON            CLOB                          NOT NULL,
    RESPUESTA_JSON            CLOB,
    ERROR_DETALLE             VARCHAR2(2000 CHAR),
    FECHA_REGISTRO            TIMESTAMP(6) WITH TIME ZONE
                              DEFAULT SYSTIMESTAMP          NOT NULL,
    FECHA_ACTUALIZACION        TIMESTAMP(6) WITH TIME ZONE
                              DEFAULT SYSTIMESTAMP          NOT NULL,
    CONSTRAINT PK_AIVO_WA_LOG PRIMARY KEY (ID_ENVIO),
    CONSTRAINT UQ_AIVO_WA_EVENTO UNIQUE
        (MODO, NUMERO_CLIENTE, FECHA_INICIO_AVERIA, PLANTILLA),
    CONSTRAINT CK_AIVO_WA_MODO CHECK (MODO IN ('PRUEBA', 'PRODUCCION')),
    CONSTRAINT CK_AIVO_WA_PLANTILLA CHECK
        (PLANTILLA IN ('averia_diagnosticada', 'averia_solucionada')),
    CONSTRAINT CK_AIVO_WA_ESTADO CHECK
        (ESTADO IN ('RESERVADO', 'ENVIANDO', 'ACEPTADO', 'ERROR_AUTH',
                    'ERROR_HTTP', 'INCIERTO')),
    CONSTRAINT CK_AIVO_WA_INTENTOS CHECK (INTENTOS IN (0, 1))
);

COMMENT ON TABLE AIVO_WHATSAPP_LOG IS
    'Reservas y respuestas Aivo. Clave por modo, cliente, inicio y plantilla.';
COMMENT ON COLUMN AIVO_WHATSAPP_LOG.NUMERO_CLIENTE IS
    'Celular del origen normalizado. Forma parte de la clave de la avería.';
COMMENT ON COLUMN AIVO_WHATSAPP_LOG.NUMERO_DESTINO IS
    'Celular real enviado en el POST; datos del origen Oracle en PRODUCCION.';
COMMENT ON COLUMN AIVO_WHATSAPP_LOG.INTENTOS IS
    'Se cambia a 1 y se confirma ANTES del POST. No se permite un segundo intento.';
COMMENT ON COLUMN AIVO_WHATSAPP_LOG.ESTADO IS
    'Todos los estados bloquean futuros envíos. ACEPTADO no confirma entrega.';

COMMIT;
