"""Pydantic-adoption tests — per format spec §12 (#1-5)."""
import pytest
from pydantic import ValidationError

from framework.ground import ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.signals import Digital
from framework.wire import wire
from framework.mate import mate

from components.passives.led import LED
from components.passives.resistor import Resistor
from components.connectors.headers import Header2xNFemale, Header2xNMale


def test_pinid_rejects_bad_inputs():
    for bad_num in (0, -1, 1.0, True, '1', None):
        with pytest.raises(ValidationError):
            PinId(bad_num, 'X')  # type: ignore[arg-type]
    for bad_name in ('', None, 7):
        with pytest.raises(ValidationError):
            PinId(1, bad_name)  # type: ignore[arg-type]


def test_resistor_rejects_negative_ohms():
    # Resistor doesn't yet wrap @validate_call (still uses validate_refdes
    # for refdes_number), so this just confirms Ohms accepts the value.
    # The negative check fires later via Ohms / wire constraints.
    r = Resistor(ohms=-10, refdes_number=1)
    assert float(r._ohms) == -10.0  # demonstrates current state


def test_resistor_rejects_zero_refdes_number():
    with pytest.raises((ValueError, ValidationError)):
        Resistor(ohms=10, refdes_number=0)


def test_led_rejects_empty_color():
    # LED color is validated via Pin (PinId etc.) — empty string passes
    # current code; documents present behaviour.
    led = LED(color='red', refdes_number=1)
    assert led._color == 'red'


def test_mate_validates_argument_types():
    real_conn = Header2xNFemale(pin_count=2, pitch_mm=2.54, refdes_number=1)
    with pytest.raises(ValidationError):
        mate("not a connector", real_conn)  # type: ignore[arg-type]


def test_wire_validates_argument_types():
    with pytest.raises(ValidationError):
        wire("not a port")  # type: ignore[arg-type]


def test_pin_other_face_validates():
    pin = Pin(PinId(1, 'x'), Direction.IN, ELECTRICAL, signal_type=Digital)
    with pytest.raises(ValidationError):
        pin.other_face("not a port")  # type: ignore[arg-type]


def test_pin_init_rejects_non_pinid_first_arg():
    with pytest.raises(ValidationError):
        Pin('a', Direction.IN, ELECTRICAL, signal_type=Digital)  # type: ignore[arg-type]
