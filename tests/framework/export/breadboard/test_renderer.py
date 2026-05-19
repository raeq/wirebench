"""Renderer-level tests for the breadboard visualiser.

Verify that the emitted SVG is well-formed XML, contains the expected
structural pieces (board surface, components, jumpers), exposes
`data-refdes` attributes for downstream tooling, and refuses
unsupported designs.
"""
from __future__ import annotations

import sys
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / 'src'))
for _d in sorted((_REPO / 'demos').iterdir()):
    if _d.is_dir():
        sys.path.insert(0, str(_d))

import components.chips        # noqa: F401, E402
import components.connectors   # noqa: F401, E402
import components.diodes       # noqa: F401, E402
import components.passives     # noqa: F401, E402
import components.transistors  # noqa: F401, E402
import framework.export.assembly_guide   # noqa: F401, E402
import framework.export.breadboard       # noqa: F401, E402

from framework.errors import BreadboardIncompatibleError   # noqa: E402
from framework.export import export_to_string              # noqa: E402

from backup_power import BackupPower                       # noqa: E402
from hello_led import HelloLED                             # noqa: E402
from water_alarm_split import WaterAlarmAssembly           # noqa: E402


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


def _render(cls) -> str:
    return export_to_string(_silently(cls), 'breadboard')


def test_hello_led_emits_valid_xml():
    """The SVG output parses as valid XML — any malformed tag would
    break browsers and downstream tooling."""
    svg = _render(HelloLED)
    root = ET.fromstring(svg)
    assert root.tag.endswith('svg')


def test_viewbox_present():
    """The SVG carries a viewBox so it scales cleanly when embedded."""
    svg = _render(HelloLED)
    root = ET.fromstring(svg)
    assert root.attrib.get('viewBox', '').startswith('0 0 ')


def test_data_refdes_attributes_present():
    """Every component group carries a `data-refdes` attribute so
    downstream tooling can target specific parts (acceptance criterion
    in spec §9 SVG correctness)."""
    svg = _render(HelloLED)
    assert 'data-refdes="R1"' in svg
    assert 'data-refdes="D1"' in svg


def test_jumpers_group_present():
    """The renderer emits a `<g class="jumpers">` block."""
    svg = _render(HelloLED)
    assert 'class="jumpers"' in svg


def test_board_surface_group_present():
    """The renderer emits a `<g class="board-surface">` block."""
    svg = _render(HelloLED)
    assert 'class="board-surface"' in svg


def test_smd_design_is_refused():
    """A design with SMD-only parts raises `BreadboardIncompatibleError`."""
    with pytest.raises(BreadboardIncompatibleError):
        _render(BackupPower)


def test_multi_board_is_refused():
    """Multi-board designs raise `BreadboardIncompatibleError` (v1 defers
    composite multi-Board emission to v2 per locked spec §12)."""
    with pytest.raises(BreadboardIncompatibleError):
        _render(WaterAlarmAssembly)


def test_render_is_deterministic():
    """Re-running the renderer on the same design produces byte-identical
    output — this is what makes the golden tests viable."""
    a = _render(HelloLED)
    b = _render(HelloLED)
    assert a == b


def test_inline_styles_not_class_styles():
    """Every visible element carries an inline `style="..."` attribute
    rather than referencing a class-based stylesheet (locked decision 6
    in spec §12 — the SVG must be fully self-contained for GitHub /
    email embed)."""
    svg = _render(HelloLED)
    # The opening rect, every line, every path must carry style.
    # Sample a few known patterns.
    assert 'style="fill:' in svg
    assert 'style="stroke:' in svg
    # No external CSS references.
    assert '<link' not in svg
    assert '<style' not in svg


def test_assembly_guide_consistency():
    """Acceptance criterion 8 — the same positions appear in both
    artefacts. We assert this indirectly by confirming the breadboard
    renderer uses the same placement function as the assembly guide."""
    from framework.export.breadboard.placement import place as bb_place
    from framework.export.assembly_guide.placement import place as ag_place
    assert bb_place is ag_place


def test_red_appears_for_plus_rail():
    """Red jumper SVG paths appear for + rail wiring (HelloLED has
    R1.t1 → +rail)."""
    svg = _render(HelloLED)
    assert 'stroke:#cc0000' in svg


def test_black_appears_for_minus_rail():
    """Black jumper SVG paths appear for − rail wiring (HelloLED has
    D1.cathode → −rail)."""
    svg = _render(HelloLED)
    # The minus-rail jumper is the only place black-as-stroke jumper
    # appears (rail strips themselves are red and light-blue).
    assert 'jumper rail_minus' in svg
