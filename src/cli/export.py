"""`wirebench export` — CLI front-end for the export framework.

Usage:

    wirebench export design.wirebench --format spice --output design.cir
    wirebench export design.wirebench --format spice           # stdout
    wirebench export --list-formats
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Trigger component registration so the loader recognises every class.
import components.chips      # noqa: F401
import components.passives   # noqa: F401
import components.connectors # noqa: F401
import framework.board       # noqa: F401

from framework.export import export_to_string, list_formats
from framework.format import load_wirebench


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='wirebench',
        description='Export a .wirebench design to a netlist or schematic format.',
    )
    sub = parser.add_subparsers(dest='cmd')

    p_export = sub.add_parser('export', help='Export a design.')
    p_export.add_argument(
        'input', nargs='?',
        help='Path to a .wirebench design file.',
    )
    p_export.add_argument(
        '--format', '-f',
        help='Target format (e.g. "spice").',
    )
    p_export.add_argument(
        '--output', '-o',
        help='Output file path. Stdout if omitted.',
    )
    p_export.add_argument(
        '--list-formats', action='store_true',
        help='Print available formats and exit.',
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.cmd != 'export':
        parser.print_help()
        return 1

    if args.list_formats:
        for fmt in list_formats():
            print(fmt)
        return 0

    if not args.input:
        parser.error('input file is required (or use --list-formats)')
    if not args.format:
        parser.error('--format is required')

    design = load_wirebench(Path(args.input))
    text = export_to_string(design, args.format)

    if args.output:
        Path(args.output).write_text(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
