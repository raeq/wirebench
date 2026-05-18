"""`wirebench import-kicad` — convert a KiCad `.net` file into a
wirebench Circuit (or a Python source file describing one).

Two modes:

  --emit python   (default) — write a `.py` file that constructs the
                              imported circuit; user can edit and run.
  --emit circuit            — instantiate the circuit in-process and
                              emit a JSON report (same shape as
                              `wirebench validate`).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from framework.errors import LoadError, UnknownPartError, WirebenchError


class _CLIParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        sys.stderr.write(f"wirebench import-kicad: error: {message}\n")
        raise SystemExit(2)


def _build_parser() -> argparse.ArgumentParser:
    parser = _CLIParser(
        prog='wirebench import-kicad',
        description='Convert a KiCad .net file into a wirebench Circuit.',
    )
    parser.add_argument('input', help='Path to a KiCad-exported .net file.')
    parser.add_argument(
        '--emit', choices=['python', 'circuit'], default='python',
        help='Output mode (default: python).',
    )
    parser.add_argument(
        '--strict', action='store_true',
        help='Raise on unmapped KiCad parts instead of substituting '
             'UnknownPart placeholders.',
    )
    parser.add_argument(
        '--output', '-o',
        help='Output path (default: <input-stem>.py for --emit python; '
             'stdout for --emit circuit).',
    )
    parser.add_argument(
        '--class-name', default=None,
        help='Name of the generated Circuit subclass '
             '(default: <InputStem>Imported).',
    )
    return parser


def run_import_kicad(argv: list[str]) -> int:
    args = _build_parser().parse_args(argv)
    input_path = Path(args.input)

    if not input_path.exists():
        sys.stderr.write(f"wirebench import-kicad: file not found: {input_path}\n")
        return 2

    # Defer the import so the CLI module can be loaded without a
    # full framework import (keeps `--help` cheap and decouples test
    # collection from registry side-effects).
    from framework.import_kicad import import_kicad_netlist
    from framework.import_kicad.emit_python import emit

    try:
        circuit, report = import_kicad_netlist(input_path, strict=args.strict)
    except UnknownPartError as e:
        sys.stderr.write(f"wirebench import-kicad: {e}\n")
        return 1
    except LoadError as e:
        # LoadError covers parse failures *and* missing-section
        # / instantiation errors re-wrapped from deeper in the
        # import pipeline.  Use a neutral verb so the message
        # doesn't mislead users about which stage failed.
        sys.stderr.write(f"wirebench import-kicad: import failed: {e}\n")
        return 2
    except WirebenchError as e:
        sys.stderr.write(
            f"wirebench import-kicad: framework refused the imported "
            f"circuit ({type(e).__name__}): {e}\n"
        )
        return 1

    if args.emit == 'circuit':
        payload = _circuit_payload(circuit, report)
        out_path = Path(args.output) if args.output else None
        if out_path:
            out_path.write_text(json.dumps(payload, indent=2) + '\n')
        else:
            json.dump(payload, sys.stdout, indent=2)
            sys.stdout.write('\n')
        return 0

    class_name = args.class_name or _default_class_name(input_path)
    source = emit(report, class_name=class_name, source_path=str(input_path))
    out_path = Path(args.output) if args.output else input_path.with_suffix('.py')
    out_path.write_text(source)

    print(f"Wrote {out_path} — {len(report.parts)} parts, "
          f"{len(report.nets)} nets.")
    if report.unresolved:
        print(
            f"{len(report.unresolved)} KiCad parts had no wirebench "
            f"equivalent (re-run with --strict to fail on these):"
        )
        for ref in report.unresolved:
            print(f"  - {ref} → UnknownPart placeholder")
    return 0


def _default_class_name(input_path: Path) -> str:
    """Sanitise the input stem into a valid Python identifier while
    preserving its existing capitalisation — `HelloLED.net` stays
    `HelloLED` (not `Helloled` from a `.title()` pass) and produces
    `HelloLEDImported`."""
    stem = ''.join(c for c in input_path.stem if c.isalnum() or c == '_')
    if not stem:
        return 'Imported'
    if not stem[0].isalpha():
        stem = 'Imported' + stem
    # Strip underscores at boundaries so the suffix concatenation
    # doesn't look like `Hello_LedImported`; underscores inside are
    # preserved verbatim (no `.title()` — we keep the user's case).
    return stem.replace('_', '') + 'Imported'


def _circuit_payload(circuit: Any, report: Any) -> dict[str, Any]:
    return {
        'status':     'constructed',
        'parts':      len(circuit.parts),
        'nets':       len(report.nets),
        'unresolved': report.unresolved,
        'skipped_nets': report.skipped_nets,
    }


def main(argv: list[str] | None = None) -> int:
    return run_import_kicad(list(sys.argv[1:] if argv is None else argv))


if __name__ == '__main__':
    raise SystemExit(main())
