from __future__ import annotations

import json
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from src.ips_spam.models import SyncMetrics


LIMA_TZ = ZoneInfo('America/Lima')


class IpsSpamLoadService:
    def __init__(
        self,
        rsync_extractor,
        html_extractor,
        list_parser,
        asn_parser,
        repository=None,
        now_provider=None,
    ):
        self.rsync_extractor = rsync_extractor
        self.html_extractor = html_extractor
        self.list_parser = list_parser
        self.asn_parser = asn_parser
        self.repository = repository
        self.now_provider = now_provider or (lambda: datetime.now(LIMA_TZ))

    def execute(
        self,
        sources,
        extract_only: bool = False,
        skip_download: bool = False,
        full_download: bool = False,
        sample_size: int = 0,
    ):
        results = {}
        for source in sources:
            run_id = uuid.uuid4()
            started_at = self.now_provider()
            source_rows = 0
            print(
                f'SOURCE_START source={source.key} '
                f'target={source.target_table}'
            )
            try:
                data = self._extract_and_parse(
                    source,
                    skip_download=skip_download,
                    full_download=full_download,
                )
                source_rows = len(data)
                if extract_only:
                    metrics = SyncMetrics(
                        source_rows=source_rows,
                        inserted=0,
                        updated=0,
                        deleted=0,
                        unchanged=0,
                    )
                elif source.kind == 'asn':
                    metrics = self.repository.sync_asn(
                        source.target_table,
                        data,
                        started_at,
                    )
                else:
                    metrics = self.repository.sync_values(
                        source.target_table,
                        data,
                        started_at,
                    )

                finished_at = self.now_provider()
                if not extract_only:
                    self.repository.insert_audit(
                        run_id=run_id,
                        source=source.key,
                        target_table=source.target_table,
                        started_at=started_at,
                        finished_at=finished_at,
                        status='SUCCESS',
                        metrics=metrics,
                    )
                result = {
                    'status': 'EXTRACTED' if extract_only else 'SUCCESS',
                    **metrics.to_dict(),
                }
                if sample_size > 0:
                    result['sample'] = [
                        self._sample_value(item)
                        for item in data[:sample_size]
                    ]
                results[source.key] = result
                print(
                    'SOURCE_RESULT '
                    + json.dumps(
                        {'source': source.key, **result},
                        ensure_ascii=False,
                        sort_keys=True,
                        default=str,
                    )
                )
            except BaseException as error:
                finished_at = self.now_provider()
                if not extract_only and self.repository is not None:
                    try:
                        self.repository.insert_audit(
                            run_id=run_id,
                            source=source.key,
                            target_table=source.target_table,
                            started_at=started_at,
                            finished_at=finished_at,
                            status='ERROR',
                            metrics=SyncMetrics(
                                source_rows=source_rows,
                                inserted=0,
                                updated=0,
                                deleted=0,
                                unchanged=0,
                            ),
                            error_detail=str(error)[:8000],
                        )
                    except BaseException as audit_error:
                        print(f'AUDIT_ERROR source={source.key}: {audit_error}')
                raise

        summary = {
            'status': 'SUCCESS',
            'extract_only': extract_only,
            'sources': results,
            'source_count': len(results),
        }
        print(
            'LOAD_RESULT '
            + json.dumps(
                summary,
                ensure_ascii=False,
                sort_keys=True,
                default=str,
            )
        )
        return summary

    def _extract_and_parse(
        self,
        source,
        skip_download: bool,
        full_download: bool,
    ):
        if source.kind == 'asn':
            path = (
                self.html_extractor.local_path()
                if skip_download
                else self.html_extractor.extract()
            )
            return self.asn_parser.parse(path)

        path = (
            self.rsync_extractor.local_path(source)
            if skip_download
            else self.rsync_extractor.extract(
                source,
                full_download=full_download,
            )
        )
        return self.list_parser.parse(path)

    @staticmethod
    def _sample_value(item):
        if hasattr(item, 'to_clickhouse_row'):
            return item.to_clickhouse_row()
        return item
