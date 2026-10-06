-- Piloto: una sola ventana GDE de 180 minutos, 06/10/2026 09:00-12:00 Lima.
-- El ancla 12:00 cubre la alarma con ttcreatetime 09:09:37.
-- Un GET ttcreatetime de 180 min y tres GET de limpiezas de 60 min.
-- Ejecutar despues de desplegar el consumidor que reconoce backfill_id.
-- Este evento usa el mismo identificador que la recarga total: el script
-- de recarga completa no lo volvera a publicar.

DECLARE
    v_ancla         VARCHAR2(16) := '2026-10-06 12:00';
    v_id            VARCHAR2(40) := 'gde-20261001-ttcreatetime';
    v_columnas      NUMBER;
    v_incompatibles NUMBER;
    v_existentes    NUMBER;
    v_msg           CLOB;
BEGIN
    SELECT COUNT(*) INTO v_columnas
    FROM USER_TAB_COLUMNS
    WHERE TABLE_NAME IN ('GDE_ALARM_AUX', 'AUTIN_ALARM_GESTOR')
      AND COLUMN_NAME = 'TTCREATETIME';

    IF v_columnas <> 2 THEN
        RAISE_APPLICATION_ERROR(-20001,
            'Falta TTCREATETIME en GDE_ALARM_AUX o AUTIN_ALARM_GESTOR');
    END IF;

    SELECT COUNT(*) INTO v_incompatibles
    FROM PADM_QUEUE_EVENTS
    WHERE QUEUE_ID = 'gde.alarm'
      AND JSON_VALUE(MSG_BODY, '$.backfill_id') = v_id
      AND NVL(JSON_VALUE(MSG_BODY, '$.granularity' RETURNING NUMBER), -1) <> 180;

    IF v_incompatibles > 0 THEN
        RAISE_APPLICATION_ERROR(-20003,
            'Ya hay eventos de esta recarga con granularidad distinta de 180');
    END IF;

    SELECT COUNT(*) INTO v_existentes
    FROM PADM_QUEUE_EVENTS
    WHERE QUEUE_ID = 'gde.alarm'
      AND JSON_VALUE(MSG_BODY, '$.backfill_id') = v_id
      AND JSON_VALUE(MSG_BODY, '$.fec_ini') = v_ancla;

    IF v_existentes = 0 THEN
        v_msg := JSON_OBJECT(
            'fec_ini' VALUE v_ancla,
            'format' VALUE 'mxm',
            'granularity' VALUE 180,
            'backfill_id' VALUE v_id
            RETURNING VARCHAR2(4000)
        );

        INSERT INTO PADM_QUEUE_EVENTS
            (QUEUE_ID, MSG_BODY, PRIORIDAD, FECHA_REGISTRO)
        VALUES ('gde.alarm', v_msg, -1, SYSDATE);
        DBMS_OUTPUT.PUT_LINE('Piloto publicado: ' || v_ancla);
    ELSE
        DBMS_OUTPUT.PUT_LINE('Piloto ya publicado: ' || v_ancla);
    END IF;

    COMMIT;
END;
/
