from __future__ import annotations

import json
import os
import re
import uuid
from contextlib import contextmanager
from functools import wraps
from pathlib import Path

from .models import Notification, TEST_PHONE
from .service import TEMPLATES


TABLE = 'AIVO_WHATSAPP_LOG'
GUARD_TABLE = 'AIVO_WA_TEST_GUARD'


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
            'UQ_AIVO_WA_EVENTO': ('U', ['NUMERO_CLIENTE', 'FECHA_INICIO_AVERIA', 'PLANTILLA']),
            'UQ_AIVO_WA_PRUEBA': ('U', ['PLANTILLA', 'NUMERO_DESTINO']),
        }
        for name, (kind, expected_columns) in required_keys.items():
            info = constraints.get(name)
            if not info or info[:3] != (kind, 'ENABLED', 'VALIDATED') or columns.get(name) != expected_columns:
                raise OracleLogError(f'Falta la restricción activa {name}. Se bloquean los envíos.')
        destination = constraints.get('CK_AIVO_WA_DESTINO')
        condition = re.sub(r'[\s"()]', '', str(destination[3])).upper() if destination else ''
        if (not destination or destination[:3] != ('C', 'ENABLED', 'VALIDATED')
                or condition != "NUMERO_DESTINO='999876502'"):
            raise OracleLogError('Falta la restricción de destino de prueba. Se bloquean los envíos.')
        guards, guard_columns = self._constraints(GUARD_TABLE)
        primary_key = guards.get('PK_AIVO_WA_GUARD')
        if (not primary_key or primary_key[:3] != ('P', 'ENABLED', 'VALIDATED')
                or guard_columns.get('PK_AIVO_WA_GUARD') != ['PLANTILLA', 'NUMERO_DESTINO']):
            raise OracleLogError('Falta la clave activa de bloqueos de prueba. Se bloquean los envíos.')

    @oracle_read
    def validate_previous_test_messages(self):
        # Confirmación explícita del usuario: ambas plantillas ya fueron recibidas.
        # Si la instalación quedó incompleta, fallar antes de reservar o autenticar.
        with self.cursor() as cursor:
            cursor.execute(f'''
                SELECT plantilla FROM {GUARD_TABLE}
                WHERE numero_destino = :numero_destino
            ''', numero_destino=TEST_PHONE)
            existing = {row[0] for row in cursor.fetchall()}
        if not set(TEMPLATES).issubset(existing):
            raise OracleLogError(
                'Faltan los bloqueos históricos de las dos plantillas ya recibidas. '
                'Complete el script SQL; no se autoriza ningún envío.'
            )

    @oracle_read
    def fetch_candidates(self, template_name, fecha_desde, limit):
        if template_name not in TEMPLATES or not 1 <= limit <= 1000:
            raise ValueError('Plantilla o límite de consulta inválido')
        query = Path(__file__).with_name('sql').joinpath(template_name + '.sql').read_text(encoding='utf-8')
        with self.cursor() as cursor:
            cursor.arraysize = min(limit, 100)
            if template_name == 'averia_diagnosticada':
                cursor.execute(query, fecha_desde=fecha_desde)
            else:
                cursor.execute(query)
            columns = [column[0].lower() for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchmany(limit)]

    def reserve(self, notification: Notification, payload: dict):
        if payload.get('to') != TEST_PHONE:
            raise OracleLogError('El destino debe ser el celular de prueba')
        record_id = str(uuid.uuid4())
        try:
            with self.cursor() as cursor:
                cursor.setinputsizes(
                    solicitud_json=self.driver.DB_TYPE_CLOB,
                    fecha_inicio=self.driver.DB_TYPE_TIMESTAMP,
                    fecha_estimada=self.driver.DB_TYPE_TIMESTAMP,
                    fecha_solucion=self.driver.DB_TYPE_TIMESTAMP,
                )
                cursor.execute(f'''
                    INSERT INTO {TABLE} (
                        id_envio, plantilla, incidencia, fecha_inicio_averia,
                        fecha_estimada_solucion, fecha_solucion, nro_documento,
                        nombre_cliente, numero_cliente, numero_destino,
                        estado, intentos, solicitud_json
                    ) VALUES (
                        :id_envio, :plantilla, :incidencia, :fecha_inicio,
                        :fecha_estimada, :fecha_solucion, :nro_documento,
                        :nombre_cliente, :numero_cliente, :numero_destino,
                        'RESERVADO', 0, :solicitud_json
                    )
                ''', {
                    'id_envio': record_id, 'plantilla': notification.template_name,
                    'incidencia': notification.incidencia, 'fecha_inicio': notification.fecha_inicio,
                    'fecha_estimada': notification.fecha_estimada, 'fecha_solucion': notification.fecha_solucion,
                    'nro_documento': notification.nro_documento, 'nombre_cliente': notification.nombre_cliente,
                    'numero_cliente': notification.numero_cliente, 'numero_destino': TEST_PHONE,
                    'solicitud_json': json.dumps(payload, ensure_ascii=False),
                })
            with self.cursor() as cursor:
                cursor.execute(f'''
                    INSERT INTO {GUARD_TABLE} (plantilla, numero_destino, motivo, id_envio)
                    VALUES (:plantilla, :numero_destino, :motivo, :id_envio)
                ''', {
                    'plantilla': notification.template_name, 'numero_destino': TEST_PHONE,
                    'motivo': 'Reserva permanente previa al POST de prueba', 'id_envio': record_id,
                })
            self.connection.commit()
        except Exception as error:
            self.connection.rollback()
            if oracle_code(error) == 1:
                return None  # La reserva existente bloquea TODOS los estados, incluso errores.
            raise database_error('reservar el mensaje', error) from error
        return record_id

    def mark_dispatching(self, record_id):
        self._update(f'''
            UPDATE {TABLE} SET estado = 'ENVIANDO', intentos = 1,
                fecha_actualizacion = SYSTIMESTAMP
            WHERE id_envio = :id_envio AND estado = 'RESERVADO' AND intentos = 0
        ''', {'id_envio': record_id})

    def finish(self, record_id, state, expected_state, http_status=None, response_body=None, error=None):
        if state not in ('ACEPTADO', 'ERROR_AUTH', 'ERROR_HTTP', 'INCIERTO'):
            raise ValueError('Estado de resultado inválido')
        self._update(f'''
            UPDATE {TABLE} SET estado = :estado, http_status = :http_status,
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
