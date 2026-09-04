from __future__ import annotations

import argparse
import datetime as dt
import os
from pathlib import Path
from typing import Optional, Sequence


DEFAULT_START = '2026-07-12 21:00'
DEFAULT_END = '2026-07-13 06:00'
DEFAULT_REMOTE_ROOT = '/hfs_public/nbi/text/pfm_output'


def parse_bool(value: object) -> bool:
    normalized = str(value).strip().lower()
    if normalized in {'1', 'true', 'yes', 'si', 'sí', 'on'}:
        return True
    if normalized in {'0', 'false', 'no', 'off'}:
        return False
    raise ValueError(f'Valor booleano no válido: {value}')


def parse_datetime(value: str) -> dt.datetime:
    formats = (
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M',
    )
    for date_format in formats:
        try:
            return dt.datetime.strptime(value, date_format)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(
        f"Fecha '{value}' inválida. Use YYYY-MM-DD HH:MM[:SS]"
    )


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_environment() -> None:
    from dotenv import load_dotenv

    root = project_root()
    load_dotenv(root / '.env')


def configure_reload_connection() -> None:
    variable_map = {
        'SFTP_NCE_RECARGA_HOST': 'SFTP_NCE_HOST',
        'SFTP_NCE_RECARGA_PORT': 'SFTP_NCE_PORT',
        'SFTP_NCE_RECARGA_USERNAME': 'SFTP_NCE_USERNAME',
        'SFTP_NCE_RECARGA_PASSWORD': 'SFTP_NCE_PASSWORD',
    }
    missing = []
    for source, target in variable_map.items():
        value = os.getenv(source)
        if value is None or value == '':
            if source != 'SFTP_NCE_RECARGA_PORT':
                missing.append(source)
            continue
        os.environ[target] = value

    if missing:
        raise RuntimeError(
            'Faltan variables para la conexión de recarga: '
            + ', '.join(missing)
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Recarga histórica de archivos CSV NCE desde SFTP hacia Oracle',
    )
    parser.add_argument(
        '--start',
        type=parse_datetime,
        default=parse_datetime(os.getenv('NCE_RECARGA_START', DEFAULT_START)),
        help='Inicio inclusivo del rango',
    )
    parser.add_argument(
        '--end',
        type=parse_datetime,
        default=parse_datetime(os.getenv('NCE_RECARGA_END', DEFAULT_END)),
        help='Fin exclusivo del rango',
    )
    parser.add_argument(
        '--remote-root',
        default=os.getenv('NCE_RECARGA_REMOTE_ROOT', DEFAULT_REMOTE_ROOT),
    )
    parser.add_argument(
        '--dry-run',
        dest='dry_run',
        action='store_true',
        help='Solo listar y validar archivos',
    )
    parser.add_argument(
        '--execute',
        dest='dry_run',
        action='store_false',
        help='Ejecutar la recarga real',
    )
    parser.add_argument(
        '--allow-missing',
        dest='strict',
        action='store_false',
        help='Permitir que falten timestamps esperados',
    )
    parser.add_argument(
        '--skip-success-events',
        dest='emit_success_events',
        action='store_false',
        help='No ejecutar SP_NCE_FILE_SUCCESS después de cargar',
    )
    parser.set_defaults(
        dry_run=parse_bool(os.getenv('NCE_RECARGA_DRY_RUN', 'true')),
        strict=parse_bool(os.getenv('NCE_RECARGA_STRICT', 'true')),
        emit_success_events=parse_bool(
            os.getenv('NCE_RECARGA_EMIT_SUCCESS_EVENTS', 'true')
        ),
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    load_environment()
    args = build_parser().parse_args(argv)
    configure_reload_connection()

    from src.nce.cargas.services.LoadCSV import LoadCSV
    from src.nce.shared.services import LOAD_CSV
    from src.nce_recarga.service import NCERecargaService
    from src.shared.app.AppContainer import AppContainer

    app_container = AppContainer()
    try:
        load_csv = app_container.getInstance(LOAD_CSV)
        if not isinstance(load_csv, LoadCSV):
            raise RuntimeError('El servicio LOAD_CSV no tiene el tipo esperado')

        service = NCERecargaService(
            load_csv=load_csv,
            remote_root=args.remote_root,
        )
        service.execute(
            start=args.start,
            end=args.end,
            dry_run=args.dry_run,
            strict=args.strict,
            emit_success_events=args.emit_success_events,
        )
        return 0
    finally:
        app_container.close_connections()
