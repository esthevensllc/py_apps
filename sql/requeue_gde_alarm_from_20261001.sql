-- Recarga GDE desde el 01/10/2026 00:00 (America/Lima).
-- Ejecutar en el esquema que contiene PADM_QUEUE_EVENTS.
-- Requiere el consumidor GDE que reconoce backfill_id y consulta 180 minutos.
-- Cada evento: un GET ttcreatetime de 180 min y tres GET de limpiezas de 60 min.
-- La fecha del evento es el FIN de la ventana de API, no su inicio.
-- Prioridad -1: los eventos normales del DAG (prioridad 0) van primero.

DECLARE
    v_inicio       DATE := TO_DATE('2026-10-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS');
    v_ahora_lima   DATE := CAST(SYSTIMESTAMP AT TIME ZONE 'America/Lima' AS DATE);
    v_fin          DATE;
    v_ancla        DATE;
    v_ultima_ancla DATE;
    v_columnas     NUMBER;
    v_incompatibles NUMBER;
    v_publicados   NUMBER := 0;
    v_omitidos     NUMBER := 0;
    v_id           VARCHAR2(40) := 'gde-20261001-ttcreatetime';

    PROCEDURE publicar(p_ancla DATE) IS
        v_ya_publicado NUMBER;
        v_msg CLOB;
    BEGIN
        SELECT COUNT(*) INTO v_ya_publicado
        FROM PADM_QUEUE_EVENTS
        WHERE QUEUE_ID = 'gde.alarm'
          AND JSON_VALUE(MSG_BODY, '$.backfill_id') = v_id
          AND JSON_VALUE(MSG_BODY, '$.fec_ini') =
              TO_CHAR(p_ancla, 'YYYY-MM-DD HH24:MI');

        IF v_ya_publicado = 0 THEN
            v_msg := JSON_OBJECT(
                'fec_ini' VALUE TO_CHAR(p_ancla, 'YYYY-MM-DD HH24:MI'),
                'format' VALUE 'mxm',
                'granularity' VALUE 180,
                'backfill_id' VALUE v_id
                RETURNING CLOB
            );

            INSERT INTO PADM_QUEUE_EVENTS
                (QUEUE_ID, MSG_BODY, PRIORIDAD, FECHA_REGISTRO)
            VALUES ('gde.alarm', v_msg, -1, SYSDATE);
            v_publicados := v_publicados + 1;
        ELSE
            v_omitidos := v_omitidos + 1;
        END IF;
    END publicar;
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

    v_fin := TRUNC(v_ahora_lima, 'HH24')
          + FLOOR(TO_NUMBER(TO_CHAR(v_ahora_lima, 'MI')) / 10) * 10 / 1440;

    IF v_fin <= v_inicio THEN
        RAISE_APPLICATION_ERROR(-20002, 'Rango de recarga vacio');
    END IF;

    -- 03:00 consulta 00:00-03:00, 06:00 consulta 03:00-06:00, etc.
    v_ancla := v_inicio + 180 / 1440;
    WHILE v_ancla <= v_fin LOOP
        publicar(v_ancla);
        v_ultima_ancla := v_ancla;
        v_ancla := v_ancla + 180 / 1440;
    END LOOP;

    -- La ultima ventana solapa como maximo 180 minutos y llega hasta ahora.
    IF v_ultima_ancla IS NULL OR v_ultima_ancla < v_fin THEN
        publicar(v_fin);
    END IF;

    DBMS_OUTPUT.PUT_LINE('Hasta: ' || TO_CHAR(v_fin, 'YYYY-MM-DD HH24:MI:SS'));
    DBMS_OUTPUT.PUT_LINE('Eventos nuevos: ' || v_publicados
        || '; ya publicados: ' || v_omitidos);
    COMMIT;
END;
/
