from __future__ import annotations

import argparse
import datetime as dt
import os
from pathlib import Path
from typing import Optional, Sequence
from zoneinfo import ZoneInfo


LIMA_TZ = ZoneInfo('America/Lima')


def project_dir() -> Path:
    return Path(__file__).resolve().parent


def load_environment() -> None:
    from dotenv import load_dotenv
    load_dotenv(project_dir() / '.env')


def clickhouse_hosts_from_environment():
    raw_hosts = os.getenv('TOP_IPS_SOURCE_HOSTS')
    if not raw_hosts:
        raise RuntimeError('Falta TOP_IPS_SOURCE_HOSTS')
    hosts = []
    for raw_host in raw_hosts.split(','):
        host = raw_host.strip()
        if host and host not in hosts:
            hosts.append(host)
    if not hosts:
        raise RuntimeError('TOP_IPS_SOURCE_HOSTS no contiene nodos válidos')
    return hosts


def clickhouse_settings_from_environment(prefix: str, host: Optional[str] = None):
    variables = {
        f'{prefix}_HOST': 'host', f'{prefix}_PORT': 'port',
        f'{prefix}_DATABASE': 'database', f'{prefix}_USERNAME': 'user',
        f'{prefix}_PASSWORD': 'password',
    }
    if host is not None:
        variables.pop(f'{prefix}_HOST')
    missing = [variable for variable in variables if not os.getenv(variable)]
    if missing:
        raise RuntimeError('Faltan variables ClickHouse: ' + ', '.join(missing))
    settings = {target: os.environ[variable] for variable, target in variables.items()}
    settings['host'] = host or settings['host']
    settings['port'] = int(settings['port'])
    return settings


def configure_source_connections(clickhouse_factory):
    connections = []
    current = None
    try:
        for index, host in enumerate(clickhouse_hosts_from_environment(), 1):
            current = clickhouse_factory()
            current.connectWithConfig(f'top_ips_source_{index}', clickhouse_settings_from_environment('TOP_IPS_SOURCE', host))
            connections.append((host, current))
            current = None
        return connections
    except BaseException:
        if current is not None:
            current.close()
        for _, clickhouse in connections:
            clickhouse.close()
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Carga los top de IP CGNAT desde cuatro nodos hacia elog')
    parser.add_argument('--process-date', default=os.getenv('TOP_IPS_PROCESS_DATE'), help='Fecha YYYY-MM-DD de la tabla fuente; por defecto, ayer en Lima')
    parser.add_argument('--batch-size', type=int, default=int(os.getenv('TOP_IPS_BATCH_SIZE', '10000')))
    return parser


def resolve_process_date(value: Optional[str]) -> dt.date:
    if not value:
        return dt.datetime.now(LIMA_TZ).date() - dt.timedelta(days=1)
    try:
        return dt.date.fromisoformat(value)
    except ValueError as error:
        raise ValueError('--process-date debe usar el formato YYYY-MM-DD') from error


def main(argv: Optional[Sequence[str]] = None) -> int:
    load_environment()
    args = build_parser().parse_args(argv)
    process_date = resolve_process_date(args.process_date)
    from src.shared.database.ClickHouseDB import ClickHouseDB
    from src.top_ips_elog.models import TOP_QUERY_DEFINITIONS
    from src.top_ips_elog.repositories import ClickHouseTopIpsSourceRepository, ClickHouseTopIpsTargetRepository
    from src.top_ips_elog.service import TopIpsElogLoadService
    source_connections, target = [], None
    try:
        source_connections = configure_source_connections(ClickHouseDB)
        target = ClickHouseDB()
        target.connectWithConfig('top_ips_target', clickhouse_settings_from_environment('TOP_IPS_TARGET'))
        source_prefix = os.getenv('TOP_IPS_SOURCE_TABLE_PREFIX', 'cgnat.huawei_cgn_nat_v2')
        service = TopIpsElogLoadService(
            [(host, ClickHouseTopIpsSourceRepository(clickhouse, source_prefix)) for host, clickhouse in source_connections],
            ClickHouseTopIpsTargetRepository(target, database=os.getenv('TOP_IPS_TARGET_DATABASE', 'elog'), batch_size=args.batch_size),
            TOP_QUERY_DEFINITIONS,
        )
        service.execute(process_date)
        return 0
    finally:
        for _, clickhouse in source_connections:
            clickhouse.close()
        if target is not None:
            target.close()
