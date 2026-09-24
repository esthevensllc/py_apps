"""Recolección segura de la instantánea UCEPROTECT desde el servidor puente."""

from __future__ import annotations

import os
import posixpath
import shutil
import stat
import tempfile
import time
from pathlib import Path


REQUIRED_DIRECTORIES = (
    'rsync/lvl1',
    'rsync/lvl2',
    'rsync/lvl3',
    'rsync/backscatter',
    'rsync/whitelist',
)


def collect_from_environment() -> None:
    host = _required('UCEPROTECT_BRIDGE_HOST')
    user = _required('UCEPROTECT_BRIDGE_USER')
    password = _required('UCEPROTECT_BRIDGE_PASSWORD')
    remote_storage = _required('UCEPROTECT_BRIDGE_STORAGE_DIR').rstrip('/')
    local_storage = Path(_required('UCEPROTECT_STORAGE_DIR'))
    port = int(os.getenv('UCEPROTECT_BRIDGE_PORT', '22'))
    timeout = int(os.getenv('UCEPROTECT_BRIDGE_TIMEOUT_SECONDS', '180'))
    max_age = int(os.getenv('UCEPROTECT_BRIDGE_MAX_AGE_SECONDS', '86400'))
    known_hosts = Path(
        os.getenv('UCEPROTECT_BRIDGE_KNOWN_HOSTS', '').strip()
        or Path.home() / '.ssh' / 'known_hosts'
    )

    if not 1 <= port <= 65535:
        raise ValueError('UCEPROTECT_BRIDGE_PORT debe estar entre 1 y 65535')
    if timeout <= 0:
        raise ValueError('UCEPROTECT_BRIDGE_TIMEOUT_SECONDS debe ser positivo')
    if max_age <= 0:
        raise ValueError('UCEPROTECT_BRIDGE_MAX_AGE_SECONDS debe ser positivo')
    if not known_hosts.is_file():
        raise RuntimeError(
            f'No existe el archivo de host keys SSH: {known_hosts}'
        )

    try:
        import paramiko
    except ImportError as error:
        raise RuntimeError(
            'No se encontró paramiko en el worker Airflow'
        ) from error

    local_storage.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(
            prefix='.uceprotect-bridge-',
            dir=str(local_storage.parent),
        )
    )
    backup = local_storage.with_name(
        f'.{local_storage.name}.previous-{time.time_ns()}'
    )
    print(
        f'BRIDGE_COLLECT_START host={host} remote={remote_storage} '
        f'destination={local_storage} protocol=sftp'
    )
    try:
        with paramiko.SSHClient() as ssh:
            ssh.load_host_keys(str(known_hosts))
            ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
            ssh.connect(
                hostname=host,
                port=port,
                username=user,
                password=password,
                timeout=timeout,
                auth_timeout=timeout,
                banner_timeout=timeout,
                look_for_keys=False,
                allow_agent=False,
            )
            with ssh.open_sftp() as sftp:
                sftp.get_channel().settimeout(timeout)
                # Fijar la ruta real para que un cambio de symlink `current`
                # durante la copia no mezcle dos instantáneas.
                snapshot = sftp.normalize(remote_storage)
                _copy_snapshot(sftp, snapshot, staging)

        _validate_snapshot(staging, max_age)

        moved_old = False
        if local_storage.exists():
            if not local_storage.is_dir():
                raise RuntimeError(
                    f'La ruta local existe y no es una carpeta: {local_storage}'
                )
            os.replace(local_storage, backup)
            moved_old = True
        try:
            os.replace(staging, local_storage)
        except BaseException:
            if moved_old and backup.exists():
                os.replace(backup, local_storage)
            raise
        if moved_old:
            shutil.rmtree(backup)
        print('BRIDGE_COLLECT_OK snapshot=validated-and-published')
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)


def _copy_snapshot(sftp, remote_root: str, local_root: Path) -> None:
    pending = [(remote_root, local_root)]
    while pending:
        remote_dir, local_dir = pending.pop()
        local_dir.mkdir(parents=True, exist_ok=True)
        for entry in sftp.listdir_attr(remote_dir):
            name = entry.filename
            if name in {'.', '..'} or '/' in name or '\\' in name:
                raise RuntimeError(f'Nombre de archivo no válido en el puente: {name!r}')
            remote_path = posixpath.join(remote_dir, name)
            local_path = local_dir / name
            if stat.S_ISDIR(entry.st_mode):
                pending.append((remote_path, local_path))
            elif stat.S_ISREG(entry.st_mode):
                sftp.get(remote_path, str(local_path))
            else:
                raise RuntimeError(
                    f'El puente contiene un archivo no regular: {remote_path}'
                )


def _validate_snapshot(storage: Path, max_age_seconds: int) -> None:
    for relative in REQUIRED_DIRECTORIES:
        folder = storage / relative
        if not folder.is_dir() or not any(item.is_file() for item in folder.rglob('*')):
            raise RuntimeError(
                f'Instantánea del puente incompleta: falta contenido en {relative}'
            )

    asn_file = storage / 'html' / 'l3charts.html'
    if not asn_file.is_file() or asn_file.stat().st_size == 0:
        raise RuntimeError(
            'Instantánea del puente incompleta: falta html/l3charts.html'
        )

    ready_file = storage / 'READY'
    if not ready_file.is_file():
        raise RuntimeError('Instantánea del puente incompleta: falta READY')
    try:
        published_at = int(ready_file.read_text(encoding='ascii').strip())
    except (OSError, ValueError) as error:
        raise RuntimeError('El marcador READY del puente no es válido') from error
    age_seconds = int(time.time()) - published_at
    if age_seconds < -300:
        raise RuntimeError('El reloj del servidor puente está adelantado')
    if age_seconds > max_age_seconds:
        raise RuntimeError(
            'La instantánea del puente está vencida: '
            f'{age_seconds} segundos; máximo {max_age_seconds}'
        )


def _required(name: str) -> str:
    value = os.getenv(name, '').strip()
    if not value:
        raise RuntimeError(f'Falta configurar {name} en src/ips_spam/.env')
    return value
