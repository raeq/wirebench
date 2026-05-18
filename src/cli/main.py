"""`wirebench` — top-level CLI dispatcher.

Three subcommands:

    wirebench export   ...    Export a .wirebench design to a netlist format.
    wirebench validate ...    Construct a Python-described design and emit
                              a structured JSON report on whether the
                              framework accepted it.
    wirebench parts    ...    List every component the framework models.

Each subcommand owns its own module; this file is the dispatcher that
parses the leading subcommand and hands off.
"""
from __future__ import annotations

import sys

from cli.export   import run_export
from cli.parts    import run_parts
from cli.validate import run_validate


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

    _print_usage()
    return 2


def _print_usage() -> None:
    print(
        'usage: wirebench <command> [<args>]\n'
        '\n'
        'commands:\n'
        '  export      Export a .wirebench design to a netlist format.\n'
        '  validate    Validate a Python-described design; emit JSON report.\n'
        '  parts       List every component the framework models.\n',
        file=sys.stderr,
    )


if __name__ == '__main__':
    raise SystemExit(main())
