from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Optional, Sequence

from src.ips_spam.models import SourceDefinition


SOURCE_KEYS = ('lvl1', 'lvl2', 'lvl3', 'backscatter', 'whitelist', 'asn')


def parse_bool(value: object) -> bool:
    normalized = str(value).strip().lower()
    if normalized in {'1', 'true', 'yes', 'si', 'sí', 'on'}:
        return True
    if normalized in {'0', 'false', 'no', 'off'}:
        return False
    raise ValueError(f'Valor booleano no válido: {value}')


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_environment() -> None:
    from dotenv import load_dotenv

    load_dotenv(project_root() / '.env')


def source_definitions():
    return (
        SourceDefinition(
            key='lvl1',
            kind='rsync',
            remote_name='dnsbl-1.uceprotect.net',
            target_table=os.getenv(
                'UCEPROTECT_TABLE_LVL1',
                'spam.UCEPRTC_LVL1',
            ),
        ),
        SourceDefinition(
            key='lvl2',
            kind='rsync',
            remote_name='dnsbl-2.uceprotect.net',
            target_table=os.getenv(
                'UCEPROTECT_TABLE_LVL2',
                'spam.UCEPRTC_LVL2',
            ),
        ),
        SourceDefinition(
            key='lvl3',
            kind='rsync',
            remote_name='dnsbl-3.uceprotect.net',
            target_table=os.getenv(
                'UCEPROTECT_TABLE_LVL3',
                'spam.UCEPRTC_LVL3',
            ),
        ),
        SourceDefinition(
            key='backscatter',
            kind='rsync',
            remote_name='ips.backscatterer.org',
            target_table=os.getenv(
                'UCEPROTECT_TABLE_BACKSCATTER',
                'spam.UCEPRTC_LST_BCK',
            ),
        ),
        SourceDefinition(
            key='whitelist',
            kind='rsync',
            remote_name='ips.whitelisted.org',
            target_table=os.getenv(
                'UCEPROTECT_TABLE_WHITELIST',
                'spam.UCEPRCT_LST_WHT',
            ),
        ),
        SourceDefinition(
            key='asn',
            kind='asn',
            target_table=os.getenv(
                'UCEPROTECT_TABLE_ASN',
                'spam.UCEPRTC_ASN',
            ),
        ),
    )


def clickhouse_settings_from_environment():
    variable_map = {
        'DB_CH_SPAM_HOST': 'host',
        'DB_CH_SPAM_PORT': 'port',
        'DB_CH_SPAM_DATABASE': 'database',
        'DB_CH_SPAM_USERNAME': 'user',
        'DB_CH_SPAM_PASSWORD': 'password',
    }
    missing = [name for name in variable_map if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            'Faltan variables ClickHouse SPAM: ' + ', '.join(missing)
        )
    settings = {
        target: os.environ[source]
        for source, target in variable_map.items()
    }
    settings['port'] = int(settings['port'])
    return settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Carga listas UCEPROTECT en ClickHouse spam',
    )
    parser.add_argument(
        '--source',
        choices=('all',) + SOURCE_KEYS,
        default=os.getenv('UCEPROTECT_SOURCE', 'all'),
        help='Fuente específica o all para procesar todas',
    )
    parser.add_argument(
        '--extract-only',
        action='store_true',
        default=parse_bool(os.getenv('UCEPROTECT_EXTRACT_ONLY', 'false')),
        help='Descarga y valida sin conectarse a ClickHouse',
    )
    parser.add_argument(
        '--skip-download',
        action='store_true',
        default=parse_bool(os.getenv('UCEPROTECT_SKIP_DOWNLOAD', 'false')),
        help='Procesa los archivos ya descargados',
    )
    parser.add_argument(
        '--full-download',
        action='store_true',
        default=parse_bool(os.getenv('UCEPROTECT_FULL_DOWNLOAD', 'false')),
        help='Fuerza la transferencia completa por rsync',
    )
    parser.add_argument(
        '--sample-size',
        type=int,
        default=int(os.getenv('UCEPROTECT_SAMPLE_SIZE', '0')),
        help='Muestra N registros en el resultado; recomendado solo para pruebas',
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=int(os.getenv('UCEPROTECT_BATCH_SIZE', '10000')),
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    load_environment()
    args = build_parser().parse_args(argv)
    if args.skip_download and args.full_download:
        raise ValueError(
            '--skip-download y --full-download no pueden usarse juntos'
        )
    if args.sample_size < 0 or args.sample_size > 100:
        raise ValueError('sample-size debe estar entre 0 y 100')

    from src.ips_spam.extractors import (
        AsnChartParser,
        HtmlExtractor,
        RsyncExtractor,
        RsyncListParser,
    )
    from src.ips_spam.repositories import ClickHouseSpamRepository
    from src.ips_spam.service import IpsSpamLoadService

    storage_dir = Path(
        os.getenv(
            'UCEPROTECT_STORAGE_DIR',
            str(project_root() / 'files' / 'uceprotect'),
        )
    )
    rsync_extractor = RsyncExtractor(
        storage_dir=storage_dir,
        remote_base=os.getenv(
            'UCEPROTECT_RSYNC_BASE',
            'rsync-mirrors.uceprotect.net::RBLDNSD-ALL',
        ),
        binary=os.getenv('UCEPROTECT_RSYNC_BINARY', 'rsync'),
        timeout_seconds=int(
            os.getenv('UCEPROTECT_RSYNC_TIMEOUT_SECONDS', '180')
        ),
    )
    html_extractor = HtmlExtractor(
        storage_dir=storage_dir,
        url=os.getenv(
            'UCEPROTECT_ASN_URL',
            'https://www.uceprotect.net/de/l3charts.php',
        ),
        timeout_seconds=int(
            os.getenv('UCEPROTECT_HTTP_TIMEOUT_SECONDS', '60')
        ),
        user_agent=os.getenv(
            'UCEPROTECT_HTTP_USER_AGENT',
            'py_apps-ips-spam/1.0',
        ),
    )

    selected_sources = [
        source
        for source in source_definitions()
        if args.source == 'all' or source.key == args.source
    ]
    clickhouse = None
    repository = None
    try:
        if not args.extract_only:
            from src.shared.database.ClickHouseDB import ClickHouseDB

            clickhouse = ClickHouseDB()
            clickhouse.connectWithConfig(
                'clickhouse_spam',
                clickhouse_settings_from_environment(),
            )
            repository = ClickHouseSpamRepository(
                clickhouse,
                audit_table=os.getenv(
                    'UCEPROTECT_AUDIT_TABLE',
                    'spam.UCEPRTC_AUDITORIA',
                ),
                batch_size=args.batch_size,
            )

        service = IpsSpamLoadService(
            rsync_extractor=rsync_extractor,
            html_extractor=html_extractor,
            list_parser=RsyncListParser(),
            asn_parser=AsnChartParser(),
            repository=repository,
        )
        service.execute(
            sources=selected_sources,
            extract_only=args.extract_only,
            skip_download=args.skip_download,
            full_download=args.full_download,
            sample_size=args.sample_size,
        )
        return 0
    finally:
        if clickhouse is not None:
            clickhouse.close()
