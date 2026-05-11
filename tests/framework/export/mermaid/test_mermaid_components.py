"""Per-component Mermaid renderer tests.

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
import framework.export.mermaid  # noqa: F401

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


def test_mermaid_init_directive_and_flowchart_type():
    text = export_to_string(
        Circuit(factor_nodes=[Resistor(100, refdes_number=1)], ports={}),
        'mermaid')
    assert text.startswith('%%{init:')
    assert '\nflowchart LR' in text


def test_mermaid_resistor_node():
    r = Resistor(330, refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    text = export_to_string(Circuit(factor_nodes=[r, vcc, gnd], ports={}), 'mermaid')
    assert 'R1["R1<br/>330Ω"]' in text


def test_mermaid_led_node():
    d = LED('red', refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], d.ports['anode'])
    wire(d.ports['cathode'], gnd.ports['out'])
    text = export_to_string(Circuit(factor_nodes=[d, vcc, gnd], ports={}), 'mermaid')
    assert 'D1["D1<br/>red LED"]' in text


def test_mermaid_chip_node():
    u = SN74HC04(refdes_number=1)
    text = export_to_string(Circuit(factor_nodes=[u], ports={}), 'mermaid')
    assert 'U1["U1<br/>SN74HC04"]' in text


def test_mermaid_no_connector_node():
    j = Header2xNFemale(pin_count=2, pitch_mm=2.54, refdes_number=1)
    text = export_to_string(Circuit(factor_nodes=[j], ports={}), 'mermaid')
    assert 'J1[' not in text


def test_mermaid_no_rail_node():
    r = Resistor(100, refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    text = export_to_string(Circuit(factor_nodes=[r, vcc, gnd], ports={}), 'mermaid')
    assert 'Rail' not in text


def test_mermaid_net_is_double_circle():
    r = Resistor(100, refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    text = export_to_string(Circuit(factor_nodes=[r, vcc, gnd], ports={}), 'mermaid')
    assert 'vcc(("vcc"))' in text
    assert 'gnd(("gnd"))' in text


def test_mermaid_edge_includes_port_name():
    d = LED('red', refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], d.ports['anode'])
    wire(d.ports['cathode'], gnd.ports['out'])
    text = export_to_string(Circuit(factor_nodes=[d, vcc, gnd], ports={}), 'mermaid')
    assert re.search(r'D1 ---\|"anode"\| \S+', text)
    assert re.search(r'D1 ---\|"cathode"\| \S+', text)


def test_mermaid_board_becomes_subgraph():
    r = Resistor(100, refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    b = Board(name='Tiny', revision='A',
              components=[r, vcc, gnd], refdes_number=1)
    text = export_to_string(Circuit(factor_nodes=[b], ports={}), 'mermaid')
    assert re.search(r'subgraph A1\["A1: Tiny Rev A"\]', text)
    assert '\n    end\n' in text


def test_mermaid_water_alarm_assembly_has_two_subgraphs():
    asm = _silently(WaterAlarmAssembly)
    text = export_to_string(asm, 'mermaid')
    assert text.count('subgraph A1[') == 1
    assert text.count('subgraph A2[') == 1


def test_mermaid_html_escape_in_label():
    """Labels embed `<br/>` for newlines — must not be escaped."""
    d = LED('red', refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], d.ports['anode'])
    wire(d.ports['cathode'], gnd.ports['out'])
    text = export_to_string(Circuit(factor_nodes=[d, vcc, gnd], ports={}), 'mermaid')
    assert '<br/>' in text
