from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class SourceDefinition:
    key: str
    kind: str
    target_table: str
    remote_name: str = ''


@dataclass(frozen=True)
class AsnRecord:
    posicion: int
    tendencia: str
    spam_score: float
    impactos: int
    proveedor: str
    asn: str

    def to_clickhouse_row(self) -> Tuple[object, ...]:
        return (
            self.posicion,
            self.tendencia,
            self.spam_score,
            self.impactos,
            self.proveedor,
            self.asn,
        )


@dataclass(frozen=True)
class SyncMetrics:
    source_rows: int
    inserted: int
    updated: int
    deleted: int
    unchanged: int

    def to_dict(self):
        return {
            'source_rows': self.source_rows,
            'inserted': self.inserted,
            'updated': self.updated,
            'deleted': self.deleted,
            'unchanged': self.unchanged,
        }
