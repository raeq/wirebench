"""`wirebench` — top-level CLI dispatcher.

Four subcommands:

    wirebench export        Export a .wirebench design to a netlist format.
    wirebench validate      Construct a Python-described design and emit
                            a structured JSON report on whether the
                            framework accepted it.
    wirebench parts         List every component the framework models.
    wirebench import-kicad  Convert a KiCad .net file to wirebench Python.

Each subcommand owns its own module; this file is the dispatcher that
parses the leading subcommand and hands off.
"""
from __future__ import annotations

import sys

from cli.export       import run_export
from cli.import_kicad import run_import_kicad
from cli.parts        import run_parts
from cli.validate     import run_validate


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ('-h', '--help'):
        _print_usage()
        return 0 if args else 1

    cmd, rest = args[0], args[1:]
    if cmd == 'export':
        return run_export(rest)
    if cmd == 'validate':
        return run_validate(rest)
    if cmd == 'parts':
        return run_parts(rest)
    if cmd == 'import-kicad':
        return run_import_kicad(rest)

    _print_usage()
    return 2


def _print_usage() -> None:
    print(
        'usage: wirebench <command> [<args>]\n'
        '\n'
        'commands:\n'
        '  export         Export a .wirebench design to a netlist format.\n'
        '  validate       Validate a Python-described design; emit JSON report.\n'
        '  parts          List every component the framework models.\n'
        '  import-kicad   Convert a KiCad .net file to wirebench Python.\n',
        file=sys.stderr,
    )


if __name__ == '__main__':
    raise SystemExit(main())
