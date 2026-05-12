"""Generic snap-apart pin headers — 1×N and 2×N, any pitch.

Workhorse parts for breadboards, jumpers, mezzanine connections, and
Arduino-style dev boards.  Pin count and pitch are constructor
parameters because the strips are field-cut.
"""
from __future__ import annotations

from typing import ClassVar

from framework.connector import Connector, declare_mating_pair
from framework.pin import PinId
from framework.port import Direction
from framework.signals import Analog
from framework.registry import register


def _header_1x_footprint(pin_count: int, pitch_mm: float) -> str:
    return (
        f"Connector_PinHeader_{pitch_mm}mm:"
        f"PinHeader_1x{pin_count:02d}_P{pitch_mm}mm_Vertical"
    )


def _header_2x_footprint(pin_count: int, pitch_mm: float) -> str:
    return (
        f"Connector_PinHeader_{pitch_mm}mm:"
        f"PinHeader_2x{pin_count // 2:02d}_P{pitch_mm}mm_Vertical"
    )


@register('Header1xNMale')
class Header1xNMale(Connector):
    """1×N pin header strip, snap-apart.  Common pitches: 2.54 mm (0.1"),
    1.27 mm (0.05" — JTAG/SWD)."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'

    # Parametric connectors need to round-trip pin count, pitch, and
    # ground domain so isolated-side instances reconstruct in their
    # own domain rather than collapsing to ELECTRICAL on load.
    SERIALIZE_KWARGS: ClassVar[tuple[str, ...]] = ('domain', 'pin_count', 'pitch_mm')

    def _build_pinout(self) -> tuple[tuple[PinId, Direction, type], ...]:
        return tuple((PinId(i, f'p{i}'), Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))

    @property
    def FOOTPRINT(self) -> str:
        return _header_1x_footprint(self._pin_count, self._pitch_mm)


@register('Header1xNFemale')
class Header1xNFemale(Connector):
    """1×N socket header strip — female counterpart to Header1xNMale."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'

    SERIALIZE_KWARGS: ClassVar[tuple[str, ...]] = ('domain', 'pin_count', 'pitch_mm')

    def _build_pinout(self) -> tuple[tuple[PinId, Direction, type], ...]:
        return tuple((PinId(i, f'p{i}'), Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))

    @property
    def FOOTPRINT(self) -> str:
        return _header_1x_footprint(self._pin_count, self._pitch_mm)


@register('Header2xNMale')
class Header2xNMale(Connector):
    """2×N dual-row pin header strip.  `pin_count` here is the *total* pin
    count (= 2 × pins_per_row), matching how these are sold and labelled."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'

    def _build_pinout(self) -> tuple[tuple[PinId, Direction, type], ...]:
        return tuple((PinId(i, f'p{i}'), Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))

    @property
    def FOOTPRINT(self) -> str:
        return _header_2x_footprint(self._pin_count, self._pitch_mm)


@register('Header2xNFemale')
class Header2xNFemale(Connector):
    """2×N dual-row socket header — female counterpart to Header2xNMale."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'

    def _build_pinout(self) -> tuple[tuple[PinId, Direction, type], ...]:
        return tuple((PinId(i, f'p{i}'), Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))

    @property
    def FOOTPRINT(self) -> str:
        return _header_2x_footprint(self._pin_count, self._pitch_mm)


declare_mating_pair(Header1xNMale, Header1xNFemale)
declare_mating_pair(Header2xNMale, Header2xNFemale)
