-- Ejecutar una sola vez en el MISMO esquema usado por el proceso de envío.
-- Modo de prueba: máximo un intento por plantilla al número 999876502.
-- No borrar registros ni deshabilitar las restricciones: permiten el bloqueo
-- incluso si el POST terminó con timeout o el proceso se interrumpió.
CREATE TABLE AIVO_WHATSAPP_LOG
(
    ID_ENVIO                  VARCHAR2(36 CHAR)             NOT NULL,
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
        (NUMERO_CLIENTE, FECHA_INICIO_AVERIA, PLANTILLA),
    CONSTRAINT UQ_AIVO_WA_PRUEBA UNIQUE (PLANTILLA, NUMERO_DESTINO),
    CONSTRAINT CK_AIVO_WA_DESTINO CHECK (NUMERO_DESTINO = '999876502'),
    CONSTRAINT CK_AIVO_WA_PLANTILLA CHECK
        (PLANTILLA IN ('averia_diagnosticada', 'averia_solucionada')),
    CONSTRAINT CK_AIVO_WA_ESTADO CHECK
        (ESTADO IN ('RESERVADO', 'ENVIANDO', 'ACEPTADO', 'ERROR_AUTH',
                    'ERROR_HTTP', 'INCIERTO')),
    CONSTRAINT CK_AIVO_WA_INTENTOS CHECK (INTENTOS IN (0, 1))
);

COMMENT ON TABLE AIVO_WHATSAPP_LOG IS
    'Reserva persistente y resultado de envíos Aivo. Prueba: uno por plantilla.';
COMMENT ON COLUMN AIVO_WHATSAPP_LOG.NUMERO_CLIENTE IS
    'Celular del origen normalizado. Forma parte de la clave de la avería.';
COMMENT ON COLUMN AIVO_WHATSAPP_LOG.NUMERO_DESTINO IS
    'Destino real del POST. Fijado a 999876502 durante la prueba.';
COMMENT ON COLUMN AIVO_WHATSAPP_LOG.INTENTOS IS
    'Se cambia a 1 y se confirma ANTES del POST. No se permite un segundo intento.';
COMMENT ON COLUMN AIVO_WHATSAPP_LOG.ESTADO IS
    'Todos los estados bloquean futuros envíos. ACEPTADO no confirma entrega.';

-- Control adicional del número de prueba, independiente del cliente origen.
-- Se crea vacío: el proceso inserta la reserva antes del primer POST.
CREATE TABLE AIVO_WA_TEST_GUARD
(
    PLANTILLA          VARCHAR2(40 CHAR)                  NOT NULL,
    NUMERO_DESTINO     VARCHAR2(20 CHAR)                  NOT NULL,
    MOTIVO             VARCHAR2(256 CHAR)                 NOT NULL,
    ID_ENVIO           VARCHAR2(36 CHAR),
    FECHA_REGISTRO     TIMESTAMP(6) WITH TIME ZONE
                       DEFAULT SYSTIMESTAMP               NOT NULL,
    CONSTRAINT PK_AIVO_WA_GUARD PRIMARY KEY (PLANTILLA, NUMERO_DESTINO),
    CONSTRAINT FK_AIVO_WA_GUARD_LOG FOREIGN KEY (ID_ENVIO)
        REFERENCES AIVO_WHATSAPP_LOG (ID_ENVIO),
    CONSTRAINT CK_AIVO_WA_GUARD_DEST CHECK (NUMERO_DESTINO = '999876502'),
    CONSTRAINT CK_AIVO_WA_GUARD_TPL CHECK
        (PLANTILLA IN ('averia_diagnosticada', 'averia_solucionada'))
);

-- Sin INSERT iniciales. Primera ejecución: un intento por plantilla.
-- Ejecuciones posteriores: las reservas existentes impiden repetirlo.
COMMIT;
