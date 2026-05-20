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
import components.chips        # noqa: F401
import components.passives     # noqa: F401
import components.connectors   # noqa: F401
import components.transducers  # noqa: F401
import framework.board         # noqa: F401

from framework.export import export_to_string, list_formats
from framework.format import load_wirebench


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='wirebench export',
        description='Export a .wirebench design to a netlist or schematic format.',
    )
    parser.add_argument(
        'input', nargs='?',
        help='Path to a .wirebench design file.',
    )
    parser.add_argument(
        '--format', '-f',
        help='Target format (e.g. "spice").',
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path. Stdout if omitted.',
    )
    parser.add_argument(
        '--list-formats', action='store_true',
        help='Print available formats and exit.',
    )
    return parser


def run_export(argv: list[str]) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

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
