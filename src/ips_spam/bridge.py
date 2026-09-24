"""Recolección segura de la instantánea UCEPROTECT desde el servidor puente."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
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
    remote_storage = _required('UCEPROTECT_BRIDGE_STORAGE_DIR').rstrip('/')
    local_storage = Path(_required('UCEPROTECT_STORAGE_DIR'))
    port = int(os.getenv('UCEPROTECT_BRIDGE_PORT', '22'))
    timeout = int(os.getenv('UCEPROTECT_BRIDGE_TIMEOUT_SECONDS', '180'))
    max_age = int(os.getenv('UCEPROTECT_BRIDGE_MAX_AGE_SECONDS', '86400'))
    identity_file = os.getenv('UCEPROTECT_BRIDGE_SSH_KEY', '').strip()
    known_hosts = os.getenv('UCEPROTECT_BRIDGE_KNOWN_HOSTS', '').strip()
    rsync_binary = os.getenv('UCEPROTECT_RSYNC_BINARY', 'rsync')

    if not 1 <= port <= 65535:
        raise ValueError('UCEPROTECT_BRIDGE_PORT debe estar entre 1 y 65535')
    if timeout <= 0:
        raise ValueError('UCEPROTECT_BRIDGE_TIMEOUT_SECONDS debe ser positivo')
    if max_age <= 0:
        raise ValueError('UCEPROTECT_BRIDGE_MAX_AGE_SECONDS debe ser positivo')

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
    ssh_parts = [
        'ssh',
        '-p',
        str(port),
        '-o',
        'BatchMode=yes',
        '-o',
        'StrictHostKeyChecking=yes',
    ]
    if known_hosts:
        ssh_parts.extend(['-o', f'UserKnownHostsFile={known_hosts}'])
    if identity_file:
        ssh_parts.extend(['-i', identity_file])

    command = [
        rsync_binary,
        '-a',
        '--delete',
        '--delay-updates',
        f'--timeout={timeout}',
        '-e',
        ' '.join(shlex.quote(part) for part in ssh_parts),
        f'{user}@{host}:{remote_storage}/',
        str(staging) + '/',
    ]

    print(
        f'BRIDGE_COLLECT_START host={host} remote={remote_storage} '
        f'destination={local_storage}'
    )
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout + 60,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or '').strip()
            raise RuntimeError(
                f'No se pudo recolectar UCEPROTECT desde {host}; '
                f'rsync código {result.returncode}: {detail[-4000:]}'
            )

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
