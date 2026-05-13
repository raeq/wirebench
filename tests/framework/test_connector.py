"""Connector + Pin BIDIR + IS_CONDUCTOR tests — per spec §13."""
from __future__ import annotations

import pytest

from framework.board import Board
from framework.circuit import Circuit
from framework.connector import Connector
from framework.errors import (
    FloatingNetError, PartConfigurationError, PortContentionError,
    ShortCircuitError, UnknownPortError, UnmateableError,
)
from framework.part import Part
from framework.ground import ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction, Port
from framework.signals import Digital
from framework.wire import wire

from components.connectors.headers import (
    Header1xNFemale, Header1xNMale, Header2xNFemale, Header2xNMale,
)
from components.connectors.usb import USBCPlug, USBCReceptacle
from components.connectors.jst_ph import JSTPHBoardSide, JSTPHCableHousing
from components.connectors.screw_terminal import ScrewTerminalBlock

from components.passives.led import LED
from components.passives.rail import Rail
from components.passives.resistor import Resistor


# -- 8. Connector abstract by convention --

def test_connector_under_specified_part_raises():
    # Header1xNMale needs pin_count + pitch_mm at construction.
    with pytest.raises(PartConfigurationError):
        Header1xNMale(refdes_number=1)


# -- 9. Fixed-geometry connector exposes its pins --

def test_usbc_receptacle_24_pins():
    c = USBCReceptacle(refdes_number=1)
    assert len(c.pins) == 24
    names = {p.name for p in c.pins}
    assert 'A1_GND' in names
    assert 'B12_GND' in names


# -- 10. Parameterised connector synthesises pinout --

def test_parameterised_header_pin_count():
    h10 = Header2xNFemale(pin_count=10, pitch_mm=2.54, refdes_number=1)
    h40 = Header2xNFemale(pin_count=40, pitch_mm=2.54, refdes_number=2)
    assert [p.name for p in h10.pins] == [f'p{i}' for i in range(1, 11)]
    assert [p.name for p in h40.pins] == [f'p{i}' for i in range(1, 41)]


# -- 11. external_ports vs ports --

def test_external_ports_vs_all_ports():
    c = USBCReceptacle(refdes_number=1)
    assert len(c.external_ports) == 24
    assert len(c.ports) == 48     # 2 faces per pin


# -- 12. Refdes prefix conventions --

@pytest.mark.parametrize("cls,prefix", [
    (Header2xNFemale,  'J'),
    (Header2xNMale,    'P'),
    (JSTPHBoardSide,   'P'),
    (JSTPHCableHousing, 'J'),
])
def test_refdes_prefix_by_gender(cls, prefix):
    assert cls.REFDES_PREFIX == prefix


# -- 13. Under-specified part rejects (also covered by 8) --

def test_no_pin_count_rejects():
    with pytest.raises(PartConfigurationError, match="pin_count"):
        Header1xNMale(pitch_mm=2.54, refdes_number=1)


def test_no_pitch_rejects():
    with pytest.raises(PartConfigurationError, match="pitch_mm"):
        Header1xNMale(pin_count=4, refdes_number=1)


# -- 14. BIDIR Pin support --

def test_bidir_pin_constructs():
    p = Pin(PinId(1, 'x'), Direction.BIDIR, ELECTRICAL, signal_type=Digital)
    assert p.external.direction is Direction.BIDIR
    assert p.internal.direction is Direction.BIDIR


def test_bidir_pin_evaluate_relays_external_to_internal():
    p = Pin(PinId(1, 'x'), Direction.BIDIR, ELECTRICAL, signal_type=Digital)
    p.external.drive(True)
    p.evaluate()
    assert p.internal.value is True


def test_bidir_pin_evaluate_relays_internal_to_external():
    p = Pin(PinId(1, 'x'), Direction.BIDIR, ELECTRICAL, signal_type=Digital)
    p.internal.drive(False)
    p.evaluate()
    assert p.external.value is False


def test_bidir_pin_contention_raises():
    p = Pin(PinId(1, 'x'), Direction.BIDIR, ELECTRICAL, signal_type=Digital)
    p.external.drive(True)
    p.internal.drive(False)
    with pytest.raises(PortContentionError, match="contention"):
        p.evaluate()


# -- 14b. IS_CONDUCTOR --

def test_pin_is_conductor():
    assert Pin.IS_CONDUCTOR is True


@pytest.mark.parametrize("cls", [Resistor, LED, Rail])
def test_passives_not_conductor(cls):
    assert cls.IS_CONDUCTOR is False


# -- 14c. other_face --

def test_pin_other_face():
    p = Pin(PinId(1, 'x'), Direction.IN, ELECTRICAL, signal_type=Digital)
    assert p.other_face(p.external) is p.internal
    assert p.other_face(p.internal) is p.external


def test_pin_other_face_rejects_stranger():
    p = Pin(PinId(1, 'x'), Direction.IN, ELECTRICAL, signal_type=Digital)
    stranger = Port('s', Direction.IN, ELECTRICAL, signal_type=Digital)
    with pytest.raises(UnknownPortError):
        p.other_face(stranger)


# -- 14e. Logical-net walker rejects cross-board multi-OUT --

def test_validate_rejects_cross_board_multi_out_via_mate():
    """Two boards, both driving the same mated pin → logical net has
    two real OUT drivers → short circuit."""
    from framework.mate import mate

    # Two boards, each with a Rail wired to a header pin.
    def _board_with_rail(refdes_number: int, gender: str) -> Board:
        rail = Rail(True)
        cls = Header1xNMale if gender == 'male' else Header1xNFemale
        c = cls(pin_count=2, pitch_mm=2.54, refdes_number=1)
        wire(rail.ports['out'], c.pins[0].internal)
        return Board(name=f'B{refdes_number}', revision='A',
                     components=[rail, c], refdes_number=refdes_number)

    b1 = _board_with_rail(1, 'male')
    b2 = _board_with_rail(2, 'female')
    mate(b1.connectors[0], b2.connectors[0])

    with pytest.raises(ShortCircuitError, match="Short circuit on logical net"):
        Circuit(parts=[b1, b2], ports={})


# -- 14f. Resistor-resistor floating net still rejected --

def test_validate_still_rejects_two_resistors_no_driver():
    from framework.node import Node
    r1 = Resistor(ohms=100, refdes_number=1)
    r2 = Resistor(ohms=100, refdes_number=2)
    shared = Node('shared', ELECTRICAL)
    r1.ports['t1'].connect(shared)
    r2.ports['t1'].connect(shared)
    with pytest.raises(FloatingNetError, match="Floating logical net"):
        Circuit(parts=[r1, r2],
                ports={'a': r1.ports['t2'], 'b': r2.ports['t2']})


# -- 15. MATES_WITH = None refuses to mate --

def test_screw_terminal_has_no_mate():
    assert ScrewTerminalBlock.MATES_WITH is None


def test_mate_refuses_when_mates_with_is_none():
    from framework.mate import mate
    s = ScrewTerminalBlock(pin_count=3, pitch_mm=5.08, refdes_number=1)
    other = Header1xNMale(pin_count=3, pitch_mm=5.08, refdes_number=1)
    with pytest.raises(UnmateableError, match="no in-model mate"):
        mate(s, other)


# -- 16. Smoke test the whole library --

def test_every_connector_class_instantiates():
    """Iterate every public class re-exported from
    components.connectors.__init__; instantiate each and verify it has
    pins and external_ports.  Catches forgotten ClassVars or missing
    _build_pinout overrides."""
    from components import connectors as conn_pkg

    # Connectors with no PITCH_MM class attribute (snap-apart headers,
    # IDC, ScrewTerminalBlock) need pitch_mm at construction.  JST
    # families set PITCH_MM as a class attribute.
    needs_pitch = {
        'Header1xNFemale', 'Header1xNMale',
        'Header2xNFemale', 'Header2xNMale',
        'IDC2xNMale', 'IDC2xNSocket',
        'ScrewTerminalBlock',
    }
    needs_pin_count = needs_pitch | {
        'JSTPHBoardSide', 'JSTPHCableHousing',
        'JSTXHBoardSide', 'JSTXHCableHousing',
        'JSTSHBoardSide', 'JSTSHCableHousing',
        'JSTGHBoardSide', 'JSTGHCableHousing',
    }
    for name in conn_pkg.__all__:
        cls = getattr(conn_pkg, name)
        kwargs: dict = {'refdes_number': 1}
        if name in needs_pin_count:
            kwargs['pin_count'] = 4
        if name in needs_pitch:
            kwargs['pitch_mm'] = 2.54
        inst = cls(**kwargs)
        assert len(inst.pins) > 0, f"{name} produced no pins"
        assert len(inst.external_ports) > 0, f"{name} produced no external_ports"
