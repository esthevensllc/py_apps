from __future__ import annotations

import datetime as dt
import json
import socket
from typing import Mapping

from src.alertas_elog.models import (
    LIMA_TZ,
    ServerAvailabilityRecord,
)


class TcpPortProbe:
    def __init__(
        self,
        port: int = 8123,
        timeout_seconds: int = 2,
        connection_factory=None,
    ):
        if port < 1 or port > 65535:
            raise ValueError('puerto TCP debe estar entre 1 y 65535')
        if timeout_seconds < 1 or timeout_seconds > 60:
            raise ValueError('TCP timeout debe estar entre 1 y 60 segundos')
        self.port = int(port)
        self.timeout_seconds = int(timeout_seconds)
        self.connection_factory = connection_factory or socket.create_connection

    def is_reachable(self, ip: str) -> bool:
        try:
            connection = self.connection_factory(
                (ip, self.port),
                timeout=self.timeout_seconds,
            )
        except OSError:
            return False
        try:
            return True
        finally:
            connection.close()


class ServerAvailabilityMonitoringService:
    def __init__(
        self,
        servers,
        probe,
        target_repository,
        now_provider=None,
    ):
        if not servers:
            raise ValueError('Debe configurarse al menos un servidor a monitorear')
        self.servers = list(servers)
        self.probe = probe
        self.target_repository = target_repository
        self.now_provider = now_provider or (lambda: dt.datetime.now(LIMA_TZ))

    def execute(self, dry_run: bool = False) -> Mapping[str, object]:
        checked_at = self.now_provider()
        records = []
        statuses = []

        for server in self.servers:
            reachable = self.probe.is_reachable(server.ip)
            record = ServerAvailabilityRecord.from_availability(
                server,
                reachable,
                checked_at,
            )
            records.append(record)
            statuses.append(
                {
                    'hostname': server.hostname,
                    'ip': server.ip,
                    'reachable': reachable,
                    'estado': record.estado,
                }
            )
            print(
                f'TCP_RESULT hostname={server.hostname} ip={server.ip} '
                f'reachable={str(reachable).lower()} estado={record.estado}'
            )

        if not dry_run:
            self.target_repository.upsert(records)

        result = {
            'servers': statuses,
            'server_count': len(statuses),
            'down_count': sum(
                1 for status in statuses if not status['reachable']
            ),
            'reachable_count': sum(
                1 for status in statuses if status['reachable']
            ),
            'dry_run': dry_run,
        }
        print('TCP_SUMMARY ' + json.dumps(result, sort_keys=True))
        return result


class AlertasElogReplicationService:
    def __init__(self, source_repository, target_repository):
        self.source_repository = source_repository
        self.target_repository = target_repository

    def execute(
        self,
        full_sync: bool = False,
        lookback_hours: int = 48,
        batch_size: int = 5000,
        dry_run: bool = False,
    ) -> Mapping[str, object]:
        cursor = None
        processed_rows = 0
        processed_batches = 0
        max_version = None

        while True:
            records = self.source_repository.fetch_batch(
                batch_size=batch_size,
                full_sync=full_sync,
                lookback_hours=lookback_hours,
                cursor=cursor,
            )
            if not records:
                break

            last_record = records[-1]
            next_cursor = (last_record.version, last_record.id)
            if next_cursor == cursor:
                raise RuntimeError(
                    f'ClickHouse no avanzó después del cursor {cursor}'
                )

            if not dry_run:
                self.target_repository.upsert(records, batch_size=batch_size)

            processed_batches += 1
            processed_rows += len(records)
            cursor = next_cursor
            max_version = last_record.version
            print(
                f'BATCH {processed_batches}: rows={len(records)} '
                f'total={processed_rows} cursor={cursor[0]}:{cursor[1]}'
            )

            if len(records) < batch_size:
                break

        result = {
            'mode': 'full' if full_sync else 'incremental',
            'processed_batches': processed_batches,
            'processed_rows': processed_rows,
            'max_version': max_version,
            'lookback_hours': lookback_hours,
            'dry_run': dry_run,
        }
        print('RESULT ' + json.dumps(result, sort_keys=True))
        return result


class MultiSourceAlertasElogReplicationService:
    def __init__(self, sources, target_repository):
        if not sources:
            raise ValueError('Debe configurarse al menos un origen ClickHouse')
        self.sources = list(sources)
        self.target_repository = target_repository

    def execute(
        self,
        full_sync: bool = False,
        lookback_hours: int = 48,
        batch_size: int = 5000,
        dry_run: bool = False,
    ) -> Mapping[str, object]:
        source_results = {}
        for source_name, source_repository in self.sources:
            print(f'ALERTAS_SOURCE_START host={source_name}')
            result = AlertasElogReplicationService(
                source_repository,
                self.target_repository,
            ).execute(
                full_sync=full_sync,
                lookback_hours=lookback_hours,
                batch_size=batch_size,
                dry_run=dry_run,
            )
            source_results[source_name] = result
            print(
                'ALERTAS_SOURCE_RESULT '
                + json.dumps(
                    {'host': source_name, **result},
                    sort_keys=True,
                )
            )

        summary = {
            'sources': source_results,
            'source_count': len(source_results),
            'processed_rows': sum(
                result['processed_rows']
                for result in source_results.values()
            ),
            'dry_run': dry_run,
        }
        print('ALERTAS_MULTI_RESULT ' + json.dumps(summary, sort_keys=True))
        return summary


class RoutersElogReplicationService:
    def __init__(self, source_repository, target_repository):
        self.source_repository = source_repository
        self.target_repository = target_repository

    def execute(self, dry_run: bool = False) -> Mapping[str, object]:
        record = self.source_repository.fetch_latest()
        if not dry_run:
            self.target_repository.upsert(record)
        result = {
            'routers_unicos': record.routers_unicos,
            'fecha_medicion': record.fecha_medicion,
            'dry_run': dry_run,
        }
        print('ROUTERS_RESULT ' + json.dumps(result, sort_keys=True))
        return result
