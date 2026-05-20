"""`wirebench validate` — construct a Python-described design, emit JSON.

Usage:

    wirebench validate path/to/design.py
    wirebench validate path/to/design.py --class WaterAlarm

Exit codes:

    0 — design constructed cleanly       (status: constructed)
    1 — framework caught a defect        (status: failed)
    2 — validator couldn't run           (status: error)

Every well-formed validation outcome — success, framework refusal,
file-not-found, syntax error, missing target class, argparse usage
error — emits a single JSON object on stdout terminated with a
newline. Diagnostic text from the loaded design (prints, warnings) is
captured and discarded.

Construction-time exceptions outside the framework's known set
(`WirebenchError`, `ValueError`, `TypeError`) are re-raised as Python
tracebacks rather than wrapped into JSON — they signal a framework
bug or a non-design problem rather than a design defect, and surfacing
them loudly is the right behaviour for the operator.  See the spec
(`.plans/phase-1.5b-spec.md` §7 step 5) for rationale.
"""
from __future__ import annotations

import argparse
import importlib.util
import io
import json
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from typing import Any

# Trigger component registration so loaded designs see every class.
import components.chips        # noqa: F401
import components.passives     # noqa: F401
import components.connectors   # noqa: F401
import components.transducers  # noqa: F401
import framework.board         # noqa: F401

from framework import Circuit
from framework.errors import WirebenchError

from cli.validate_extractors import empty_details, extract


class _JSONArgumentParser(argparse.ArgumentParser):
    """argparse parser that emits a `status: error` JSON payload
    instead of writing to stderr + exiting silently.  Preserves the
    one-JSON-object-per-invocation contract on usage errors (missing
    positional, unknown flag, etc.)."""

    def error(self, message: str) -> None:  # type: ignore[override]
        _emit({
            'status':      'error',
            'design':      None,
            'error_class': 'UsageError',
            'message':     message,
            'details':     empty_details(),
        })
        raise SystemExit(2)


def _build_parser() -> argparse.ArgumentParser:
    parser = _JSONArgumentParser(
        prog='wirebench validate',
        description=(
            'Construct a Circuit subclass and emit a structured JSON '
            'report on whether the framework accepted it.'
        ),
    )
    parser.add_argument(
        'path',
        help='Python file containing a Circuit subclass to instantiate.',
    )
    parser.add_argument(
        '--class', dest='class_name', default=None,
        help=(
            'Name of the Circuit subclass to instantiate. Defaults to '
            'the first top-level Circuit subclass found in the file.'
        ),
    )
    return parser


def _emit(payload: dict[str, Any]) -> None:
    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write('\n')


def _details_with_remediation(e: WirebenchError) -> dict[str, Any]:
    """Build the `details` dict for a framework exception, merging the
    structured fields the regex extractor scrapes from the message with
    the high-confidence remediation hint the exception class produces
    (when one applies).  Omits the `remediation` key entirely when the
    class returned `None` — keeps the JSON shape minimal for the
    common low-confidence case."""
    details: dict[str, Any] = dict(extract(type(e).__name__, str(e)))
    remediation = e.suggested_remediation()
    if remediation is not None:
        details['remediation'] = remediation
    return details


def _error(message: str, error_class: str, *, design: str | None = None) -> int:
    _emit({
        'status':      'error',
        'design':      design,
        'error_class': error_class,
        'message':     message,
        'details':     empty_details(),
    })
    return 2


def _load_module(path: Path) -> Any:
    """Import `path` as a module under a synthetic name. Raises on
    FileNotFoundError / SyntaxError / ImportError so the caller can
    map those to `status: error`.

    The file's parent directory is prepended to `sys.path` during the
    load so designs that import sibling helper modules (a common
    pattern under `demos/<name>/`) resolve the same way as when the
    file is executed directly."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    spec = importlib.util.spec_from_file_location('_wirebench_validate', path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    parent_dir = str(path.resolve().parent)
    sys.path.insert(0, parent_dir)
    try:
        spec.loader.exec_module(module)
    finally:
        try:
            sys.path.remove(parent_dir)
        except ValueError:
            pass
    return module


def _find_circuit_classes(module: Any) -> list[type[Circuit]]:
    """Top-level Circuit subclasses defined in `module` itself
    (not re-imports). Ordered by source-file appearance."""
    candidates: list[type[Circuit]] = []
    for name in dir(module):
        obj = getattr(module, name)
        if not isinstance(obj, type):
            continue
        if not issubclass(obj, Circuit) or obj is Circuit:
            continue
        if getattr(obj, '__module__', None) != module.__name__:
            continue
        candidates.append(obj)
    candidates.sort(key=_class_source_line)
    return candidates


def _class_source_line(cls: type) -> int:
    """Best-effort source line of `cls`'s definition. Falls back to 0
    when inspect can't locate it (built-ins, dynamically-defined classes,
    etc.) — ordering then defaults to dir() order, which is good enough."""
    import inspect
    try:
        return inspect.getsourcelines(cls)[1]
    except (OSError, TypeError):
        return 0


def _select_target(
    candidates: list[type[Circuit]], class_name: str | None, path: Path,
) -> type[Circuit] | str:
    """Return the chosen class, or an error-message string."""
    if class_name is not None:
        for cls in candidates:
            if cls.__name__ == class_name:
                return cls
        return (
            f"Class {class_name!r} not found in {path} "
            f"(found: {[c.__name__ for c in candidates] or 'none'})"
        )
    if not candidates:
        return f"No Circuit subclass found in {path}"
    if len(candidates) > 1:
        names = ', '.join(c.__name__ for c in candidates)
        return (
            f"Multiple Circuit subclasses found in {path} "
            f"({names}); use --class NAME to pick one"
        )
    return candidates[0]


def run_validate(argv: list[str]) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    path = Path(args.path)

    sink = io.StringIO()

    try:
        with redirect_stdout(sink), redirect_stderr(sink):
            module = _load_module(path)
    except FileNotFoundError as e:
        return _error(str(e), type(e).__name__)
    except SyntaxError as e:
        return _error(str(e), type(e).__name__)
    except ImportError as e:
        return _error(str(e), type(e).__name__)
    except Exception as e:
        return _error(str(e), type(e).__name__)

    candidates = _find_circuit_classes(module)
    target = _select_target(candidates, args.class_name, path)
    if isinstance(target, str):
        return _error(target, 'NoTargetError')

    try:
        with redirect_stdout(sink), redirect_stderr(sink):
            design = target()
    except WirebenchError as e:
        sys.stderr.write(traceback.format_exc())
        _emit({
            'status':      'failed',
            'design':      target.__name__,
            'error_class': type(e).__name__,
            'message':     str(e),
            'details':     _details_with_remediation(e),
        })
        return 1
    except (ValueError, TypeError) as e:
        sys.stderr.write(traceback.format_exc())
        _emit({
            'status':      'failed',
            'design':      target.__name__,
            'error_class': type(e).__name__,
            'message':     str(e),
            'details':     extract(type(e).__name__, str(e)),
        })
        return 1

    parts = getattr(design, 'parts', ())
    _emit({
        'status':   'constructed',
        'design':   target.__name__,
        'parts':    len(parts),
        'warnings': [],
    })
    return 0


def main(argv: list[str] | None = None) -> int:
    return run_validate(list(sys.argv[1:] if argv is None else argv))


if __name__ == '__main__':
    raise SystemExit(main())
