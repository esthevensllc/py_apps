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
    parser.add_argument('--plantilla', choices=tuple(TEMPLATES))
    parser.add_argument('--to', help='Número de celular en el formato aceptado por Aivo')
    parser.add_argument('--nombre')
    parser.add_argument('--hora', help='Hora en formato hh:mm, requerida para averia_diagnosticada')
    parser.add_argument('--periodo', type=str.upper, choices=('AM', 'PM'))
    parser.add_argument('--env-file', type=Path, default=Path(__file__).with_name('.env'))
    parser.add_argument('--dry-run', action='store_true', help='Muestra el JSON sin autenticar ni enviar')
    parser.add_argument('--check-auth', action='store_true', help='Prueba la autenticación sin enviar mensajes ni mostrar el token')
    args = parser.parse_args(argv)
    if args.check_auth:
        if args.dry_run or any(value is not None for value in (
            args.plantilla, args.to, args.nombre, args.hora, args.periodo,
        )):
            parser.error('--check-auth no se combina con opciones de envío ni --dry-run')
    else:
        missing = [name for name in ('plantilla', 'to', 'nombre') if getattr(args, name) is None]
        if missing:
            parser.error('Faltan argumentos: ' + ', '.join('--' + name for name in missing))
    try:
        if not args.check_auth:
            payload = build_payload(args.plantilla, args.to, args.nombre, args.hora, args.periodo)
        if args.dry_run:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0
        if not args.env_file.is_file() and args.env_file != Path(__file__).with_name('.env'):
            raise ValueError(f'No existe el archivo de configuración: {args.env_file}')
        load_dotenv(args.env_file, override=False)
        client = AivoClient(AivoSettings.from_environment())
        if args.check_auth:
            client.authenticate()
            print(json.dumps({'autenticacion_correcta': True}))
            return 0
        result = client.send_message(args.plantilla, args.to, args.nombre, args.hora, args.periodo)
        print(json.dumps({'solicitud_aceptada': True, 'respuesta': result}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, AivoError, OSError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
