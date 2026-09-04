from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Mapping, Optional, Sequence, Union
from zoneinfo import ZoneInfo


LIMA_TZ = ZoneInfo('America/Lima')
SOURCE_COLUMNS = (
    'id',
    'hostname',
    'ip',
    'fecha_inicio',
    'fecha_fin',
    'nombre',
    'umbral',
    'porcentaje_indicador',
    'estado',
    'fecha_envio',
    'version',
)


@dataclass(frozen=True)
class AlertRecord:
    id: str
    hostname: str
    ip: str
    fecha_inicio: str
    fecha_fin: Optional[str]
    nombre: str
    umbral: Decimal
    porcentaje_indicador: Decimal
    estado: str
    fecha_envio: str
    version: int

    @classmethod
    def from_clickhouse_row(
        cls,
        row: Union[Mapping[str, object], Sequence[object]],
    ) -> 'AlertRecord':
        if isinstance(row, Mapping):
            values = [row[column] for column in SOURCE_COLUMNS]
        else:
            if len(row) != len(SOURCE_COLUMNS):
                raise ValueError(
                    f'ClickHouse devolvió {len(row)} columnas; '
                    f'se esperaban {len(SOURCE_COLUMNS)}'
                )
            values = list(row)

        record_id = str(values[0])
        try:
            uuid.UUID(record_id)
        except (ValueError, AttributeError) as error:
            raise ValueError(f'ID no es UUID válido: {record_id}') from error

        estado = cls._required_string(values[8], 'estado').upper()
        if estado not in {'ACTIVE', 'CLEARED'}:
            raise ValueError(f"Estado no permitido por Oracle: '{estado}'")

        record = cls(
            id=record_id,
            hostname=cls._required_string(values[1], 'hostname'),
            ip=cls._required_string(values[2], 'ip'),
            fecha_inicio=cls._oracle_timestamp(values[3], 'fecha_inicio'),
            fecha_fin=(
                None
                if values[4] is None
                else cls._oracle_timestamp(values[4], 'fecha_fin')
            ),
            nombre=cls._required_string(values[5], 'nombre'),
            umbral=cls._decimal(values[6], 'umbral'),
            porcentaje_indicador=cls._decimal(
                values[7],
                'porcentaje_indicador',
            ),
            estado=estado,
            fecha_envio=cls._oracle_timestamp(values[9], 'fecha_envio'),
            version=int(values[10]),
        )
        record.validate_lengths()
        return record

    def validate_lengths(self) -> None:
        limits = {
            'id': (self.id, 36),
            'hostname': (self.hostname, 255),
            'ip': (self.ip, 45),
            'nombre': (self.nombre, 255),
            'estado': (self.estado, 16),
        }
        for field, (value, limit) in limits.items():
            if len(value) > limit:
                raise ValueError(
                    f'{field} supera VARCHAR2({limit}): {len(value)} caracteres'
                )

    def to_oracle_row(self) -> Mapping[str, object]:
        return {
            'id': self.id,
            'hostname': self.hostname,
            'ip': self.ip,
            'fecha_inicio': self.fecha_inicio,
            'fecha_fin': self.fecha_fin,
            'nombre': self.nombre,
            'umbral': self.umbral,
            'porcentaje_indicador': self.porcentaje_indicador,
            'estado': self.estado,
            'fecha_envio': self.fecha_envio,
        }

    @staticmethod
    def _required_string(value: object, field: str) -> str:
        if value is None:
            raise ValueError(f'{field} no puede ser NULL')
        result = str(value)
        if result == '':
            raise ValueError(f'{field} no puede estar vacío')
        return result

    @staticmethod
    def _decimal(value: object, field: str) -> Decimal:
        try:
            result = Decimal(str(value))
        except (InvalidOperation, ValueError) as error:
            raise ValueError(f'{field} no es numérico: {value}') from error
        if not result.is_finite():
            raise ValueError(f'{field} no puede ser NaN o infinito')
        return result

    @staticmethod
    def _oracle_timestamp(value: object, field: str) -> str:
        parsed: Optional[dt.datetime] = None
        if isinstance(value, dt.datetime):
            parsed = value
        elif isinstance(value, str):
            normalized = value.strip()
            if normalized.endswith('Z'):
                normalized = normalized[:-1] + '+00:00'
            try:
                parsed = dt.datetime.fromisoformat(normalized)
            except ValueError as error:
                raise ValueError(
                    f'{field} no tiene un timestamp ISO válido: {value}'
                ) from error
        else:
            raise ValueError(f'{field} no es timestamp: {value}')

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=LIMA_TZ)
        else:
            parsed = parsed.astimezone(LIMA_TZ)

        offset = parsed.strftime('%z')
        offset = offset[:3] + ':' + offset[3:]
        return parsed.strftime('%Y-%m-%d %H:%M:%S.%f ') + offset


@dataclass(frozen=True)
class MonitoredServer:
    hostname: str
    ip: str

    def __post_init__(self) -> None:
        if not self.hostname.strip():
            raise ValueError('hostname del servidor no puede estar vacío')
        if not self.ip.strip():
            raise ValueError('ip del servidor no puede estar vacía')
        if len(self.hostname) > 255:
            raise ValueError('hostname del servidor supera VARCHAR2(255)')
        if len(self.ip) > 45:
            raise ValueError('ip del servidor supera VARCHAR2(45)')


@dataclass(frozen=True)
class ServerAvailabilityRecord:
    id: str
    hostname: str
    ip: str
    nombre: str
    umbral: Decimal
    porcentaje_indicador: Decimal
    estado: str
    fecha_envio: str

    @classmethod
    def from_availability(
        cls,
        server: MonitoredServer,
        reachable: bool,
        checked_at: dt.datetime,
    ) -> 'ServerAvailabilityRecord':
        record = cls(
            id=str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f'py_apps/alertas_elog/server/{server.ip}',
                )
            ),
            hostname=server.hostname,
            ip=server.ip,
            nombre=f'Servidor Caido {server.hostname} {server.ip}',
            umbral=Decimal('1'),
            porcentaje_indicador=(
                Decimal('0') if reachable else Decimal('100')
            ),
            estado='CLEARED' if reachable else 'ACTIVE',
            fecha_envio=AlertRecord._oracle_timestamp(
                checked_at,
                'fecha_envio',
            ),
        )
        record.validate_lengths()
        return record

    def validate_lengths(self) -> None:
        limits = {
            'id': (self.id, 36),
            'hostname': (self.hostname, 255),
            'ip': (self.ip, 45),
            'nombre': (self.nombre, 255),
            'estado': (self.estado, 16),
        }
        for field, (value, limit) in limits.items():
            if len(value) > limit:
                raise ValueError(
                    f'{field} supera VARCHAR2({limit}): {len(value)} caracteres'
                )

    def to_oracle_row(self) -> Mapping[str, object]:
        return {
            'id': self.id,
            'hostname': self.hostname,
            'ip': self.ip,
            'nombre': self.nombre,
            'umbral': self.umbral,
            'porcentaje_indicador': self.porcentaje_indicador,
            'estado': self.estado,
            'fecha_envio': self.fecha_envio,
        }


@dataclass(frozen=True)
class RouterMetricRecord:
    routers_unicos: int
    fecha_medicion: str

    @classmethod
    def from_clickhouse_row(
        cls,
        row: Union[Mapping[str, object], Sequence[object]],
    ) -> 'RouterMetricRecord':
        if isinstance(row, Mapping):
            routers_unicos = row['routers_unicos']
            fecha_medicion = row['fecha_medicion']
        else:
            if len(row) != 2:
                raise ValueError(
                    f'ClickHouse devolvió {len(row)} columnas para routers; '
                    'se esperaban 2'
                )
            routers_unicos, fecha_medicion = row

        count = int(routers_unicos)
        if count < 0:
            raise ValueError('routers_unicos no puede ser negativo')
        return cls(
            routers_unicos=count,
            fecha_medicion=AlertRecord._oracle_timestamp(
                fecha_medicion,
                'fecha_medicion',
            ),
        )

    def to_oracle_row(self) -> Mapping[str, object]:
        return {
            'routers_unicos': self.routers_unicos,
            'fecha_medicion': self.fecha_medicion,
        }
