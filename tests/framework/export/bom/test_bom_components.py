"""Per-component BOM renderer tests.

If a test fails because a renderer is missing or incorrect, the fix
is to add or correct the renderer — not to lower the assertion bar.
No `pytest.skip`, `xfail`, "current behaviour", "TODO: tighten", or
relaxed regex unless there's a specific in-spec deferral with a
tracked follow-on.
"""
from __future__ import annotations

import csv
import io
import warnings

import pytest

# Trigger registrations.
import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.export.bom  # noqa: F401

from framework.board import Board
from framework.circuit import Circuit
from framework.export import export_to_string
from framework.wire import wire

from components.chips.sn74hc04 import SN74HC04
from components.connectors.headers import Header2xNFemale
from components.passives.led import LED
from components.passives.rail import Rail
from components.passives.resistor import Resistor

from water_alarm_split import WaterAlarmAssembly


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


def _rows(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text)))


# ---------------------------------------------------------------------------
# Per-component
# ---------------------------------------------------------------------------

def test_bom_resistor_row():
    r = Resistor(330, refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    text = export_to_string(Circuit(factor_nodes=[r, vcc, gnd], ports={}), 'bom')
    rows = _rows(text)
    [row] = [r for r in rows if r['Refdes'] == 'R1']
    assert row['Value'].startswith('330')
    assert row['Footprint'] == 'Resistor_SMD:R_0603_1608Metric'
    assert row['Quantity'] == '1'
    assert row['Parent'] == ''


def test_bom_led_row_uses_color_as_value():
    d = LED('red', refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], d.ports['anode'])
    wire(d.ports['cathode'], gnd.ports['out'])
    [row] = [r for r in _rows(export_to_string(
        Circuit(factor_nodes=[d, vcc, gnd], ports={}), 'bom'))
        if r['Refdes'] == 'D1']
    assert row['Value'] == 'red LED'
    assert row['Footprint'] == 'LED_SMD:LED_0805'


def test_bom_chip_row_value_is_class_name():
    u = SN74HC04(refdes_number=1)
    [row] = [r for r in _rows(export_to_string(
        Circuit(factor_nodes=[u], ports={}), 'bom'))
        if r['Refdes'] == 'U1']
    assert row['Value'] == 'SN74HC04'
    assert row['Footprint'] == 'Package_DIP:DIP-14_W7.62mm'


def test_bom_connector_is_on_bom():
    """Connectors are real parts — they must appear on the BOM."""
    conn = Header2xNFemale(pin_count=2, pitch_mm=2.54, refdes_number=1)
    rows = _rows(export_to_string(
        Circuit(factor_nodes=[conn], ports={}), 'bom'))
    assert any(r['Refdes'] == 'J1' for r in rows)
    [j1] = [r for r in rows if r['Refdes'] == 'J1']
    assert 'Header2xNFemale' in j1['Value']
    assert 'PinHeader_2x' in j1['Footprint']


def test_bom_rail_not_on_bom():
    """Rails are logical markers, not procurable parts."""
    r = Resistor(1000, refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    rows = _rows(export_to_string(
        Circuit(factor_nodes=[r, vcc, gnd], ports={}), 'bom'))
    # No row referencing 'Rail' as a value or refdes.
    assert all('Rail' not in row['Value'] for row in rows)


def test_bom_chip_cells_not_separately_listed():
    """Chips' internal cells (NORLatch, DarlingtonChannel) are private
    implementation — never separately on the BOM."""
    u = SN74HC04(refdes_number=1)
    rows = _rows(export_to_string(
        Circuit(factor_nodes=[u], ports={}), 'bom'))
    # Only one refdes-bearing row: the chip itself.
    refdesed = [r for r in rows if r['Refdes']]
    assert len(refdesed) == 1
    assert refdesed[0]['Refdes'] == 'U1'


# ---------------------------------------------------------------------------
# Board hierarchy
# ---------------------------------------------------------------------------

def test_bom_board_row_appears():
    r = Resistor(330, refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    b = Board(name='Tiny', revision='A',
              components=[r, vcc, gnd], refdes_number=1)
    asm = Circuit(factor_nodes=[b], ports={})
    rows = _rows(export_to_string(asm, 'bom'))
    [a1] = [r for r in rows if r['Refdes'] == 'A1']
    assert 'Tiny' in a1['Value']
    assert 'Rev A' in a1['Value']


def test_bom_child_components_have_parent_column():
    asm = _silently(WaterAlarmAssembly)
    rows = _rows(export_to_string(asm, 'bom'))
    # Every component inside A1 or A2 has the corresponding Parent.
    parents = {r['Refdes']: r['Parent'] for r in rows}
    assert parents['A1'] == ''
    assert parents['A2'] == ''
    # U1 appears twice — once per board.
    u1_parents = [r['Parent'] for r in rows if r['Refdes'] == 'U1']
    assert set(u1_parents) == {'A1', 'A2'}


def test_bom_rows_sorted_by_refdes_class():
    """Refdes prefix order: A, R, C, L, D, Q, U, J, P, ... — boards
    and passives first, then ICs, then connectors."""
    asm = _silently(WaterAlarmAssembly)
    rows = _rows(export_to_string(asm, 'bom'))
    prefixes = []
    for r in rows:
        p = r['Refdes'].rstrip('0123456789')
        if not prefixes or prefixes[-1] != p:
            prefixes.append(p)
    # Assemblies come before LEDs come before ICs come before connectors.
    assert prefixes.index('A') < prefixes.index('D') < prefixes.index('U')
    assert prefixes.index('U') < prefixes.index('J')
    assert prefixes.index('J') < prefixes.index('P')


def test_bom_header_columns():
    text = export_to_string(
        Circuit(factor_nodes=[Resistor(100, refdes_number=1)], ports={}), 'bom')
    first_line = text.splitlines()[0]
    assert first_line == 'Refdes,Value,Footprint,Quantity,Parent,Description'


def test_bom_water_alarm_has_no_pin_cell_or_rail():
    from water_alarm import WaterAlarm
    rows = _rows(export_to_string(_silently(WaterAlarm), 'bom'))
    for r in rows:
        val = r['Value'].lower()
        assert 'pin' not in val
        assert 'rail' not in val
        assert 'inverter' not in val   # cell, not a part
        assert 'norlatch' not in val
