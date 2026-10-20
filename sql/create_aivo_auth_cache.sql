-- Ejecutar una sola vez en el esquema COMPARTIDO por todos los workers/manuales.
-- No contiene Bearer en claro: TOKEN_ENCRYPTED se cifra con Fernet fuera de Oracle.
CREATE TABLE AIVO_AUTH_GUARD
(
    ACCOUNT_KEY VARCHAR2(64 CHAR) NOT NULL,
    CONSTRAINT PK_AIVO_AUTH_GUARD PRIMARY KEY (ACCOUNT_KEY)
);

COMMENT ON TABLE AIVO_AUTH_GUARD IS
    'Exclusion por cuenta mediante FOR UPDATE NOWAIT. Conexion dedicada durante todo el lote.';

CREATE TABLE AIVO_AUTH_CACHE
(
    ACCOUNT_KEY       VARCHAR2(64 CHAR) NOT NULL,
    TOKEN_ENCRYPTED   CLOB,
    GENERATED_AT      NUMBER(20, 6),
    REFRESH_AT        NUMBER(20, 6),
    EXPIRES_AT        NUMBER(20, 6),
    LAST_AUTH_AT      NUMBER(20, 6),
    NEXT_AUTH_AT      NUMBER(20, 6),
    BLOCKED           NUMBER(1) DEFAULT 0 NOT NULL,
    LAST_ERROR_CODE   VARCHAR2(80 CHAR),
    LOCK_OWNER        VARCHAR2(36 CHAR),
    CONSTRAINT PK_AIVO_AUTH_CACHE PRIMARY KEY (ACCOUNT_KEY),
    CONSTRAINT CK_AIVO_AUTH_BLOCKED CHECK (BLOCKED IN (0, 1))
);

COMMENT ON TABLE AIVO_AUTH_CACHE IS
    'Un token cifrado y una reserva por cuenta Aivo. No borrar para forzar otro login.';
COMMENT ON COLUMN AIVO_AUTH_CACHE.ACCOUNT_KEY IS
    'SHA-256 de endpoint y usuario normalizado; no contiene contraseña ni bearer.';
COMMENT ON COLUMN AIVO_AUTH_CACHE.GENERATED_AT IS 'Epoch UTC en segundos';
COMMENT ON COLUMN AIVO_AUTH_CACHE.NEXT_AUTH_AT IS
    'Control persistente de autenticaciones; se confirma antes del POST /auth.';
