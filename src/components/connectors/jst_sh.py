"""JST SH series — 1.0 mm pitch wire-to-board housings.

Common in drone GPS modules and other compact-format electronics.
"""
from __future__ import annotations

from typing import ClassVar

from framework.connector import Connector, declare_mating_pair
from framework.pin import PinId
from framework.port import Direction
from framework.signals import Analog
from framework.registry import register


@register('JSTSHBoardSide')
class JSTSHBoardSide(Connector):
    """JST SH board-side male header (1.0 mm pitch)."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PITCH_MM:     ClassVar[float] = 1.0

    def _build_pinout(self) -> tuple[tuple[PinId, Direction, type], ...]:
        return tuple((PinId(i, f'p{i}'), Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))


@register('JSTSHCableHousing')
class JSTSHCableHousing(Connector):
    """JST SH cable-side female crimp housing (1.0 mm pitch)."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PITCH_MM:     ClassVar[float] = 1.0

    def _build_pinout(self) -> tuple[tuple[PinId, Direction, type], ...]:
        return tuple((PinId(i, f'p{i}'), Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))


declare_mating_pair(JSTSHBoardSide, JSTSHCableHousing)
