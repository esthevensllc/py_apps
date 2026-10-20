from __future__ import annotations

import json
import os
import re
import uuid
from contextlib import contextmanager
from functools import wraps
from pathlib import Path

from .models import Notification, normalize_phone, recipient_phone
from .service import TEMPLATES


TABLE = 'AIVO_WHATSAPP_LOG'
MODE = 'PRODUCCION'


class OracleLogError(RuntimeError):
    pass


def oracle_code(error):
    return getattr(error.args[0], 'code', None) if error.args else None


def database_error(operation, error):
    code = oracle_code(error)
    suffix = f' (ORA-{code:05d})' if isinstance(code, int) else ''
    return OracleLogError(f'Fallo Oracle al {operation}{suffix}. No se autoriza otro envío.')


def oracle_read(method):
    @wraps(method)
    def wrapped(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except (OracleLogError, ValueError):
            raise
        except Exception as error:
            raise database_error('leer controles o candidatos', error) from error
    return wrapped


def connect_oracle():
    values = {name: os.getenv('AIVO_ORACLE_' + name.upper(), '') for name in ('user', 'password', 'dsn')}
    missing = [name for name, value in values.items() if not value.strip()]
    if missing:
        raise ValueError('Faltan variables: ' + ', '.join('AIVO_ORACLE_' + name.upper() for name in missing))
    try:
        import cx_Oracle as driver
    except ImportError:
        try:
            import oracledb as driver
        except ImportError as error:
            raise OracleLogError('Instale cx_Oracle o las dependencias de requirements-oracle.txt') from error
        library = os.getenv('AIVO_ORACLE_CLIENT_LIB_DIR')
        if library:
            try:
                driver.init_oracle_client(lib_dir=library)
            except Exception as error:
                raise database_error('inicializar el cliente Oracle', error) from error
    try:
        connection = driver.connect(**values)
        connection.autocommit = False
    except Exception as error:
        raise database_error('conectar', error) from error
    return connection, driver


class OracleRepository:
    """Conexión dedicada. Cada checkpoint se confirma antes de continuar."""

    table = TABLE
    mode = MODE

    def build_payload(self, notification):
        return notification.payload()

    def reservation_extra(self):
        return {}

    def reservation_key(self, values):
        return {key: values[key] for key in ('modo', 'numero_cliente', 'fecha_inicio_averia', 'plantilla')}

    def __init__(self, connection, driver):
        if connection.autocommit:
            raise OracleLogError('La conexión de control debe tener autocommit desactivado')
        self.connection = connection
        self.driver = driver

    @contextmanager
    def cursor(self):
        cursor = self.connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    @oracle_read
    def _constraints(self, table):
        with self.cursor() as cursor:
            cursor.execute('''
                SELECT constraint_name, constraint_type, status, validated, search_condition
                FROM user_constraints WHERE table_name = :table_name
            ''', table_name=table)
            constraints = {row[0]: row[1:] for row in cursor.fetchall()}
            cursor.execute('''
                SELECT constraint_name, column_name, position
                FROM user_cons_columns WHERE table_name = :table_name
                ORDER BY constraint_name, position
            ''', table_name=table)
            columns = {}
            for name, column, _ in cursor.fetchall():
                columns.setdefault(name, []).append(column)
        return constraints, columns

    def validate_safety(self):
        constraints, columns = self._constraints(TABLE)
        required_keys = {
            'PK_AIVO_WA_LOG': ('P', ['ID_ENVIO']),
            'UQ_AIVO_WA_EVENTO': ('U', ['MODO', 'NUMERO_CLIENTE', 'FECHA_INICIO_AVERIA', 'PLANTILLA']),
        }
        for name, (kind, expected_columns) in required_keys.items():
            info = constraints.get(name)
            if not info or info[:3] != (kind, 'ENABLED', 'VALIDATED') or columns.get(name) != expected_columns:
                raise OracleLogError(f'Falta la restricción activa {name}. Se bloquean los envíos.')
        mode = constraints.get('CK_AIVO_WA_MODO')
        condition = re.sub(r'[\s"()]', '', str(mode[3])).upper() if mode else ''
        if (not mode or mode[:3] != ('C', 'ENABLED', 'VALIDATED')
                or condition != "MODOIN'PRUEBA','PRODUCCION'"):
            raise OracleLogError('Falta la restricción de modo. Ejecute la migración a producción.')
        if 'UQ_AIVO_WA_PRUEBA' in constraints or 'CK_AIVO_WA_DESTINO' in constraints:
            raise OracleLogError('Persisten restricciones de prueba. Complete la migración a producción.')

    def candidate_query(self, template_name, limit):
        query = Path(__file__).with_name('sql').joinpath(template_name + '.sql').read_text(encoding='utf-8')
        clean_phone = "REGEXP_REPLACE(TRIM(CAST(src.numero_cliente AS VARCHAR2(64))), '[+ ()-]', '')"
        normalized_phone = (
            f"CASE WHEN LENGTH({clean_phone}) = 9 AND SUBSTR({clean_phone}, 1, 1) = '9' "
            f"THEN '51' || {clean_phone} ELSE {clean_phone} END"
        )
        # Excluir reservas ANTES del límite para que los lotes posteriores avancen.
        query = f'''
            SELECT src.* FROM ({query}) src
            WHERE NOT EXISTS (
                SELECT 1 FROM {TABLE} log
                WHERE log.modo = :modo AND log.plantilla = :plantilla
                  AND log.numero_cliente = {normalized_phone}
                  AND log.fecha_inicio_averia = CAST(src.fecha_inicio_averia AS TIMESTAMP)
                  AND NOT (log.estado = 'ERROR_AUTH' AND log.intentos = 0)
            ) AND ROWNUM <= :limite
        '''
        params = {'modo': MODE, 'plantilla': template_name, 'limite': limit}
        return query, params

    @oracle_read
    def fetch_candidates(self, template_name, limit):
        if template_name not in TEMPLATES or not 1 <= limit <= 1000:
            raise ValueError('Plantilla o límite de consulta inválido')
        query, params = self.candidate_query(template_name, limit)
        with self.cursor() as cursor:
            cursor.arraysize = min(limit, 100)
            cursor.execute(query, params)
            columns = [column[0].lower() for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchmany(limit)]

    def reserve(self, notification: Notification, payload: dict):
        if payload != self.build_payload(notification):
            raise OracleLogError('La solicitud no coincide con el cliente y los datos obtenidos de Oracle')
        record_id = str(uuid.uuid4())
        values = {
            'id_envio': record_id, 'modo': self.mode, 'plantilla': notification.template_name,
            'incidencia': notification.incidencia, 'fecha_inicio_averia': notification.fecha_inicio,
            'fecha_estimada_solucion': notification.fecha_estimada, 'fecha_solucion': notification.fecha_solucion,
            'nro_documento': notification.nro_documento, 'nombre_cliente': notification.nombre_cliente,
            'numero_cliente': notification.numero_cliente, 'numero_destino': payload['to'],
            'solicitud_json': json.dumps(payload, ensure_ascii=False),
        }
        values.update(self.reservation_extra())
        try:
            with self.cursor() as cursor:
                cursor.setinputsizes(
                    solicitud_json=self.driver.DB_TYPE_CLOB,
                    fecha_inicio_averia=self.driver.DB_TYPE_TIMESTAMP,
                    fecha_estimada_solucion=self.driver.DB_TYPE_TIMESTAMP,
                    fecha_solucion=self.driver.DB_TYPE_TIMESTAMP,
                )
                cursor.execute(f'''
                    INSERT INTO {self.table} ({', '.join(values)}, estado, intentos)
                    VALUES ({', '.join(':' + key for key in values)}, 'RESERVADO', 0)
                ''', values)
            self.connection.commit()
        except Exception as error:
            self.connection.rollback()
            if oracle_code(error) == 1:
                return self._reclaim_auth_failure(values)
            raise database_error('reservar el mensaje', error) from error
        return record_id

    def _reclaim_auth_failure(self, values):
        """Solo recupera fallos anteriores a cualquier POST de mensaje."""
        key = self.reservation_key(values)
        where = ' AND '.join(name + ' = :' + name for name in key)
        try:
            with self.cursor() as cursor:
                if 'fecha_inicio_averia' in key:
                    cursor.setinputsizes(fecha_inicio_averia=self.driver.DB_TYPE_TIMESTAMP)
                cursor.execute(f'''
                    SELECT id_envio FROM {self.table}
                    WHERE {where} AND estado = 'ERROR_AUTH' AND intentos = 0
                ''', key)
                existing = cursor.fetchone()
            if existing is None:
                return None
            updates = {name: value for name, value in values.items() if name not in key and name != 'id_envio'}
            params = {**key, **updates, 'existing_id': existing[0]}
            with self.cursor() as cursor:
                cursor.setinputsizes(
                    solicitud_json=self.driver.DB_TYPE_CLOB,
                    fecha_estimada_solucion=self.driver.DB_TYPE_TIMESTAMP,
                    fecha_solucion=self.driver.DB_TYPE_TIMESTAMP,
                    **({'fecha_inicio_averia': self.driver.DB_TYPE_TIMESTAMP} if 'fecha_inicio_averia' in params else {}),
                )
                cursor.execute(f'''
                    UPDATE {self.table} SET
                        {', '.join(name + ' = :' + name for name in updates)},
                        estado = 'RESERVADO', http_status = NULL,
                        respuesta_json = NULL, error_detalle = NULL,
                        fecha_actualizacion = SYSTIMESTAMP
                    WHERE id_envio = :existing_id AND {where}
                      AND estado = 'ERROR_AUTH' AND intentos = 0
                ''', params)
                if cursor.rowcount != 1:
                    self.connection.rollback()
                    return None
            self.connection.commit()
            return existing[0]
        except Exception as error:
            self.connection.rollback()
            raise database_error('recuperar un fallo previo de autenticación', error) from error

    def mark_dispatching(self, record_id):
        self._update(f'''
            UPDATE {self.table} SET estado = 'ENVIANDO', intentos = 1,
                fecha_actualizacion = SYSTIMESTAMP
            WHERE id_envio = :id_envio AND estado = 'RESERVADO' AND intentos = 0
        ''', {'id_envio': record_id})

    def finish(self, record_id, state, expected_state, http_status=None, response_body=None, error=None):
        if state not in ('ACEPTADO', 'ERROR_AUTH', 'ERROR_HTTP', 'INCIERTO'):
            raise ValueError('Estado de resultado inválido')
        self._update(f'''
            UPDATE {self.table} SET estado = :estado, http_status = :http_status,
                respuesta_json = :respuesta_json, error_detalle = :error_detalle,
                fecha_actualizacion = SYSTIMESTAMP
            WHERE id_envio = :id_envio AND estado = :estado_anterior
        ''', {
            'id_envio': record_id, 'estado': state, 'estado_anterior': expected_state,
            'http_status': http_status, 'respuesta_json': response_body,
            'error_detalle': str(error)[:2000] if error else None,
        }, clob=True)

    def _update(self, query, params, clob=False):
        try:
            with self.cursor() as cursor:
                if clob:
                    cursor.setinputsizes(respuesta_json=self.driver.DB_TYPE_CLOB)
                cursor.execute(query, params)
                if cursor.rowcount != 1:
                    raise OracleLogError('La reserva no está en el estado esperado')
            self.connection.commit()
        except Exception as error:
            self.connection.rollback()
            raise database_error('confirmar el log', error) from error


class OracleTestRepository(OracleRepository):
    """Una solicitud por ronda, plantilla y destino; log separado de producción."""

    table = 'AIVO_WHATSAPP_TEST_LOG'
    mode = 'PRUEBA'

    def __init__(self, connection, driver, test_to, test_id):
        super().__init__(connection, driver)
        if not isinstance(test_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', test_id):
            raise ValueError('--test-id debe tener 1 a 64 letras, dígitos, guiones o guiones bajos')
        # Una clave de destino estable evita repetir usando 9 dígitos y luego +51.
        self.test_to = normalize_phone(test_to)
        self.recipient = recipient_phone(test_to)
        self.test_id = test_id

    def build_payload(self, notification):
        payload = notification.payload()
        payload['to'] = self.recipient
        return payload

    def reservation_extra(self):
        return {'id_prueba': self.test_id, 'destino_clave': self.test_to}

    def reservation_key(self, values):
        return {key: values[key] for key in ('id_prueba', 'plantilla', 'destino_clave')}

    def validate_safety(self):
        constraints, columns = self._constraints(self.table)
        for name, kind, expected in (
            ('PK_AIVO_WA_TLOG', 'P', ['ID_ENVIO']),
            ('UQ_AIVO_WA_TEST', 'U', ['ID_PRUEBA', 'PLANTILLA', 'DESTINO_CLAVE']),
        ):
            info = constraints.get(name)
            if not info or info[:3] != (kind, 'ENABLED', 'VALIDATED') or columns.get(name) != expected:
                raise OracleLogError(f'Falta la restricción de pruebas {name}; no se autoriza el envío')
        mode = constraints.get('CK_AIVO_WA_TMODE')
        condition = re.sub(r'[\s"()]', '', str(mode[3])).upper() if mode else ''
        if not mode or mode[:3] != ('C', 'ENABLED', 'VALIDATED') or condition != "MODO='PRUEBA'":
            raise OracleLogError('Falta la restricción de modo PRUEBA')

    def candidate_query(self, template_name, limit):
        base = Path(__file__).with_name('sql').joinpath(template_name + '.sql').read_text(encoding='utf-8')
        params = {'limite': limit}
        return f'SELECT src.* FROM ({base}) src WHERE ROWNUM <= :limite', params
