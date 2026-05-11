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
from components.chips.sn74hc04 import SN74HC04
from components.connectors.headers import Header2xNFemale, Header2xNMale
from framework.board import Board


def test_pinid_rejects_bad_inputs():
    for bad_num in (0, -1, 1.0, True, '1', None):
        with pytest.raises(ValidationError):
            PinId(bad_num, 'X')  # type: ignore[arg-type]
    for bad_name in ('', None, 7):
        with pytest.raises(ValidationError):
            PinId(1, bad_name)  # type: ignore[arg-type]


def test_resistor_rejects_negative_ohms():
    with pytest.raises(ValidationError):
        Resistor(ohms=-10, refdes_number=1)
    with pytest.raises(ValidationError):
        Resistor(ohms=0, refdes_number=1)


def test_resistor_rejects_zero_refdes_number():
    with pytest.raises((ValueError, ValidationError)):
        Resistor(ohms=10, refdes_number=0)


def test_led_rejects_empty_color():
    with pytest.raises(ValidationError):
        LED(color='', refdes_number=1)


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


def test_chip_rejects_invalid_refdes():
    for bad in (0, -1, 1.0, True, '1', None):
        with pytest.raises(ValidationError):
            SN74HC04(refdes_number=bad)  # type: ignore[arg-type]


def test_connector_rejects_invalid_pin_count():
    for bad in (0, -2, 1.5, '2'):
        with pytest.raises(ValidationError):
            Header2xNFemale(pin_count=bad, pitch_mm=2.54, refdes_number=1)  # type: ignore[arg-type]


def test_connector_rejects_invalid_pitch_mm():
    for bad in (0, -2.54, '2.54'):
        with pytest.raises(ValidationError):
            Header2xNFemale(pin_count=2, pitch_mm=bad, refdes_number=1)  # type: ignore[arg-type]


def test_board_rejects_empty_name_and_revision():
    with pytest.raises(ValidationError):
        Board(name='', revision='A', components=[], refdes_number=1)
    with pytest.raises(ValidationError):
        Board(name='B', revision='', components=[], refdes_number=1)


def test_call_path_validates_inputs():
    # __call__ now validates types: a non-bool to LED.__call__ raises.
    led = LED(color='red', refdes_number=1)
    with pytest.raises(ValidationError):
        led('not-a-bool')  # type: ignore[arg-type]
    # Resistor.__call__ rejects a non-numeric current.
    r = Resistor(330, refdes_number=1)
    with pytest.raises(ValidationError):
        r('not-a-number')  # type: ignore[arg-type]
