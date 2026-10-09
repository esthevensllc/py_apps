from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass
from typing import Optional

from .service import build_payload


LIMA_TZ = dt.timezone(dt.timedelta(hours=-5))


def recipient_phone(value) -> str:
    if value is None:
        raise ValueError('El celular de origen es obligatorio para evitar duplicados')
    phone = re.sub(r'[+ ()-]', '', str(value).strip())
    if not re.fullmatch(r'[0-9]{7,15}', phone):
        raise ValueError('El celular de origen no es válido')
    return phone


def normalize_phone(value) -> str:
    phone = recipient_phone(value)
    if len(phone) == 9 and phone.startswith('9'):
        phone = '51' + phone
    return phone


def oracle_datetime(value, field_name: str) -> dt.datetime:
    if not isinstance(value, dt.datetime):
        raise ValueError(f'{field_name} debe ser una fecha/hora Oracle no nula')
    if value.tzinfo is not None:
        value = value.astimezone(LIMA_TZ).replace(tzinfo=None)
    return value


def text_value(value, name: str, maximum: int, required=False) -> Optional[str]:
    text = str(value).strip() if value is not None else None
    if required and not text:
        raise ValueError(f'{name} es obligatorio')
    if text and len(text) > maximum:
        raise ValueError(f'{name} supera {maximum} caracteres')
    return text or None


@dataclass(frozen=True)
class Notification:
    template_name: str
    incidencia: str
    fecha_inicio: dt.datetime
    numero_cliente: str
    nombre_cliente: str
    numero_destino: str
    nro_documento: Optional[str] = None
    fecha_estimada: Optional[dt.datetime] = None
    fecha_solucion: Optional[dt.datetime] = None

    @classmethod
    def from_row(cls, template_name: str, row: dict):
        estimated = row.get('fecha_estimada_solucion')
        solved = row.get('fecha_solucion')
        if template_name == 'averia_diagnosticada':
            estimated = oracle_datetime(estimated, 'fecha_estimada_solucion')
        if template_name == 'averia_solucionada':
            solved = oracle_datetime(solved, 'fecha_solucion')
        return cls(
            template_name=template_name,
            incidencia=text_value(row.get('incidencia'), 'incidencia', 128, True),
            fecha_inicio=oracle_datetime(row.get('fecha_inicio_averia'), 'fecha_inicio_averia'),
            numero_cliente=normalize_phone(row.get('numero_cliente')),
            nombre_cliente=text_value(row.get('nombre_cliente'), 'nombre_cliente', 256, True),
            numero_destino=recipient_phone(row.get('numero_cliente')),
            nro_documento=text_value(row.get('nro_documento'), 'nro_documento', 64),
            fecha_estimada=estimated,
            fecha_solucion=solved,
        )

    def payload(self) -> dict:
        if self.template_name == 'averia_diagnosticada':
            if self.fecha_estimada is None:
                raise ValueError('Falta fecha_estimada_solucion')
            hour = self.fecha_estimada.strftime('%I:%M')
            period = 'AM' if self.fecha_estimada.hour < 12 else 'PM'
            return build_payload(self.template_name, self.numero_destino, self.nombre_cliente, hour, period)
        return build_payload(self.template_name, self.numero_destino, self.nombre_cliente)
