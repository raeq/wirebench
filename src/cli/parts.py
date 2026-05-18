"""`wirebench parts` — list every component the framework models.

Default form (no filters): every registered part, one per line,
aligned in four columns: refdes prefix, class name, module path,
one-line description.

Filters compose with AND.  See `parts_data.PartDescriptor` for the
field set surfaced to consumers via `--json`.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from cli.parts_data import (
    KNOWN_KINDS, PartDescriptor, all_parts, filter_parts,
)
from framework.pin_function import PinFunction

# Surface PinFunction names (the enum's member identifiers — POWER,
# GROUND, …) so `--pin-function` errors loudly on typos rather than
# silently returning an empty catalogue.
_KNOWN_PIN_FUNCTIONS = sorted(member.name for member in PinFunction)


class _JSONArgumentParser(argparse.ArgumentParser):
    """Same shape as the validate-CLI parser: usage errors emit a
    diagnostic line on stderr and exit 2, instead of dumping a full
    argparse stack trace."""

    def error(self, message: str) -> None:  # type: ignore[override]
        sys.stderr.write(f"wirebench parts: error: {message}\n")
        raise SystemExit(2)


def _build_parser() -> argparse.ArgumentParser:
    parser = _JSONArgumentParser(
        prog='wirebench parts',
        description=(
            'List every component the framework models. '
            'Filters compose with AND.'
        ),
    )
    parser.add_argument(
        'subcommand', nargs='?', default='list',
        choices=['list'],
        help='Subcommand (only "list" supported in v1).',
    )
    parser.add_argument(
        '--prefix',
        help='Only parts whose REFDES_PREFIX matches (e.g. "R").',
    )
    parser.add_argument(
        '--kind', choices=sorted(KNOWN_KINDS),
        help='Only parts of the given kind.',
    )
    parser.add_argument(
        '--has-cell', action='store_true',
        help='Only chips with a behavioural cell.',
    )
    parser.add_argument(
        '--has-footprint', action='store_true',
        help='Only parts with a KiCad footprint declared.',
    )
    parser.add_argument(
        '--pin-function',
        type=str.upper,  # case-insensitive entry, store as canonical name
        choices=_KNOWN_PIN_FUNCTIONS,
        help=(
            'Only parts that expose pins with this function. '
            f"One of: {', '.join(_KNOWN_PIN_FUNCTIONS)}."
        ),
    )
    parser.add_argument(
        '--json', dest='as_json', action='store_true',
        help='Emit JSON instead of aligned text.',
    )
    return parser


def _format_table(parts: list[PartDescriptor]) -> str:
    """Four-column aligned text, one part per line."""
    if not parts:
        return ""
    rows = [
        (
            p['refdes_prefix'] or '—',
            p['class_name'],
            p['module'],
            p['description'],
        )
        for p in parts
    ]
    widths = [max(len(r[c]) for r in rows) for c in range(4)]
    lines = [
        f"{r[0]:<{widths[0]}}  "
        f"{r[1]:<{widths[1]}}  "
        f"{r[2]:<{widths[2]}}  "
        f"{r[3]}"
        for r in rows
    ]
    return "\n".join(lines)


def run_parts(argv: list[str]) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    parts = all_parts()
    parts = filter_parts(
        parts,
        prefix=args.prefix,
        kind=args.kind,
        has_cell=args.has_cell,
        has_footprint=args.has_footprint,
        pin_function=args.pin_function,
    )

    if args.as_json:
        json.dump(parts, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    table = _format_table(parts)
    if table:
        sys.stdout.write(table + "\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    return run_parts(list(sys.argv[1:] if argv is None else argv))


if __name__ == '__main__':
    raise SystemExit(main())
