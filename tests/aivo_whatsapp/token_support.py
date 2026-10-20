"""Almacén en memoria solo para pruebas unitarias del cliente HTTP."""
import threading
import time
import uuid

from cryptography.fernet import Fernet

from src.aivo_whatsapp.token_cache import TokenCacheError, TokenCoordinator, OracleTokenStore

KEY = Fernet.generate_key()


class MemoryStore:
    def __init__(self):
        self.now = time.time()
        self.state = dict.fromkeys(OracleTokenStore.FIELDS)
        self.state['blocked'] = 0
        self.lock = threading.Lock()
        self.owner = None
        self.history = {}

    def acquire(self, owner):
        if not self.lock.acquire(blocking=False):
            raise TokenCacheError('Otra ejecución está usando esta cuenta')
        self.owner = owner

    def release(self, owner):
        assert self.owner == owner
        self.owner = None
        self.lock.release()

    def read(self, owner):
        assert self.owner == owner and owner is not None
        return dict(self.state, now=self.now)

    def save(self, owner, updates):
        self.read(owner)
        self.state.update(updates)

    def begin_auth(self, owner, minimum_interval, reason='INICIAL'):
        state = self.read(owner)
        if state['blocked']:
            raise TokenCacheError('ALERTA AIVO: cuenta bloqueada', True)
        if (state['next_auth_at'] or 0) > self.now:
            raise TokenCacheError('Autenticación en espera de seguridad')
        self.save(owner, dict(token_encrypted=None, generated_at=None, refresh_at=None,
                              expires_at=None, last_auth_at=self.now,
                              next_auth_at=self.now + minimum_interval, last_error_code=None))
        auth_id = str(uuid.uuid4())
        self.history[auth_id] = dict(estado='INICIADO', motivo=reason)
        return auth_id

    def complete_auth(self, owner, auth_id, updates, info):
        self.save(owner, updates)
        self.history[auth_id].update(info, estado='GENERADO')

    def fail_auth(self, owner, auth_id, error, info=None):
        self.save(owner, dict(token_encrypted=None, blocked=int(getattr(error, 'account_blocked', False)),
                              last_error_code=getattr(error, 'error_code', None) or 'AuthFailure'))
        self.history[auth_id].update(info or {}, estado='GENERADO_SIN_CACHE' if info else 'ERROR_AUTH')


def make_manager(store=None, key=KEY):
    return TokenCoordinator(store or MemoryStore(), key)
