"""Tests for the DriveType axis on chip pins.

Covers:
  * Construction-time invariant in `Chip.__init__`: `PIN_DRIVE_TYPES`
    entries must name a real pin AND require OUT or BIDIR direction
    for any non-PUSH_PULL drive.
  * Default behaviour: pins not in `PIN_DRIVE_TYPES` are PUSH_PULL.
  * `Chip.pin_drive_type` classmethod returns the declared drive type
    (or PUSH_PULL by default).

The ERC predicate (OD pin needs a pull-up to a POWER rail) is tested
separately in tests/framework/export/assembly_guide/test_pin_function_
erc.py — it lives with the other ERC predicates.
"""
from __future__ import annotations

from typing import ClassVar

import pytest

from framework.chip import Chip
from framework.drive_type import DriveType
from framework.errors import PartConfigurationError
from framework.ground import ELECTRICAL, GroundDomain
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog, Digital


def _make_chip_cls(*, pin_table, drive_types):
    """Build a one-off Chip subclass with the given pin table and
    drive-type overrides.  Used by every test in this file."""
    class _Stub(Chip):
        REFDES_PREFIX: ClassVar[str] = 'U'
        BARE_FIRMWARE_DRIVEN: ClassVar[bool] = True   # skip OUT-driver check
        PIN_DRIVE_TYPES: ClassVar[dict[str, DriveType]] = drive_types
        __slots__ = ('_refdes_number',)

        def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                     refdes_number: RefdesNumber) -> None:
            validate_refdes(self.REFDES_PREFIX, refdes_number)
            self._refdes_number = refdes_number
            pins = [
                Pin(PinId(number, name), direction, domain,
                    mandatory=False, signal_type=signal_type)
                for number, name, direction, signal_type in pin_table
            ]
            super().__init__(pins=pins, cells=[])

        @property
        def refdes(self) -> str:
            return f"{self.REFDES_PREFIX}{self._refdes_number}"

        def __call__(self) -> None: pass

    return _Stub


# Reusable pin tables.  Each is a minimal but-valid set of pins:
# always VCC + GND + the function pin under test.
_BASE = (
    (1, 'VCC', Direction.IN, Analog),
    (2, 'GND', Direction.IN, Analog),
)


# ----------------------------------------------------- default + lookup

def test_default_pin_drive_type_is_push_pull():
    Stub = _make_chip_cls(
        pin_table=(*_BASE, (3, 'OUT', Direction.OUT, Digital)),
        drive_types={},
    )
    assert Stub.pin_drive_type('OUT') is DriveType.PUSH_PULL
    assert Stub.pin_drive_type('VCC') is DriveType.PUSH_PULL
    # Unknown name — still PUSH_PULL (no exception).
    assert Stub.pin_drive_type('NONE_SUCH') is DriveType.PUSH_PULL


def test_pin_drive_type_returns_declared_value():
    Stub = _make_chip_cls(
        pin_table=(*_BASE, (3, 'OUT', Direction.OUT, Digital)),
        drive_types={'OUT': DriveType.OPEN_COLLECTOR},
    )
    assert Stub.pin_drive_type('OUT') is DriveType.OPEN_COLLECTOR


# ------------------------------------------ validator: pin must exist

def test_pin_drive_types_referencing_unknown_pin_raises():
    # The class declares a drive type for 'NOPE' which doesn't exist
    # in the pin table — caught at construction.
    Stub = _make_chip_cls(
        pin_table=(*_BASE, (3, 'OUT', Direction.OUT, Digital)),
        drive_types={'NOPE': DriveType.OPEN_DRAIN},
    )
    with pytest.raises(PartConfigurationError, match=r"no pin has that name"):
        Stub(refdes_number=1)


# ------------------------------- validator: non-PUSH_PULL needs OUT/BIDIR

@pytest.mark.parametrize('drive_type', [
    DriveType.OPEN_DRAIN,
    DriveType.OPEN_COLLECTOR,
    DriveType.TRI_STATE,
])
def test_non_push_pull_on_in_pin_raises(drive_type):
    Stub = _make_chip_cls(
        pin_table=(*_BASE, (3, 'IN', Direction.IN, Digital)),
        drive_types={'IN': drive_type},
    )
    with pytest.raises(PartConfigurationError, match=r"non-PUSH_PULL"):
        Stub(refdes_number=1)


@pytest.mark.parametrize('drive_type', [
    DriveType.OPEN_DRAIN,
    DriveType.OPEN_COLLECTOR,
    DriveType.TRI_STATE,
])
def test_non_push_pull_on_out_pin_constructs(drive_type):
    Stub = _make_chip_cls(
        pin_table=(*_BASE, (3, 'OUT', Direction.OUT, Digital)),
        drive_types={'OUT': drive_type},
    )
    chip = Stub(refdes_number=1)
    assert type(chip).pin_drive_type('OUT') is drive_type


@pytest.mark.parametrize('drive_type', [
    DriveType.OPEN_DRAIN,
    DriveType.OPEN_COLLECTOR,
    DriveType.TRI_STATE,
])
def test_non_push_pull_on_bidir_pin_constructs(drive_type):
    # The I²C SDA case: BIDIR + OPEN_DRAIN must be allowed.  I²C
    # protocol mandates wired-AND open-drain for multi-master
    # arbitration; refusing this combination would block every I²C
    # peripheral in the catalogue.
    Stub = _make_chip_cls(
        pin_table=(*_BASE, (3, 'SDA', Direction.BIDIR, Digital)),
        drive_types={'SDA': drive_type},
    )
    chip = Stub(refdes_number=1)
    assert type(chip).pin_drive_type('SDA') is drive_type


def test_push_pull_on_in_pin_is_no_op():
    # Explicitly declaring an IN pin as PUSH_PULL is silly but legal
    # — PUSH_PULL is the default; the validator only fires on
    # non-PUSH_PULL declarations.
    Stub = _make_chip_cls(
        pin_table=(*_BASE, (3, 'IN', Direction.IN, Digital)),
        drive_types={'IN': DriveType.PUSH_PULL},
    )
    chip = Stub(refdes_number=1)
    assert type(chip).pin_drive_type('IN') is DriveType.PUSH_PULL


# ------------------------------------------------ enum value stability

def test_drive_type_values_are_lowercase_role_names():
    # Stable string values for failure-message text and any future
    # serialization.
    assert DriveType.PUSH_PULL.value      == 'push_pull'
    assert DriveType.OPEN_DRAIN.value     == 'open_drain'
    assert DriveType.OPEN_COLLECTOR.value == 'open_collector'
    assert DriveType.TRI_STATE.value      == 'tri_state'
