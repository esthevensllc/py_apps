from __future__ import annotations

import datetime as dt
import json
import posixpath
from collections import defaultdict
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from src.nce_recarga.selector import ManifestItem, ManifestSummary, NCEFileSelector


class NCERecargaValidationError(Exception):
    pass


class NCERecargaService:
    def __init__(self, load_csv, remote_root: str, selector=None):
        self.load_csv = load_csv
        self.sftp_service = load_csv.sftp_service
        self.remote_root = remote_root.rstrip('/')
        self.selector = selector or NCEFileSelector()

    def execute(
        self,
        start: dt.datetime,
        end: dt.datetime,
        dry_run: bool = True,
        strict: bool = True,
        emit_success_events: bool = True,
    ) -> Mapping[str, object]:
        if start >= end:
            raise NCERecargaValidationError(
                'La fecha inicial debe ser menor que la fecha final'
            )

        filenames_by_directory = self._list_directories(start, end)
        manifest = self.selector.select(filenames_by_directory, start, end)
        self._print_manifest_summary(manifest, start, end)

        if len(manifest.items) == 0:
            raise NCERecargaValidationError(
                'No se encontraron archivos para el rango y familias solicitados'
            )

        if strict and len(manifest.missing_groups) > 0:
            first_missing = ', '.join(
                f'{family}@{timestamp:%Y-%m-%d %H:%M}'
                for family, timestamp in manifest.missing_groups[:20]
            )
            raise NCERecargaValidationError(
                f'Faltan {len(manifest.missing_groups)} grupos esperados. '
                f'Primeros faltantes: {first_missing}'
            )

        if dry_run:
            for item in manifest.items:
                print(
                    f'FILE {item.family} {item.timestamp:%Y-%m-%d %H:%M} '
                    f'{item.remote_path}'
                )
            print('DRY_RUN: manifiesto validado; no se descargaron ni cargaron archivos')
            return self._result(manifest, loaded_groups=0, loaded_files=0)

        grouped_items = self._group_items(manifest.items)
        loaded_groups = 0
        loaded_files = 0
        total_groups = len(grouped_items)

        for (timestamp, family), items in grouped_items:
            filenames = [item.filename for item in items]
            remote_dirs = {item.remote_dir for item in items}
            if len(remote_dirs) != 1:
                raise NCERecargaValidationError(
                    f'El grupo {family}@{timestamp} aparece en varias rutas'
                )

            remote_dir = next(iter(remote_dirs))
            queue_id = f'nce.{family}_min'.lower()
            print(
                f'LOAD {loaded_groups + 1}/{total_groups}: '
                f'{family} {timestamp:%Y-%m-%d %H:%M} '
                f'({len(filenames)} archivo(s))'
            )
            self.load_csv.execute(
                queue_id,
                [family],
                timestamp,
                'mxm',
                remote_dir=remote_dir,
                filenames=filenames,
                emit_success_event=emit_success_events,
            )
            loaded_groups += 1
            loaded_files += len(filenames)

        result = self._result(manifest, loaded_groups, loaded_files)
        print('RESULT ' + json.dumps(result, ensure_ascii=False, sort_keys=True))
        return result

    def _list_directories(
        self,
        start: dt.datetime,
        end: dt.datetime,
    ) -> Dict[str, Sequence[str]]:
        directories: Dict[str, Sequence[str]] = {}
        for day in self._iter_days(start, end):
            str_day = day.strftime('%Y%m%d')
            remote_dir = posixpath.join(self.remote_root, str_day, str_day)
            print(f'LIST {remote_dir}')
            try:
                directories[remote_dir] = self.sftp_service.get_filenames(
                    remote_dir,
                    r'.*\.csv$',
                )
            except Exception as error:
                raise NCERecargaValidationError(
                    f'No se pudo listar el directorio remoto {remote_dir}: {error}'
                ) from error
        return directories

    @staticmethod
    def _iter_days(
        start: dt.datetime,
        end: dt.datetime,
    ) -> Iterable[dt.datetime]:
        cursor = start.replace(hour=0, minute=0, second=0, microsecond=0)
        last_included = end - dt.timedelta(microseconds=1)
        last_day = last_included.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        while cursor <= last_day:
            yield cursor
            cursor += dt.timedelta(days=1)

    @staticmethod
    def _group_items(
        items: Sequence[ManifestItem],
    ) -> List[Tuple[Tuple[dt.datetime, str], List[ManifestItem]]]:
        groups: Dict[Tuple[dt.datetime, str], List[ManifestItem]] = defaultdict(list)
        for item in items:
            groups[(item.timestamp, item.family)].append(item)
        return sorted(groups.items(), key=lambda group: group[0])

    def _print_manifest_summary(
        self,
        manifest: ManifestSummary,
        start: dt.datetime,
        end: dt.datetime,
    ) -> None:
        print(
            f'RANGE [{start:%Y-%m-%d %H:%M:%S}, '
            f'{end:%Y-%m-%d %H:%M:%S})'
        )
        print(
            f'MANIFEST files={len(manifest.items)} '
            f'actual_groups={len(manifest.actual_groups)} '
            f'expected_groups={len(manifest.expected_groups)} '
            f'missing_groups={len(manifest.missing_groups)} '
            f'unexpected_groups={len(manifest.unexpected_groups)}'
        )
        for family in self.selector.families:
            print(
                f'FAMILY {family} '
                f'files={manifest.files_by_family.get(family, 0)}'
            )

    @staticmethod
    def _result(
        manifest: ManifestSummary,
        loaded_groups: int,
        loaded_files: int,
    ) -> Mapping[str, object]:
        return {
            'manifest_files': len(manifest.items),
            'actual_groups': len(manifest.actual_groups),
            'expected_groups': len(manifest.expected_groups),
            'missing_groups': len(manifest.missing_groups),
            'unexpected_groups': len(manifest.unexpected_groups),
            'loaded_groups': loaded_groups,
            'loaded_files': loaded_files,
        }
