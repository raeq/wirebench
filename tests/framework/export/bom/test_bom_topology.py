"""BOM topology cross-reference.

BOM doesn't carry per-port connectivity in the same way SPICE/KiCad
do — it lists parts, not nets. The cross-reference here is therefore
membership-based: the set of refdes-bearing components in the live
model must equal the set of refdes columns in the BOM (plus boards
on top, with the right parent attribution).

If a test fails because a renderer is missing or incorrect, the fix
is to add or correct the renderer — not to lower the assertion bar.
"""
from __future__ import annotations

import csv
import io
import warnings

import pytest

import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.export.bom  # noqa: F401

from framework.board import Board
from framework.chip import Chip
from framework.circuit import Circuit
from framework.connector import Connector
from framework.export import export_to_string
from framework.pin import Pin

from components.passives.led import LED
from components.passives.rail import Rail
from components.passives.resistor import Resistor

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


def _expected_bom_rows(design) -> set[tuple[str, str]]:
    """Walk the model and return {(refdes, parent_refdes)} for every
    component that belongs on the BOM."""
    out: set[tuple[str, str]] = set()

    def visit(node, parent: str) -> None:
        if isinstance(node, (Pin, Rail)):
            return
        if isinstance(node, Chip):
            out.add((node.refdes, parent))
            return
        if isinstance(node, Board):
            out.add((node.refdes, parent))
            for c in node._factor_nodes:
                visit(c, node.refdes)
            return
        if isinstance(node, Circuit):
            for c in node._factor_nodes:
                visit(c, parent)
            return
        rd = getattr(node, 'refdes', None)
        if rd:
            out.add((rd, parent))

    visit(design, '')
    return out


@pytest.mark.parametrize("factory", [
    WaterAlarm, WaterAlarmAssembly,
], ids=['WaterAlarm', 'WaterAlarmAssembly'])
def test_bom_refdes_set_matches_model(factory):
    design = _silently(factory)
    rows = list(csv.DictReader(io.StringIO(export_to_string(design, 'bom'))))
    actual = {(r['Refdes'], r['Parent']) for r in rows}
    expected = _expected_bom_rows(design)
    missing = expected - actual
    extra = actual - expected
    assert not missing and not extra, (
        f"BOM mismatch for {factory.__name__}:\n"
        f"  missing from BOM: {sorted(missing)}\n"
        f"  extra on BOM:     {sorted(extra)}"
    )
