"""Per-component Yosys JSON renderer tests.

If a test fails because a renderer is missing or incorrect, the fix
is to add or correct the renderer — not to lower the assertion bar.
No `pytest.skip`, `xfail`, "current behaviour", "TODO: tighten", or
relaxed regex unless there's a specific in-spec deferral.
"""
from __future__ import annotations

import json
import warnings

import pytest

import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.export.yosys  # noqa: F401

from framework.circuit import Circuit
from framework.export import export_to_string
from framework.wire import wire

from components.chips.sn74hc04 import SN74HC04
from components.connectors.headers import Header2xNFemale
from components.passives.led import LED
from components.passives.rail import Rail
from components.passives.resistor import Resistor

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


def _doc(design):
    return json.loads(export_to_string(design, 'yosys'))


def test_yosys_top_level_shape():
    d = _doc(_silently(WaterAlarm))
    assert d['creator'].startswith('wirebench')
    assert 'modules' in d


def test_yosys_one_module_per_design_when_no_boards():
    d = _doc(_silently(WaterAlarm))
    assert list(d['modules'].keys()) == ['WaterAlarm']


def test_yosys_resistor_cell():
    r = Resistor(330, refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    d = _doc(Circuit(factor_nodes=[r, vcc, gnd], ports={}))
    cells = next(iter(d['modules'].values()))['cells']
    assert 'R1' in cells
    assert cells['R1']['type'] == 'Resistor'
    assert cells['R1']['parameters']['ohms'] == '330'
    assert set(cells['R1']['connections'].keys()) == {'t1', 't2'}


def test_yosys_led_cell_carries_color_parameter():
    d = LED('red', refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], d.ports['anode'])
    wire(d.ports['cathode'], gnd.ports['out'])
    doc = _doc(Circuit(factor_nodes=[d, vcc, gnd], ports={}))
    cell = next(iter(doc['modules'].values()))['cells']['D1']
    assert cell['type'] == 'LED'
    assert cell['parameters']['color'] == 'red'


def test_yosys_chip_cell_has_all_pins():
    u = SN74HC04(refdes_number=1)
    cells = _doc(Circuit(factor_nodes=[u], ports={}))['modules']['Circuit']['cells']
    chip = cells['U1']
    assert chip['type'] == 'SN74HC04'
    # All 12 chip pins present.
    for i in range(1, 7):
        assert f'a_{i}' in chip['connections']
        assert f'y_{i}' in chip['connections']
    # Directions correct: a_* are inputs, y_* are outputs.
    assert chip['port_directions']['a_1'] == 'input'
    assert chip['port_directions']['y_1'] == 'output'


def test_yosys_connector_emitted_as_cell():
    j = Header2xNFemale(pin_count=2, pitch_mm=2.54, refdes_number=1)
    cells = _doc(Circuit(factor_nodes=[j], ports={}))['modules']['Circuit']['cells']
    assert 'J1' in cells
    # Connector pins use 'inout' direction (BIDIR).
    assert all(d == 'inout' for d in cells['J1']['port_directions'].values())


def test_yosys_assembly_has_per_board_modules():
    asm = _silently(WaterAlarmAssembly)
    doc = _doc(asm)
    modules = doc['modules']
    # Top-level + one per board.
    assert 'WaterAlarmAssembly' in modules or 'Circuit' in modules
    # Each Board contributes a module named '<ClassName>_A1' / '_A2'.
    board_modules = [m for m in modules if m.startswith(('SensorBoard_', 'ControllerBoard_'))]
    assert len(board_modules) == 2


def test_yosys_bit_ids_are_integers_starting_at_2():
    asm = _silently(WaterAlarm)
    doc = _doc(asm)
    cells = doc['modules']['WaterAlarm']['cells']
    for cell in cells.values():
        for bits in cell['connections'].values():
            assert isinstance(bits, list)
            assert all(isinstance(b, int) and b >= 2 for b in bits)


def test_yosys_netnames_present_for_vcc_and_gnd():
    asm = _silently(WaterAlarm)
    doc = _doc(asm)
    netnames = doc['modules']['WaterAlarm']['netnames']
    assert 'vcc' in netnames
    assert 'GND' in netnames


def test_yosys_output_is_deterministic():
    text1 = export_to_string(_silently(WaterAlarm), 'yosys')
    text2 = export_to_string(_silently(WaterAlarm), 'yosys')
    assert text1 == text2


def test_yosys_sorted_keys():
    """JSON output uses sort_keys=True so cell/port order is stable."""
    asm = _silently(WaterAlarmAssembly)
    text = export_to_string(asm, 'yosys')
    # `cells` map keys appear in alphabetical order in the text.
    idx_d1 = text.find('"D1"')
    idx_u1 = text.find('"U1"')
    if idx_d1 != -1 and idx_u1 != -1:
        assert idx_d1 < idx_u1   # D < U alphabetically
