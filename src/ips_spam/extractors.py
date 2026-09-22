from __future__ import annotations

import gzip
import os
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, List, Sequence
from urllib.parse import urlparse
from urllib.request import ProxyHandler, Request, build_opener, urlopen

from src.ips_spam.models import AsnRecord, SourceDefinition


class RsyncExtractor:
    def __init__(
        self,
        storage_dir: Path,
        remote_base: str,
        binary: str = 'rsync',
        timeout_seconds: int = 180,
        proxy_url: str = '',
    ):
        self.storage_dir = Path(storage_dir)
        self.remote_base = remote_base.rstrip('/')
        self.binary = binary
        self.timeout_seconds = int(timeout_seconds)
        self.proxy_url = proxy_url.strip()

    def local_path(self, source: SourceDefinition) -> Path:
        return self.storage_dir / 'rsync' / source.key

    def extract(
        self,
        source: SourceDefinition,
        full_download: bool = False,
    ) -> Path:
        destination = self.local_path(source)
        destination.mkdir(parents=True, exist_ok=True)
        command = [
            self.binary,
            '-az',
            '--delete',
            f'--timeout={self.timeout_seconds}',
        ]
        if full_download:
            command.extend(['--ignore-times', '--whole-file'])
        command.extend(
            [
                f'{self.remote_base}/{source.remote_name}',
                str(destination) + '/',
            ]
        )
        print(
            f'RSYNC_START source={source.key} remote={source.remote_name} '
            f"destination={destination} proxy={'enabled' if self.proxy_url else 'disabled'}"
        )
        try:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds + 60,
                env=self._environment(),
            )
        except FileNotFoundError as error:
            raise RuntimeError(
                f'No se encontró el ejecutable rsync: {self.binary}'
            ) from error
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(
                f'Rsync excedió el timeout para {source.key}'
            ) from error
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or '').strip()
            raise RuntimeError(
                f'Rsync falló para {source.key} con código '
                f'{result.returncode}: {detail[-2000:]}'
            )
        print(f'RSYNC_OK source={source.key}')
        return destination

    def _environment(self):
        environment = os.environ.copy()
        if self.proxy_url:
            environment['RSYNC_PROXY'] = self._proxy_endpoint()
        return environment

    def _proxy_endpoint(self) -> str:
        proxy_url = self.proxy_url
        if '://' not in proxy_url:
            proxy_url = f'http://{proxy_url}'
        parsed = urlparse(proxy_url)
        if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
            raise RuntimeError(
                'UCEPROTECT_RSYNC_PROXY debe tener formato host:puerto o URL HTTP'
            )
        return parsed.netloc


class HtmlExtractor:
    def __init__(
        self,
        storage_dir: Path,
        url: str,
        timeout_seconds: int = 60,
        user_agent: str = 'py_apps-ips-spam/1.0',
        http_proxy: str = '',
        https_proxy: str = '',
    ):
        self.storage_dir = Path(storage_dir)
        self.url = url
        self.timeout_seconds = int(timeout_seconds)
        self.user_agent = user_agent
        self.http_proxy = http_proxy.strip()
        self.https_proxy = https_proxy.strip()

    def local_path(self) -> Path:
        return self.storage_dir / 'html' / 'l3charts.html'

    def extract(self) -> Path:
        destination = self.local_path()
        destination.parent.mkdir(parents=True, exist_ok=True)
        request = Request(
            self.url,
            headers={
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml',
            },
        )
        print(
            'HTTP_START source=asn '
            f"url={self.url} proxy={'enabled' if self.https_proxy else 'disabled'}"
        )
        try:
            opener = self._opener()
            with opener.open(request, timeout=self.timeout_seconds) as response:
                payload = response.read()
                charset = response.headers.get_content_charset() or 'utf-8'
        except OSError as error:
            raise RuntimeError(
                f'No se pudo descargar la tabla ASN desde {self.url}: {error}'
            ) from error
        html = payload.decode(charset, errors='replace')
        destination.write_text(html, encoding='utf-8')
        print(f'HTTP_OK source=asn bytes={len(payload)}')
        return destination

    def _opener(self):
        proxies = {}
        if self.http_proxy:
            proxies['http'] = self.http_proxy
        if self.https_proxy:
            proxies['https'] = self.https_proxy
        return build_opener(ProxyHandler(proxies)) if proxies else _UrlOpener()


class _UrlOpener:
    @staticmethod
    def open(request, timeout):
        return urlopen(request, timeout=timeout)


class RsyncListParser:
    SKIPPED_PREFIXES = ('#', ';', '$', ':')

    def parse(self, path: Path) -> List[str]:
        files = [item for item in Path(path).rglob('*') if item.is_file()]
        if not files:
            raise RuntimeError(f'No se encontraron archivos en {path}')
        values = set()
        for file_path in files:
            for line in self._read_lines(file_path):
                value = self._parse_line(line)
                if value:
                    values.add(value)
        if not values:
            raise RuntimeError(
                f'La fuente {path} no contiene registros válidos'
            )
        return sorted(values)

    @staticmethod
    def _read_lines(file_path: Path) -> Iterable[str]:
        opener = gzip.open if file_path.suffix.lower() == '.gz' else open
        with opener(file_path, mode='rt', encoding='utf-8', errors='replace') as stream:
            yield from stream

    def _parse_line(self, raw_line: str) -> str:
        line = raw_line.lstrip('\ufeff').strip()
        if not line or line.startswith(self.SKIPPED_PREFIXES):
            return ''
        line = line.split('#', 1)[0].strip()
        if not line:
            return ''
        return line.split(None, 1)[0].strip()


class _ChartTableParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self._row = None
        self._cell = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == 'tr':
            self._row = []
        elif tag in {'td', 'th'} and self._row is not None:
            self._cell = []
        elif tag == 'img' and self._cell is not None:
            attributes = dict(attrs)
            self._cell.extend(
                str(attributes.get(name, ''))
                for name in ('src', 'alt', 'title')
                if attributes.get(name)
            )

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in {'td', 'th'} and self._cell is not None:
            value = ' '.join(' '.join(self._cell).split())
            self._row.append(value)
            self._cell = None
        elif tag == 'tr' and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None
            self._cell = None


class AsnChartParser:
    ASN_PATTERN = re.compile(r'\bAS\s*(\d+)\b', re.IGNORECASE)

    def parse(self, path: Path) -> List[AsnRecord]:
        html = Path(path).read_text(encoding='utf-8', errors='replace')
        parser = _ChartTableParser()
        parser.feed(html)
        records = {}
        for cells in parser.rows:
            record = self._parse_row(cells)
            if record is None:
                continue
            previous = records.get(record.asn)
            if previous is None or record.posicion < previous.posicion:
                records[record.asn] = record
        if not records:
            raise RuntimeError(
                'No se encontraron filas ASN válidas en l3charts.php; '
                'revise si cambió la estructura HTML'
            )
        return sorted(records.values(), key=lambda item: item.posicion)

    def _parse_row(self, cells: Sequence[str]):
        asn_index = None
        asn_number = None
        for index, cell in enumerate(cells):
            match = self.ASN_PATTERN.search(cell)
            if match:
                asn_index = index
                asn_number = match.group(1)
                break
        if asn_index is None or asn_index < 4:
            return None
        try:
            position = self._parse_integer(cells[0])
            spam_score = self._parse_decimal(cells[asn_index - 3])
            impacts = self._parse_integer(cells[asn_index - 2])
        except ValueError:
            return None
        provider = cells[asn_index - 1].strip()
        if not provider:
            return None
        trend = self._parse_trend(cells[asn_index - 4])
        return AsnRecord(
            posicion=position,
            tendencia=trend,
            spam_score=spam_score,
            impactos=impacts,
            proveedor=provider,
            asn=f'AS{asn_number}',
        )

    @staticmethod
    def _parse_integer(value: str) -> int:
        match = re.search(r'-?\d[\d.,]*', value)
        if not match:
            raise ValueError(value)
        return int(re.sub(r'[^0-9-]', '', match.group(0)))

    @staticmethod
    def _parse_decimal(value: str) -> float:
        match = re.search(r'-?\d[\d.,]*', value)
        if not match:
            raise ValueError(value)
        number = match.group(0)
        if ',' in number and '.' in number:
            if number.rfind(',') > number.rfind('.'):
                number = number.replace('.', '').replace(',', '.')
            else:
                number = number.replace(',', '')
        elif ',' in number:
            number = number.replace(',', '.')
        return float(number)

    @staticmethod
    def _parse_trend(value: str) -> str:
        normalized = value.lower()
        if any(token in normalized for token in ('up', 'hoch', 'rise')):
            return 'UP'
        if any(token in normalized for token in ('down', 'runter', 'fall')):
            return 'DOWN'
        if any(token in normalized for token in ('same', 'gleich', 'equal')):
            return 'SAME'
        return 'UNKNOWN'
