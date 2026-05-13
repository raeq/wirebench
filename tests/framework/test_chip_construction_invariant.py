"""Construction-time invariant tests for `Chip.__init__`.

A chip class with an OUT pin must drive that pin's internal face via
a cell, or declare `BARE_FIRMWARE_DRIVEN = True` to opt out.  These
tests pin the contract:

- A `_BrokenChip` with an OUT pin and `cells=[]` raises
  `PartConfigurationError` at construction.
- A `_FixedChip` that wires a driving cell constructs cleanly.
- A `_FirmwareDrivenChip` with `BARE_FIRMWARE_DRIVEN = True` skips
  the check and constructs cleanly.
"""
from __future__ import annotations

import pytest

from framework.chip import Chip
from framework.errors import PartConfigurationError
from framework.part import Part
from framework.ground import ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction, Port
from framework.signals import Digital
from framework.wire import wire


class _PassiveDriver(Part):
    """Tiny Part that drives one OUT port to False — just
    enough to satisfy the invariant for a "fixed" chip."""

    __slots__ = ('_ports',)

    def __init__(self) -> None:
        self._ports = {
            'out': Port('out', Direction.OUT, ELECTRICAL,
                        mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    def evaluate(self) -> None:
        self._ports['out'].drive(False)


def test_broken_chip_raises_part_configuration_error() -> None:
    """A Chip subclass declaring an OUT pin with `cells=[]` and no
    internal driver is rejected at construction."""

    class _BrokenChip(Chip):
        __slots__ = ()

        def __init__(self) -> None:
            y = Pin(PinId(1, 'y'), Direction.OUT, ELECTRICAL,
                    mandatory=False, signal_type=Digital)
            super().__init__(pins=[y], cells=[])

        def __call__(self) -> None:
            return None

    with pytest.raises(PartConfigurationError, match="'y'"):
        _BrokenChip()


def test_fixed_chip_constructs_cleanly() -> None:
    """A Chip whose OUT pin is driven by a cell satisfies the
    invariant and constructs cleanly."""

    class _FixedChip(Chip):
        __slots__ = ('_drv',)

        def __init__(self) -> None:
            y = Pin(PinId(1, 'y'), Direction.OUT, ELECTRICAL,
                    mandatory=False, signal_type=Digital)
            self._drv = _PassiveDriver()
            wire(self._drv.ports['out'], y.internal)
            super().__init__(pins=[y], cells=[self._drv])

        def __call__(self) -> None:
            return None

    chip = _FixedChip()
    assert chip is not None


def test_firmware_driven_chip_skips_invariant() -> None:
    """A Chip with `BARE_FIRMWARE_DRIVEN = True` ships with `cells=[]`
    and an OUT pin without raising — the opt-out path for MCUs."""

    class _FirmwareDrivenChip(Chip):
        __slots__ = ()
        BARE_FIRMWARE_DRIVEN = True

        def __init__(self) -> None:
            y = Pin(PinId(1, 'y'), Direction.OUT, ELECTRICAL,
                    mandatory=False, signal_type=Digital)
            super().__init__(pins=[y], cells=[])

        def __call__(self) -> None:
            return None

    chip = _FirmwareDrivenChip()
    assert chip is not None


def test_passthrough_chip_satisfies_invariant() -> None:
    """An IN pin wired directly to an OUT pin internally (no cell)
    is a valid pass-through configuration — the IN pin's internal
    face is an OUT-direction driver from the OUT pin's perspective."""

    class _PassThroughChip(Chip):
        __slots__ = ()

        def __init__(self) -> None:
            a = Pin(PinId(1, 'a'), Direction.IN, ELECTRICAL,
                    mandatory=False, signal_type=Digital)
            y = Pin(PinId(2, 'y'), Direction.OUT, ELECTRICAL,
                    mandatory=False, signal_type=Digital)
            wire(a.internal, y.internal)
            super().__init__(pins=[a, y], cells=[])

        def __call__(self) -> None:
            return None

    chip = _PassThroughChip()
    assert chip is not None


def test_error_message_names_pin_and_points_at_pattern() -> None:
    """The `PartConfigurationError` message is actionable — it
    names the offending pin and points at the established cell
    pattern."""

    class _MisconfiguredChip(Chip):
        __slots__ = ()

        def __init__(self) -> None:
            a = Pin(PinId(1, 'A'), Direction.IN, ELECTRICAL,
                    mandatory=False, signal_type=Digital)
            out_pin = Pin(PinId(2, 'BAD'), Direction.OUT, ELECTRICAL,
                          mandatory=False, signal_type=Digital)
            super().__init__(pins=[a, out_pin], cells=[])

        def __call__(self) -> None:
            return None

    with pytest.raises(PartConfigurationError) as exc_info:
        _MisconfiguredChip()
    msg = str(exc_info.value)
    assert "'BAD'" in msg
    assert "pin 2" in msg
    assert "BARE_FIRMWARE_DRIVEN" in msg
    assert "src/components/chips/concepts/" in msg
