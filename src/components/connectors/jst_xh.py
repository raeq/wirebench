"""JST XH series — 2.5 mm pitch wire-to-board housings.

Common in LiPo balance leads (2-pin to 7-pin) and slightly larger
hobby/industrial gear than the PH series.
"""
from __future__ import annotations

from typing import ClassVar

from framework.connector import Connector, declare_mating_pair
from framework.pin import PinId
from framework.port import Direction
from framework.signals import Analog
from framework.registry import register


@register('JSTXHBoardSide')
class JSTXHBoardSide(Connector):
    """JST XH board-side male header (2.5 mm pitch)."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PITCH_MM:     ClassVar[float] = 2.5

    def _build_pinout(self) -> tuple[tuple[PinId, Direction, type], ...]:
        return tuple((PinId(i, f'p{i}'), Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))


@register('JSTXHCableHousing')
class JSTXHCableHousing(Connector):
    """JST XH cable-side female crimp housing (2.5 mm pitch)."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PITCH_MM:     ClassVar[float] = 2.5

    def _build_pinout(self) -> tuple[tuple[PinId, Direction, type], ...]:
        return tuple((PinId(i, f'p{i}'), Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))


declare_mating_pair(JSTXHBoardSide, JSTXHCableHousing)
