"""Domain report renderer — output regression + sanity tests.

Mirrors `tests/framework/export/net_report/` — the per-demo
`docs/<Class>.domain-report.md` files are the golden source.
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
import framework.export.domain_report  # noqa: F401, E402

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
                golden = docs / f"{name}.domain-report.md"
                if golden.exists():
                    yield demo_dir.name, name, obj, golden


@pytest.mark.parametrize(
    "demo,class_name,cls,golden",
    list(_iter_golden_pairs()),
    ids=lambda x: x if isinstance(x, str) else getattr(x, '__name__', repr(x)),
)
def test_domain_report_matches_committed_demo_output(
    demo, class_name, cls, golden,
):
    design = _construct(cls)
    if design is None:
        pytest.skip(f"{class_name} cannot be constructed without args")
    actual = export_to_string(design, 'domain_report')
    expected = golden.read_text()
    assert actual == expected, (
        f"{demo}/{class_name}.domain-report.md drift — re-run "
        f"`uv run python scripts/render_demo_docs.py` to refresh."
    )


# ----------------------------------------------------- structural sanity


def test_single_domain_design_shows_no_crossings():
    from hello_led import HelloLED
    out = export_to_string(_silently(HelloLED), 'domain_report')
    assert "1 ground domain(s)" in out
    assert "Boundaries to other domains: None" in out


def test_multi_domain_design_detects_isolator_crossings():
    from isolated_rs232 import IsolatedRS232Link
    out = export_to_string(_silently(IsolatedRS232Link), 'domain_report')
    assert "2 ground domain(s)" in out
    assert "ELECTRICAL" in out
    assert "ISOLATED_RS232" in out
    # The ISOW7841 bridges both domains and should appear under both
    # `Boundaries to other domains` sections.
    assert "crossed via U1 (`ISOW7841`)" in out
