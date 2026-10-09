from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

from dotenv import load_dotenv

from .service import AivoClient, AivoError, AivoSettings, TEMPLATES, build_payload


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description='Solicita el envío de una plantilla WhatsApp mediante Aivo')
    parser.add_argument('--plantilla', required=True, choices=tuple(TEMPLATES))
    parser.add_argument('--to', required=True, help='Número de celular en el formato aceptado por Aivo')
    parser.add_argument('--nombre', required=True)
    parser.add_argument('--hora', help='Hora en formato hh:mm, requerida para averia_diagnosticada')
    parser.add_argument('--periodo', type=str.upper, choices=('AM', 'PM'))
    parser.add_argument('--env-file', type=Path, default=Path(__file__).with_name('.env'))
    parser.add_argument('--dry-run', action='store_true', help='Muestra el JSON sin autenticar ni enviar')
    args = parser.parse_args(argv)
    try:
        payload = build_payload(args.plantilla, args.to, args.nombre, args.hora, args.periodo)
        if args.dry_run:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0
        if not args.env_file.is_file() and args.env_file != Path(__file__).with_name('.env'):
            raise ValueError(f'No existe el archivo de configuración: {args.env_file}')
        load_dotenv(args.env_file, override=False)
        client = AivoClient(AivoSettings.from_environment())
        result = client.send_message(args.plantilla, args.to, args.nombre, args.hora, args.periodo)
        print(json.dumps({'solicitud_aceptada': True, 'respuesta': result}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, AivoError, OSError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
