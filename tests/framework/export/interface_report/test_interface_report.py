"""Interface report renderer — output regression + sanity tests.

Mirrors `tests/framework/export/net_report/` — the per-demo
`docs/<Class>.interface-report.md` files are the golden source.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[4]
_DEMOS = _REPO / 'demos'
if str(_DEMOS) not in sys.path:
    sys.path.insert(0, str(_DEMOS))
for _d in sorted(_DEMOS.iterdir()):
    if _d.is_dir() and not _d.name.startswith('_') and str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

import components.chips        # noqa: F401, E402
import components.passives     # noqa: F401, E402
import components.connectors   # noqa: F401, E402
import components.diodes       # noqa: F401, E402
import components.transistors  # noqa: F401, E402
import framework.export.interface_report  # noqa: F401, E402

from framework.circuit import Circuit  # noqa: E402
from framework.export import export_to_string  # noqa: E402


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


def _construct(cls):
    try:
        return _silently(cls)
    except Exception:
        try:
            return _silently(cls, refdes_number=1)
        except Exception:
            return None


def _iter_golden_pairs():
    for demo_dir in sorted(_DEMOS.iterdir()):
        if not demo_dir.is_dir() or demo_dir.name.startswith('_'):
            continue
        docs = demo_dir / 'docs'
        if not docs.is_dir():
            continue
        for py_file in sorted(demo_dir.glob('*.py')):
            if py_file.name.startswith('_'):
                continue
            mod_name = py_file.stem
            try:
                mod = __import__(mod_name)
            except Exception:
                continue
            for name in sorted(dir(mod)):
                obj = getattr(mod, name)
                if not (isinstance(obj, type)
                        and issubclass(obj, Circuit)
                        and obj.__module__ == mod_name):
                    continue
                golden = docs / f"{name}.interface-report.md"
                if golden.exists():
                    yield demo_dir.name, name, obj, golden


@pytest.mark.parametrize(
    "demo,class_name,cls,golden",
    list(_iter_golden_pairs()),
    ids=lambda x: x if isinstance(x, str) else getattr(x, '__name__', repr(x)),
)
def test_interface_report_matches_committed_demo_output(
    demo, class_name, cls, golden,
):
    design = _construct(cls)
    if design is None:
        pytest.skip(f"{class_name} cannot be constructed without args")
    actual = export_to_string(design, 'interface_report')
    expected = golden.read_text()
    assert actual == expected, (
        f"{demo}/{class_name}.interface-report.md drift — re-run "
        f"`uv run python scripts/render_demo_docs.py` to refresh."
    )


# ----------------------------------------------------- structural sanity


def test_design_without_boards_emits_no_connector_table():
    from hello_led import HelloLED
    out = export_to_string(_silently(HelloLED), 'interface_report')
    assert "no `Board` subclasses" in out


def test_multi_board_design_lists_each_board():
    from isolated_rs232 import IsolatedRS232Link
    out = export_to_string(_silently(IsolatedRS232Link), 'interface_report')
    assert "Board: `ControllerSourceBoard` (A1)" in out
    assert "Board: `IsolatedRS232Board` (A2)" in out
    assert "Board: `RS232CableBoard` (A3)" in out


def test_mated_pairs_surface_at_document_head():
    from isolated_rs232 import IsolatedRS232Link
    out = export_to_string(_silently(IsolatedRS232Link), 'interface_report')
    assert "Mating pairs:" in out
    assert "A1.P1 mates with A2.J1" in out


def test_supply_pin_labelled_as_supply():
    from fan_cooling import CooledSystem
    out = export_to_string(_silently(CooledSystem), 'interface_report')
    assert "+ supply" in out
    assert "− supply" in out
