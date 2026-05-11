"""Per-component DOT renderer tests.

If a test fails because a renderer is missing or incorrect, the fix
is to add or correct the renderer — not to lower the assertion bar.
No `pytest.skip`, `xfail`, "current behaviour", "TODO: tighten", or
relaxed regex unless there's a specific in-spec deferral.
"""
from __future__ import annotations

import re
import warnings

import pytest

import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.export.dot  # noqa: F401

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


# ---------------------------------------------------------------------------
# Per-component
# ---------------------------------------------------------------------------

def test_dot_resistor_node_declaration():
    r = Resistor(330, refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    text = export_to_string(Circuit(factor_nodes=[r, vcc, gnd], ports={}), 'dot')
    assert re.search(r'^\s*R1 \[label="R1\\\\n330Ω"\];', text, flags=re.M)


def test_dot_led_node_includes_color():
    d = LED('red', refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], d.ports['anode'])
    wire(d.ports['cathode'], gnd.ports['out'])
    text = export_to_string(Circuit(factor_nodes=[d, vcc, gnd], ports={}), 'dot')
    assert re.search(r'D1 \[label="D1\\\\nred LED"\];', text)


def test_dot_chip_node_uses_class_name():
    u = SN74HC04(refdes_number=1)
    text = export_to_string(Circuit(factor_nodes=[u], ports={}), 'dot')
    assert re.search(r'U1 \[label="U1\\\\nSN74HC04"\];', text)


def test_dot_connectors_emit_no_node():
    """Per §5.2: connectors are conductors, collapsed into nets."""
    j = Header2xNFemale(pin_count=2, pitch_mm=2.54, refdes_number=1)
    text = export_to_string(Circuit(factor_nodes=[j], ports={}), 'dot')
    assert 'J1 [label=' not in text


def test_dot_rail_emits_no_node():
    """Rails get inlined into vcc/gnd net names; no separate node."""
    r = Resistor(100, refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    text = export_to_string(Circuit(factor_nodes=[r, vcc, gnd], ports={}), 'dot')
    # No Rail box; 'vcc' and 'gnd' appear only as nets in the circle line.
    assert 'Rail' not in text
    assert 'vcc' in text and 'gnd' in text


def test_dot_header_directives_present():
    text = export_to_string(
        Circuit(factor_nodes=[Resistor(100, refdes_number=1)], ports={}),
        'dot')
    assert text.startswith('digraph "')
    assert 'rankdir=LR;' in text
    assert text.rstrip().endswith('}')


def test_dot_nets_emitted_as_circle_nodes():
    r = Resistor(330, refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    text = export_to_string(Circuit(factor_nodes=[r, vcc, gnd], ports={}), 'dot')
    assert 'node [shape=circle' in text
    assert 'vcc' in text
    assert 'gnd' in text


def test_dot_edges_have_port_taillabels():
    d = LED('red', refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], d.ports['anode'])
    wire(d.ports['cathode'], gnd.ports['out'])
    text = export_to_string(Circuit(factor_nodes=[d, vcc, gnd], ports={}), 'dot')
    # Edge from D1 with taillabel "anode" or "cathode".
    assert re.search(r'D1 -> \S+ \[taillabel="anode"\];', text)
    assert re.search(r'D1 -> \S+ \[taillabel="cathode"\];', text)


def test_dot_board_becomes_subgraph_cluster():
    r = Resistor(330, refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    b = Board(name='Tiny', revision='A',
              components=[r, vcc, gnd], refdes_number=1)
    asm = Circuit(factor_nodes=[b], ports={})
    text = export_to_string(asm, 'dot')
    assert 'subgraph cluster_A1' in text
    assert 'Tiny' in text
    assert 'Rev A' in text


def test_dot_chip_pin_edge_uses_chip_port_name():
    u = SN74HC04(refdes_number=1)
    d = LED('red', refdes_number=1)
    gnd = Rail(False)
    # Drive a_1 from gnd, route y_1 through an LED to gnd.
    wire(gnd.ports['out'], u.ports['a_1'])
    wire(u.ports['y_1'], d.ports['anode'])
    wire(d.ports['cathode'], gnd.ports['out'])
    text = export_to_string(Circuit(factor_nodes=[u, d, gnd], ports={}), 'dot')
    assert re.search(r'U1 -> \S+ \[taillabel="a_1"\];', text)
    assert re.search(r'U1 -> \S+ \[taillabel="y_1"\];', text)


def test_dot_water_alarm_assembly_emits_two_clusters():
    asm = _silently(WaterAlarmAssembly)
    text = export_to_string(asm, 'dot')
    assert text.count('subgraph cluster_A1') == 1
    assert text.count('subgraph cluster_A2') == 1
