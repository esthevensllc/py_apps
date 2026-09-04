from __future__ import annotations

import argparse
import ipaddress
import os
from pathlib import Path
from typing import Optional, Sequence


def parse_bool(value: object) -> bool:
    normalized = str(value).strip().lower()
    if normalized in {'1', 'true', 'yes', 'si', 'sí', 'on'}:
        return True
    if normalized in {'0', 'false', 'no', 'off'}:
        return False
    raise ValueError(f'Valor booleano no válido: {value}')


def load_environment() -> None:
    from dotenv import load_dotenv

    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / '.env')


def clickhouse_hosts_from_environment():
    raw_hosts = os.getenv('DB_CH_ELOG_HOSTS') or os.getenv('DB_CH_ELOG_HOST')
    if not raw_hosts:
        raise RuntimeError(
            'Falta DB_CH_ELOG_HOSTS (o DB_CH_ELOG_HOST por compatibilidad)'
        )

    hosts = []
    for value in raw_hosts.split(','):
        host = value.strip()
        if host and host not in hosts:
            hosts.append(host)
    if not hosts:
        raise RuntimeError('DB_CH_ELOG_HOSTS no contiene servidores válidos')
    return hosts


def monitored_servers_from_environment():
    from src.alertas_elog.models import MonitoredServer

    raw_servers = os.getenv('ALERTAS_ELOG_MONITORED_SERVERS')
    if not raw_servers:
        raise RuntimeError('Falta ALERTAS_ELOG_MONITORED_SERVERS')

    servers_by_ip = {}
    hostnames = set()
    for entry in raw_servers.split(','):
        value = entry.strip()
        hostname, separator, raw_ip = value.partition('=')
        hostname = hostname.strip()
        server_ip = raw_ip.strip()
        if not separator or not hostname or not server_ip:
            raise RuntimeError(
                'ALERTAS_ELOG_MONITORED_SERVERS debe usar '
                'HOSTNAME=IP separados por coma'
            )
        try:
            normalized_ip = str(ipaddress.ip_address(server_ip))
        except ValueError as error:
            raise RuntimeError(
                f'IP inválida en ALERTAS_ELOG_MONITORED_SERVERS: {server_ip}'
            ) from error
        if normalized_ip in servers_by_ip:
            raise RuntimeError(f'IP de monitoreo duplicada: {normalized_ip}')
        if hostname in hostnames:
            raise RuntimeError(f'HOSTNAME de monitoreo duplicado: {hostname}')
        servers_by_ip[normalized_ip] = hostname
        hostnames.add(hostname)

    clickhouse_hosts = clickhouse_hosts_from_environment()
    missing = [host for host in clickhouse_hosts if host not in servers_by_ip]
    extra = [host for host in servers_by_ip if host not in clickhouse_hosts]
    if missing or extra:
        raise RuntimeError(
            'Los servidores monitoreados deben coincidir con DB_CH_ELOG_HOSTS. '
            f'Faltantes={missing}; adicionales={extra}'
        )
    return [
        MonitoredServer(hostname=servers_by_ip[ip], ip=ip)
        for ip in clickhouse_hosts
    ]


def clickhouse_settings_from_environment(host=None):
    variable_map = {
        'DB_CH_ELOG_PORT': 'port',
        'DB_CH_ELOG_DATABASE': 'database',
        'DB_CH_ELOG_USERNAME': 'user',
        'DB_CH_ELOG_PASSWORD': 'password',
    }
    missing = [name for name in variable_map if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            'Faltan variables ClickHouse ELOG: ' + ', '.join(missing)
        )
    settings = {
        target: os.environ[source]
        for source, target in variable_map.items()
    }
    settings['host'] = host or clickhouse_hosts_from_environment()[0]
    settings['port'] = int(settings['port'])
    return settings


def configure_clickhouse_connections(clickhouse_factory):
    connections = []
    for index, host in enumerate(clickhouse_hosts_from_environment(), 1):
        clickhouse = clickhouse_factory()
        try:
            clickhouse.connectWithConfig(
                f'clickhouse_elog_{index}',
                clickhouse_settings_from_environment(host),
            )
        except BaseException:
            clickhouse.close()
            for _, configured_clickhouse in connections:
                configured_clickhouse.close()
            raise
        connections.append((host, clickhouse))
    return connections


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Replica cgnat.collector_alerts de ClickHouse hacia Oracle',
    )
    parser.add_argument(
        '--full-sync',
        action='store_true',
        default=parse_bool(os.getenv('ALERTAS_ELOG_FULL_SYNC', 'false')),
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=parse_bool(os.getenv('ALERTAS_ELOG_DRY_RUN', 'false')),
        help='Lee y valida el origen sin escribir en Oracle',
    )
    parser.add_argument(
        '--lookback-hours',
        type=int,
        default=int(os.getenv('ALERTAS_ELOG_LOOKBACK_HOURS', '48')),
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=int(os.getenv('ALERTAS_ELOG_BATCH_SIZE', '5000')),
    )
    parser.add_argument(
        '--monitor-port',
        type=int,
        default=int(
            os.getenv(
                'ALERTAS_ELOG_MONITOR_PORT',
                os.getenv('DB_CH_ELOG_PORT', '8123'),
            )
        ),
    )
    parser.add_argument(
        '--tcp-timeout-seconds',
        type=int,
        default=int(
            os.getenv(
                'ALERTAS_ELOG_TCP_TIMEOUT_SECONDS',
                '2',
            )
        ),
    )
    parser.add_argument(
        '--source-table',
        default=os.getenv(
            'ALERTAS_ELOG_SOURCE_TABLE',
            'cgnat.collector_alerts',
        ),
    )
    parser.add_argument(
        '--target-table',
        default=os.getenv('ALERTAS_ELOG_TARGET_TABLE', 'ALERTAS_ELOG'),
    )
    parser.add_argument(
        '--routers-source-prefix',
        default=os.getenv(
            'ROUTERS_ELOG_SOURCE_PREFIX',
            'cgnat.huawei_cgn_nat_v2',
        ),
    )
    parser.add_argument(
        '--routers-target-table',
        default=os.getenv('ROUTERS_ELOG_TARGET_TABLE', 'ROUTERS_ELOG'),
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    load_environment()
    args = build_parser().parse_args(argv)

    from src.alertas_elog.repositories import (
        ClickHouseCollectorAlertsRepository,
        ClickHouseRoutersElogRepository,
        OracleAlertasElogRepository,
        OracleRoutersElogRepository,
        OracleServerAvailabilityRepository,
    )
    from src.alertas_elog.service import (
        MultiSourceAlertasElogReplicationService,
        RoutersElogReplicationService,
        ServerAvailabilityMonitoringService,
        TcpPortProbe,
    )
    from src.shared.app.AppContainer import AppContainer
    from src.shared.database.ClickHouseDB import ClickHouseDB

    clickhouses = []
    app_container = None
    try:
        app_container = AppContainer()
        oracle = app_container.getInstance('dboracle')

        monitoring_service = ServerAvailabilityMonitoringService(
            monitored_servers_from_environment(),
            TcpPortProbe(
                port=args.monitor_port,
                timeout_seconds=args.tcp_timeout_seconds,
            ),
            OracleServerAvailabilityRepository(oracle, args.target_table),
        )
        monitoring_service.execute(dry_run=args.dry_run)

        clickhouses = configure_clickhouse_connections(ClickHouseDB)
        service = MultiSourceAlertasElogReplicationService(
            [
                (
                    host,
                    ClickHouseCollectorAlertsRepository(
                        clickhouse,
                        args.source_table,
                    ),
                )
                for host, clickhouse in clickhouses
            ],
            OracleAlertasElogRepository(oracle, args.target_table),
        )
        service.execute(
            full_sync=args.full_sync,
            lookback_hours=args.lookback_hours,
            batch_size=args.batch_size,
            dry_run=args.dry_run,
        )
        routers_service = RoutersElogReplicationService(
            ClickHouseRoutersElogRepository(
                clickhouses,
                args.routers_source_prefix,
            ),
            OracleRoutersElogRepository(
                oracle,
                args.routers_target_table,
            ),
        )
        routers_service.execute(dry_run=args.dry_run)
        return 0
    finally:
        for _, clickhouse in clickhouses:
            clickhouse.close()
        if app_container is not None:
            app_container.close_connections()
