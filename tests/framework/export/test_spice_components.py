"""Per-component SPICE renderer tests."""
import re
import warnings

import pytest

# Trigger registrations.
import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.export.spice  # noqa: F401

from framework.export import export_to_string
from framework.export.base import ExporterContext
from framework.export.spice.renderers import (
    render_led, render_rail, render_resistor,
)

from components.chips.sn74hc04 import SN74HC04
from components.passives.led import LED
from components.passives.rail import Rail
from components.passives.resistor import Resistor
from components.connectors.headers import Header2xNFemale
from framework.board import Board
from framework.circuit import Circuit
from framework.wire import wire


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


# ---------------------------------------------------------------------------
# Resistor / LED / Rail
# ---------------------------------------------------------------------------

def test_resistor_renders_to_R_line():
    r = Resistor(330, refdes_number=1)
    vcc = Rail(True)
    gnd = Rail(False)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    design = Circuit(parts=[r, vcc, gnd], ports={})

    text = export_to_string(design, 'spice')
    assert re.search(r'^R1\s+vcc\s+0\s+330(\.0)?$', text, flags=re.M)


def test_led_renders_with_D_LED_model():
    d = LED('red', refdes_number=1)
    vcc = Rail(True)
    gnd = Rail(False)
    wire(vcc.ports['out'], d.ports['anode'])
    wire(d.ports['cathode'], gnd.ports['out'])
    design = Circuit(parts=[d, vcc, gnd], ports={})

    text = export_to_string(design, 'spice')
    assert re.search(r'^D1\s+vcc\s+0\s+D_LED$', text, flags=re.M)
    assert '.LIB' in text  # library reference present


def test_rail_true_emits_voltage_source():
    vcc = Rail(True)
    gnd = Rail(False)
    r = Resistor(1000, refdes_number=1)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    design = Circuit(parts=[vcc, gnd, r], ports={})

    text = export_to_string(design, 'spice')
    assert re.search(r'^V_\S+\s+vcc\s+0\s+DC\s+5(\.0)?$', text, flags=re.M)


def test_rail_false_emits_no_source():
    gnd = Rail(False)
    r = Resistor(1000, refdes_number=1)
    vcc = Rail(True)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    design = Circuit(parts=[gnd, r, vcc], ports={})

    text = export_to_string(design, 'spice')
    # Exactly one V_* source (for vcc).
    assert len(re.findall(r'^V_\S+\b', text, flags=re.M)) == 1


# ---------------------------------------------------------------------------
# Chips
# ---------------------------------------------------------------------------

def test_chip_renders_as_X_instance_with_ordered_pins():
    u = SN74HC04(refdes_number=1)
    design = Circuit(parts=[u], ports={})

    text = export_to_string(design, 'spice')
    # X-instance line: refdes, then 12 pin nets (datasheet pins
    # excluding GND/VCC), then model name.
    m = re.search(r'^U1\s+((?:\S+\s+){12})SN74HC04$', text, flags=re.M)
    assert m, f"SN74HC04 X-instance not found in:\n{text}"


# ---------------------------------------------------------------------------
# Connectors
# ---------------------------------------------------------------------------

def test_connector_emits_nothing():
    """Connectors are transparent in netlist export — IS_CONDUCTOR
    collapses them into the net, no SPICE line per pin."""
    conn = Header2xNFemale(pin_count=2, pitch_mm=2.54, refdes_number=1)
    vcc = Rail(True)
    gnd = Rail(False)
    wire(vcc.ports['out'], conn.pins[0].internal)
    wire(gnd.ports['out'], conn.pins[1].internal)
    design = Circuit(parts=[conn, vcc, gnd], ports={})

    text = export_to_string(design, 'spice')
    # No 'J1' or per-pin line referencing the connector refdes.
    assert not re.search(r'^J1\b', text, flags=re.M)


# ---------------------------------------------------------------------------
# Boards
# ---------------------------------------------------------------------------

def test_board_emits_SUBCKT_and_X_instance():
    r = Resistor(330, refdes_number=1)
    vcc = Rail(True)
    gnd = Rail(False)
    conn = Header2xNFemale(pin_count=2, pitch_mm=2.54, refdes_number=1)
    wire(vcc.ports['out'], r.ports['t1'])
    wire(r.ports['t2'], gnd.ports['out'])
    board = Board(
        name='Tiny',
        revision='A',
        components=[r, vcc, gnd, conn],
        refdes_number=1,
    )
    assembly = Circuit(parts=[board], ports={})

    text = export_to_string(assembly, 'spice')
    assert re.search(r'^\.SUBCKT\s+A1_SUBCKT\b', text, flags=re.M)
    assert re.search(r'^\.ENDS\s+A1_SUBCKT\b', text, flags=re.M)
    assert re.search(r'^XA1\s+.+\s+A1_SUBCKT$', text, flags=re.M)
