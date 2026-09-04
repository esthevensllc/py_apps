from __future__ import annotations

import datetime as dt
import posixpath
import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


DEFAULT_FAMILIES: Mapping[str, int] = {
    'PM_IG27_5': 5,
    'PM_IG30028_15': 15,
    'PM_IG64_15': 15,
    'PM_IG30227_15': 15,
    'PM_IG4090_5': 5,
    'PM_IG30014_15': 15,
    'PM_IG11_5': 5,
    'PM_IG4090_15': 15,
    'PM_IG30029_15': 15,
    'PM_IG7106_5': 5,
    'PM_IG7413_15': 15,
    'PM_IG1_5': 5,
    'PM_IG3_15': 15,
    'PM_IG27_15': 15,
    'PM_IG45046_5': 5,
    'PM_IG45027_15': 15,
}


@dataclass(frozen=True)
class ManifestItem:
    family: str
    timestamp: dt.datetime
    filename: str
    remote_dir: str
    suffix: Optional[str] = None

    @property
    def remote_path(self) -> str:
        return posixpath.join(self.remote_dir, self.filename)


@dataclass(frozen=True)
class ManifestSummary:
    items: Tuple[ManifestItem, ...]
    expected_groups: Tuple[Tuple[str, dt.datetime], ...]
    missing_groups: Tuple[Tuple[str, dt.datetime], ...]
    unexpected_groups: Tuple[Tuple[str, dt.datetime], ...]

    @property
    def actual_groups(self) -> Tuple[Tuple[str, dt.datetime], ...]:
        return tuple(sorted({(item.family, item.timestamp) for item in self.items}))

    @property
    def files_by_family(self) -> Dict[str, int]:
        return dict(Counter(item.family for item in self.items))


class NCEFileSelector:
    def __init__(self, families: Mapping[str, int] = DEFAULT_FAMILIES):
        if len(families) == 0:
            raise ValueError('Se requiere al menos una familia de archivos')

        self.families = dict(families)
        family_expression = '|'.join(
            re.escape(family)
            for family in sorted(self.families, key=len, reverse=True)
        )
        self.filename_pattern = re.compile(
            rf'^(?P<family>{family_expression})_'
            rf'(?P<timestamp>[0-9]{{12}})'
            rf'(?:_(?P<suffix>[0-9]+))?\.csv$',
            re.IGNORECASE,
        )
        self.canonical_families = {
            family.lower(): family for family in self.families
        }

    def parse(
        self,
        filename: str,
        remote_dir: str,
    ) -> Optional[ManifestItem]:
        match = self.filename_pattern.fullmatch(filename)
        if match is None:
            return None

        try:
            timestamp = dt.datetime.strptime(
                match.group('timestamp'),
                '%Y%m%d%H%M',
            )
        except ValueError:
            return None

        family = self.canonical_families[match.group('family').lower()]
        return ManifestItem(
            family=family,
            timestamp=timestamp,
            filename=filename,
            remote_dir=remote_dir.rstrip('/'),
            suffix=match.group('suffix'),
        )

    def select(
        self,
        filenames_by_directory: Mapping[str, Iterable[str]],
        start: dt.datetime,
        end: dt.datetime,
    ) -> ManifestSummary:
        if start >= end:
            raise ValueError('La fecha inicial debe ser menor que la fecha final')

        items: List[ManifestItem] = []
        for remote_dir, filenames in filenames_by_directory.items():
            for filename in filenames:
                item = self.parse(filename, remote_dir)
                if item is not None and start <= item.timestamp < end:
                    items.append(item)

        items.sort(
            key=lambda item: (
                item.timestamp,
                item.family,
                item.filename,
            )
        )

        expected = set(self.expected_groups(start, end))
        actual = {(item.family, item.timestamp) for item in items}

        return ManifestSummary(
            items=tuple(items),
            expected_groups=tuple(sorted(expected)),
            missing_groups=tuple(sorted(expected - actual)),
            unexpected_groups=tuple(sorted(actual - expected)),
        )

    def expected_groups(
        self,
        start: dt.datetime,
        end: dt.datetime,
    ) -> Sequence[Tuple[str, dt.datetime]]:
        groups: List[Tuple[str, dt.datetime]] = []
        for family, granularity in self.families.items():
            cursor = self._ceil_to_granularity(start, granularity)
            while cursor < end:
                groups.append((family, cursor))
                cursor += dt.timedelta(minutes=granularity)
        return groups

    @staticmethod
    def _ceil_to_granularity(
        value: dt.datetime,
        granularity: int,
    ) -> dt.datetime:
        minute_floor = value.replace(second=0, microsecond=0)
        minutes_since_midnight = minute_floor.hour * 60 + minute_floor.minute
        remainder = minutes_since_midnight % granularity

        if remainder != 0:
            minute_floor += dt.timedelta(minutes=granularity - remainder)

        if value.second != 0 or value.microsecond != 0:
            if minute_floor <= value:
                minute_floor += dt.timedelta(minutes=granularity)

        return minute_floor
