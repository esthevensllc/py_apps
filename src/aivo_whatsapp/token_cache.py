"""Bearer compartido, cifrado y coordinado por cuenta en Oracle."""
from __future__ import annotations

import hashlib
import datetime as dt
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field

from cryptography.fernet import Fernet, InvalidToken


class TokenCacheError(RuntimeError):
    def __init__(self, message, account_blocked=False):
        super().__init__(message)
        self.account_blocked = account_blocked


@dataclass(frozen=True)
class TokenGrant:
    token: str = field(repr=False)
    expires_at: float | None = None
    http_status: int | None = None


def lima_date(epoch):
    return dt.datetime.fromtimestamp(epoch, dt.timezone(dt.timedelta(hours=-5))).replace(tzinfo=None, microsecond=0)


class OracleTokenStore:
    TABLE = 'AIVO_AUTH_CACHE'
    FIELDS = (
        'token_encrypted', 'generated_at', 'refresh_at', 'expires_at',
        'last_auth_at', 'next_auth_at', 'blocked', 'last_error_code', 'lock_owner', 'fecha_registro',
    )

    def __init__(self, connection_factory, account_key):
        self.factory = connection_factory
        self.account_key = account_key
        self.connection = None
        self.driver = None
        self.guard = None

    def _acquire_guard(self):
        # Conexión separada: este bloqueo REAL de fila no se libera al guardar
        # el token ni vence mientras una llamada HTTP siga pendiente.
        self.guard, _ = self.factory()
        if self.guard.autocommit:
            raise TokenCacheError('La conexión de exclusión debe tener autocommit desactivado')
        cursor = self.guard.cursor()
        try:
            cursor.execute('SELECT account_key FROM AIVO_AUTH_GUARD WHERE account_key = :account_key',
                           account_key=self.account_key)
            if cursor.fetchone() is None:
                try:
                    cursor.execute('INSERT INTO AIVO_AUTH_GUARD (account_key) VALUES (:account_key)',
                                   account_key=self.account_key)
                    self.guard.commit()
                except Exception as error:
                    self.guard.rollback()
                    if not error.args or getattr(error.args[0], 'code', None) != 1:
                        raise
            cursor.execute('SELECT account_key FROM AIVO_AUTH_GUARD WHERE account_key = :account_key FOR UPDATE NOWAIT',
                           account_key=self.account_key)
            if cursor.fetchone() is None:
                raise TokenCacheError('Falta la fila de exclusión Aivo')
        except Exception as error:
            raise TokenCacheError('No se obtuvo la exclusión de cuenta Aivo. Otra ejecución está activa o falta AIVO_AUTH_GUARD.') from error
        finally:
            cursor.close()

    @contextmanager
    def _transaction(self):
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except TokenCacheError:
            self.connection.rollback()
            raise
        except Exception as error:
            self.connection.rollback()
            code = getattr(error.args[0], 'code', None) if error.args else None
            suffix = f' ORA-{code:05d}' if isinstance(code, int) else ''
            raise TokenCacheError(f'No se pudo acceder al control compartido de Aivo.{suffix}') from error
        finally:
            cursor.close()

    @staticmethod
    def _now(cursor):
        # El reloj de Oracle evita diferencias de hora entre workers.
        cursor.execute("SELECT (CAST(SYS_EXTRACT_UTC(SYSTIMESTAMP) AS DATE) - DATE '1970-01-01') * 86400 FROM dual")
        return float(cursor.fetchone()[0])

    def _locked(self, cursor, owner=None):
        if owner is not None:
            # Confirmar también que la conexión que conserva la exclusión sigue
            # viva. Los tiempos de una consulta Oracle no deben liberar la cuenta.
            guard_cursor = self.guard.cursor()
            try:
                guard_cursor.execute('SELECT account_key FROM AIVO_AUTH_GUARD WHERE account_key = :account_key FOR UPDATE NOWAIT',
                                     account_key=self.account_key)
                if guard_cursor.fetchone() is None:
                    raise TokenCacheError('Se perdió la exclusión de la cuenta Aivo')
            finally:
                guard_cursor.close()
        cursor.execute(f'''SELECT {', '.join(self.FIELDS)} FROM {self.TABLE}
            WHERE account_key = :account_key FOR UPDATE WAIT 5''', account_key=self.account_key)
        row = cursor.fetchone()
        if row is None:
            raise TokenCacheError('Falta la fila de control de autenticación')
        state = dict(zip(self.FIELDS, row))
        if hasattr(state['token_encrypted'], 'read'):
            state['token_encrypted'] = state['token_encrypted'].read()
        state['now'] = self._now(cursor)
        if owner is not None and state['lock_owner'] != owner:
            raise TokenCacheError('Se perdió la reserva de la cuenta Aivo; no se autoriza otra llamada')
        return state

    def _write(self, cursor, updates):
        sizes = {}
        if 'token_encrypted' in updates:
            sizes['token_encrypted'] = self.driver.DB_TYPE_CLOB
        if 'fecha_registro' in updates:
            sizes['fecha_registro'] = self.driver.DB_TYPE_DATE
        if sizes:
            cursor.setinputsizes(**sizes)
        cursor.execute(f'''UPDATE {self.TABLE}
            SET {', '.join(name + ' = :' + name for name in updates)}
            WHERE account_key = :account_key''', {**updates, 'account_key': self.account_key})
        if cursor.rowcount != 1:
            raise TokenCacheError('No se pudo confirmar el estado de autenticación')

    def acquire(self, owner):
        try:
            self._acquire_guard()
            self.connection, self.driver = self.factory()
            if self.connection.autocommit:
                raise TokenCacheError('La conexión de autenticación debe tener autocommit desactivado')
            cursor = self.connection.cursor()
            try:
                cursor.execute(f'INSERT INTO {self.TABLE} (account_key) VALUES (:account_key)', account_key=self.account_key)
                self.connection.commit()
            except Exception as error:
                self.connection.rollback()
                if not error.args or getattr(error.args[0], 'code', None) != 1:
                    raise TokenCacheError('Cree AIVO_AUTH_CACHE antes de autenticar') from error
            finally:
                cursor.close()
            with self._transaction() as cursor:
                state = self._locked(cursor)
                # El bloqueo real ya fue adquirido: una marca de un proceso
                # interrumpido no impide recuperarse ni habilita otro login.
                self._write(cursor, {'lock_owner': owner})
        except Exception:
            if self.connection is not None:
                self.connection.close()
                self.connection = None
            if self.guard is not None:
                self.guard.rollback()
                self.guard.close()
                self.guard = None
            raise

    def release(self, owner):
        try:
            with self._transaction() as cursor:
                cursor.execute(f'''UPDATE {self.TABLE} SET lock_owner = NULL
                    WHERE account_key = :account_key AND lock_owner = :owner''',
                    account_key=self.account_key, owner=owner)
        finally:
            try:
                self.connection.close()
                self.connection = None
            finally:
                self.guard.rollback()
                self.guard.close()
                self.guard = None

    def read(self, owner):
        with self._transaction() as cursor:
            state = self._locked(cursor, owner)
            return state

    def save(self, owner, updates):
        with self._transaction() as cursor:
            state = self._locked(cursor, owner)
            self._write(cursor, updates)

    def begin_auth(self, owner, minimum_interval, reason='INICIAL'):
        auth_id = str(uuid.uuid4())
        with self._transaction() as cursor:
            state = self._locked(cursor, owner)
            if state['blocked']:
                raise TokenCacheError('ALERTA AIVO: cuenta bloqueada. Requiere revisión del proveedor.', True)
            if float(state['next_auth_at'] or 0) > state['now']:
                raise TokenCacheError('Autenticación en espera de seguridad; no se permiten inicios de sesión consecutivos')
            # Confirmar ANTES de /auth: un timeout o una interrupción tampoco
            # permite que otro proceso haga inmediatamente otro inicio de sesión.
            self._write(cursor, {
                'token_encrypted': None, 'generated_at': None, 'refresh_at': None, 'expires_at': None,
                'last_auth_at': state['now'], 'next_auth_at': state['now'] + minimum_interval,
                'last_error_code': None,
            })
            cursor.setinputsizes(fecha_solicitud=self.driver.DB_TYPE_DATE)
            cursor.execute('''INSERT INTO AIVO_AUTH_HISTORY
                (id_auth, account_key, motivo, estado, fecha_solicitud)
                VALUES (:id_auth, :account_key, :motivo, 'INICIADO', :fecha_solicitud)''',
                id_auth=auth_id, account_key=self.account_key, motivo=reason, fecha_solicitud=lima_date(state['now']))
        return auth_id

    def complete_auth(self, owner, auth_id, updates, info):
        with self._transaction() as cursor:
            self._locked(cursor, owner)
            self._write(cursor, updates)
            self._finish_history(cursor, auth_id, 'GENERADO', info, None, None)

    def fail_auth(self, owner, auth_id, error, info=None):
        with self._transaction() as cursor:
            state = self._locked(cursor, owner)
            code = getattr(error, 'error_code', None) or 'AuthFailure'
            self._write(cursor, {
                'token_encrypted': None,
                'blocked': 1 if getattr(error, 'account_blocked', False) else 0,
                'last_error_code': code,
            })
            detail = str(error) if isinstance(error, TokenCacheError) or hasattr(error, 'http_status') else type(error).__name__
            info = dict(info or {}, fecha_finalizacion=lima_date(state['now']))
            info.setdefault('http_status', getattr(error, 'http_status', None))
            self._finish_history(cursor, auth_id, 'GENERADO_SIN_CACHE' if info.get('token_fingerprint') else 'ERROR_AUTH',
                                 info, code, detail[:2000])

    def _finish_history(self, cursor, auth_id, status, info, code, detail):
        values = {name: info.get(name) for name in (
            'token_fingerprint', 'fecha_registro', 'fecha_renovacion', 'fecha_vencimiento',
            'fecha_finalizacion', 'http_status',
        )}
        cursor.setinputsizes(**{name: self.driver.DB_TYPE_DATE for name in values if name.startswith('fecha_')})
        cursor.execute('''UPDATE AIVO_AUTH_HISTORY SET estado = :estado,
            token_fingerprint = :token_fingerprint, fecha_registro = :fecha_registro,
            fecha_renovacion = :fecha_renovacion, fecha_vencimiento = :fecha_vencimiento,
            fecha_finalizacion = :fecha_finalizacion, http_status = :http_status,
            error_codigo = :error_codigo, error_detalle = :error_detalle
            WHERE id_auth = :id_auth AND account_key = :account_key AND estado = 'INICIADO' ''',
            dict(values, estado=status, error_codigo=code, error_detalle=detail, id_auth=auth_id, account_key=self.account_key))
        if cursor.rowcount != 1:
            raise TokenCacheError('No se pudo confirmar el historial de autenticación')


class TokenCoordinator:
    """Una sola renovación por cuenta, sin reintentos consecutivos de /auth."""
    def __init__(self, store, encryption_key, refresh_seconds=9 * 3600, minimum_interval=900):
        try:
            self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        except (ValueError, TypeError) as error:
            raise TokenCacheError('AIVO_TOKEN_ENCRYPTION_KEY debe ser una clave Fernet válida y compartida por los workers') from error
        self.store = store
        self.refresh_seconds = refresh_seconds
        self.minimum_interval = minimum_interval
        self.mutex = threading.RLock()
        self.owner = None

    @contextmanager
    def session(self):
        with self.mutex:
            outermost = self.owner is None
            if outermost:
                owner = str(uuid.uuid4())
                self.store.acquire(owner)
                self.owner = owner
            try:
                yield self
            finally:
                if outermost:
                    try:
                        self.store.release(self.owner)
                    finally:
                        self.owner = None

    def touch(self):
        return self.store.read(self.owner)

    def _decrypt(self, state):
        encrypted = state['token_encrypted']
        if not encrypted:
            return None
        try:
            return self.cipher.decrypt(encrypted.encode()).decode()
        except (InvalidToken, UnicodeError) as error:
            raise TokenCacheError('No se pudo descifrar el token; verifique la clave compartida. No se vuelve a autenticar.') from error

    def get(self, issuer, rejected_token=None):
        with self.session():
            state = self.touch()
            if state['blocked']:
                raise TokenCacheError('ALERTA AIVO: cuenta bloqueada en el control compartido. No se solicita otro token.', True)
            token = self._decrypt(state)
            valid = token and float(state['expires_at'] or 0) > state['now'] + 30
            fresh = valid and float(state['refresh_at'] or 0) > state['now']
            if fresh and (rejected_token is None or token != rejected_token):
                return token
            if rejected_token is not None and token == rejected_token:
                self.reject(rejected_token)
            reason = ('HTTP_401' if rejected_token is not None else
                      'RECUPERACION' if not token and state['last_auth_at'] is not None else
                      'INICIAL' if not token else 'VENCIMIENTO' if not valid else 'RENOVACION_PREVENTIVA')
            auth_id = self.store.begin_auth(self.owner, self.minimum_interval, reason)
            info = None
            try:
                grant = issuer()
                now = self.touch()['now']
                expires_at = min(now + 10 * 3600, grant.expires_at or now + 10 * 3600)
                if expires_at <= now + 30:
                    raise TokenCacheError('El token recibido ya está vencido o próximo a vencer')
                info = {
                    'token_fingerprint': hashlib.sha256(grant.token.encode()).hexdigest(),
                    'fecha_registro': lima_date(now), 'fecha_finalizacion': lima_date(now),
                    'fecha_renovacion': lima_date(min(now + self.refresh_seconds, expires_at - 300)),
                    'fecha_vencimiento': lima_date(expires_at), 'http_status': grant.http_status,
                }
                self.store.complete_auth(self.owner, auth_id, {
                    'token_encrypted': self.cipher.encrypt(grant.token.encode()).decode(),
                    'generated_at': now, 'expires_at': expires_at,
                    'refresh_at': min(now + self.refresh_seconds, expires_at - 300),
                    # Oracle DATE no incluye zona: guardar hora de Lima (UTC-5),
                    # usando el mismo instante de Oracle que GENERATED_AT.
                    'fecha_registro': info['fecha_registro'],
                    'blocked': 0, 'last_error_code': None,
                }, info)
                return grant.token
            except Exception as error:
                self.store.fail_auth(self.owner, auth_id, error, info)
                raise

    def reject(self, rejected_token):
        """No volver a usar un token rechazado, ni durante la espera de seguridad."""
        with self.session():
            state = self.touch()
            if not state['blocked'] and self._decrypt(state) == rejected_token:
                self.store.save(self.owner, {
                    'token_encrypted': None, 'generated_at': None, 'refresh_at': None, 'expires_at': None,
                    'last_error_code': 'TokenRejected401',
                })

    def block(self, error_code='UserBlockedException'):
        with self.session():
            self.store.save(self.owner, {'blocked': 1, 'token_encrypted': None, 'last_error_code': error_code})

    def status(self):
        with self.session():
            state = self.touch()
            return {key: state[key] for key in (
                'generated_at', 'refresh_at', 'expires_at', 'last_auth_at', 'next_auth_at', 'blocked', 'last_error_code',
            )}


def build_token_coordinator(settings):
    # Importación diferida: consultar/importar un DAG no abre conexiones.
    from .repository import connect_oracle
    account_key = hashlib.sha256(('https://gateway.aivo.co/api/v1/auth\0' + settings.user.strip().casefold()).encode()).hexdigest()
    store = OracleTokenStore(connect_oracle, account_key)
    return TokenCoordinator(store, settings.token_encryption_key,
                            settings.token_refresh_hours * 3600, settings.auth_min_interval)
