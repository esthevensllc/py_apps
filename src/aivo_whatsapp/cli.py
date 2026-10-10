from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

from dotenv import load_dotenv

from .service import AivoClient, AivoError, AivoSettings, TEMPLATES, build_payload
from .repository import OracleLogError, OracleRepository, OracleTestRepository, connect_oracle
from .workflow import run_batch


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
    parser.add_argument('--from-oracle', action='store_true', help='Lee las consultas y envía con reserva persistente en Oracle')
    parser.add_argument('--test-to', help='Redirige únicamente esta prueba manual al celular indicado')
    parser.add_argument('--test-id', help='Identificador de ronda; repetirlo conserva el bloqueo por destino y plantilla')
    parser.add_argument('--fecha-desde', default='2026-10-08', help='Fecha mínima de petición del diagnóstico, YYYY-MM-DD')
    parser.add_argument('--limit', type=int, default=100, help='Máximo de filas consultadas por plantilla (1 a 1000)')
    args = parser.parse_args(argv)
    if args.test_to is not None or args.test_id is not None:
        if not args.from_oracle or args.check_auth or not args.test_to or not args.test_id:
            parser.error('--test-to y --test-id deben usarse juntos con --from-oracle')
    if args.check_auth:
        if args.from_oracle or args.dry_run or any(value is not None for value in (
            args.plantilla, args.to, args.nombre, args.hora, args.periodo,
        )):
            parser.error('--check-auth no se combina con opciones de envío ni --dry-run')
    elif args.from_oracle:
        if any(value is not None for value in (args.to, args.nombre, args.hora, args.periodo)):
            parser.error('--from-oracle obtiene celular, nombre y hora desde las consultas')
    else:
        missing = [name for name in ('plantilla', 'to', 'nombre') if getattr(args, name) is None]
        if missing:
            parser.error('Faltan argumentos: ' + ', '.join('--' + name for name in missing))
    try:
        if not args.check_auth and not args.from_oracle:
            payload = build_payload(args.plantilla, args.to, args.nombre, args.hora, args.periodo)
        if args.dry_run and not args.from_oracle:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0
        if not args.check_auth and not args.from_oracle:
            raise ValueError('El envío directo está deshabilitado para evitar duplicados. Use --from-oracle con el log creado.')
        if not args.env_file.is_file() and args.env_file != Path(__file__).with_name('.env'):
            raise ValueError(f'No existe el archivo de configuración: {args.env_file}')
        load_dotenv(args.env_file, override=False)
        client = None if args.dry_run else AivoClient(AivoSettings.from_environment())
        if args.from_oracle:
            fecha_desde = dt.datetime.strptime(args.fecha_desde, '%Y-%m-%d')
            if not 1 <= args.limit <= 1000:
                raise ValueError('--limit debe estar entre 1 y 1000')
            connection, driver = connect_oracle()
            try:
                repository = (
                    OracleTestRepository(connection, driver, args.test_to, args.test_id)
                    if args.test_to else OracleRepository(connection, driver)
                )
                result = run_batch(
                    repository, client, args.plantilla,
                    fecha_desde, args.limit, args.dry_run,
                )
            finally:
                connection.close()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 1 if result['errores'] or result['invalidos'] else 0
        if args.check_auth:
            client.authenticate()
            print(json.dumps({'autenticacion_correcta': True}))
            return 0
    except (ValueError, AivoError, OSError, OracleLogError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
