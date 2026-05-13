"""Per-component KiCad renderer tests.

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
import framework.export.kicad  # noqa: F401

from framework.board import Board
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


def test_kicad_header_directives():
    r = Resistor(330, refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    text = export_to_string(Circuit(parts=[r, vcc, gnd], ports={}), 'kicad')
    assert text.startswith('(export (version "E")')
    assert '(tool "wirebench' in text
    assert text.rstrip().endswith(')')


def test_kicad_resistor_comp_record():
    r = Resistor(330, refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    text = export_to_string(Circuit(parts=[r, vcc, gnd], ports={}), 'kicad')
    assert '(ref "R1")' in text
    assert '(value "330")' in text
    assert '(footprint "Resistor_SMD:R_0603_1608Metric")' in text
    assert '(libsource (lib "Device") (part "R")' in text


def test_kicad_led_comp_record_uses_color_as_value():
    d = LED('red', refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], d.ports['anode'])
    wire(d.ports['cathode'], gnd.ports['out'])
    text = export_to_string(Circuit(parts=[d, vcc, gnd], ports={}), 'kicad')
    assert '(ref "D1")' in text
    assert '(value "red")' in text
    assert '(libsource (lib "Device") (part "LED")' in text


def test_kicad_chip_comp_uses_dip_footprint():
    u = SN74HC04(refdes_number=1)
    text = export_to_string(Circuit(parts=[u], ports={}), 'kicad')
    assert '(ref "U1")' in text
    assert '(value "SN74HC04")' in text
    assert '(footprint "Package_DIP:DIP-14_W7.62mm")' in text


def test_kicad_connector_comp_is_present():
    j = Header2xNFemale(pin_count=4, pitch_mm=2.54, refdes_number=1)
    text = export_to_string(Circuit(parts=[j], ports={}), 'kicad')
    assert '(ref "J1")' in text
    assert 'Header2xNFemale_4' in text
    assert 'PinHeader_2x02_P2.54mm_Vertical' in text


def test_kicad_rails_emit_no_comp():
    r = Resistor(100, refdes_number=1)
    vcc = Rail(True); gnd = Rail(False)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    text = export_to_string(Circuit(parts=[r, vcc, gnd], ports={}), 'kicad')
    # No (comp ...) record with value "Rail" or refdes Rail.
    assert 'value "Rail"' not in text


def test_kicad_assembly_qualifies_refdes_across_boards():
    """Per §5.1: U1 in two boards becomes A1_U1 and A2_U1."""
    asm = _silently(WaterAlarmAssembly)
    text = export_to_string(asm, 'kicad')
    assert '(ref "A1_U1")' in text   # sensor-board ULN
    assert '(ref "A2_U1")' in text   # controller-board SN74HC04
    assert '(ref "A2_U2")' in text
    assert '(ref "A2_D1")' in text


def test_kicad_sheetpath_per_component():
    asm = _silently(WaterAlarmAssembly)
    text = export_to_string(asm, 'kicad')
    # Every comp has a sheetpath; A1_* uses /A1/, A2_* uses /A2/.
    assert '(sheetpath (names "/A1/")' in text
    assert '(sheetpath (names "/A2/")' in text


def test_kicad_tstamps_are_deterministic_sha1():
    """tstamps should be 8 hex chars, deterministic across runs."""
    text1 = export_to_string(_silently(WaterAlarmAssembly), 'kicad')
    text2 = export_to_string(_silently(WaterAlarmAssembly), 'kicad')
    assert text1 == text2
    tstamps = re.findall(r'tstamps "/([0-9a-f]+)/"', text1)
    assert tstamps, "No tstamps in output"
    assert all(len(t) == 8 for t in tstamps), f"Bad tstamp lengths: {tstamps}"


def test_kicad_net_names_vcc_and_gnd():
    asm = _silently(WaterAlarmAssembly)
    text = export_to_string(asm, 'kicad')
    assert '(name "GND")' in text
    assert '(name "vcc")' in text


def test_kicad_nets_carry_per_node_pin_numbers():
    """Every (node ...) entry has (pin "<number>") with an integer."""
    text = export_to_string(_silently(WaterAlarm), 'kicad')
    pins = re.findall(r'\(pin "(\d+)"\)', text)
    assert pins, "No pin numbers found in nets section"
    # All must parse as positive ints.
    assert all(int(p) > 0 for p in pins)


def test_kicad_chip_pin_directions_in_pintype():
    """Chip pins use input/output/bidirectional."""
    text = export_to_string(_silently(WaterAlarm), 'kicad')
    # SN74HC04 has inputs (a_*) and outputs (y_*).
    assert '(pintype "input")' in text
    assert '(pintype "output")' in text
