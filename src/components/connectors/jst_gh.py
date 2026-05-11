"""JST GH series — 1.25 mm pitch wire-to-board housings.

Common on drone flight controllers and compact-format peripherals.
"""
from __future__ import annotations

from typing import ClassVar

from framework.connector import Connector, declare_mating_pair
from framework.pin import PinId
from framework.port import Direction
from framework.signals import Analog
from framework.registry import register


@register('JSTGHBoardSide')
class JSTGHBoardSide(Connector):
    """JST GH board-side male header (1.25 mm pitch)."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PITCH_MM:     ClassVar[float] = 1.25

    def _build_pinout(self) -> tuple[tuple[PinId, Direction, type], ...]:
        return tuple((PinId(i, f'p{i}'), Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))
    @property
    def FOOTPRINT(self) -> str:
        n = self._pin_count
        return f"Connector_JST:JST_GH_BM{n}B-GHS-TBT_1x{n:02d}-1MP_P1.25mm_Vertical"



@register('JSTGHCableHousing')
class JSTGHCableHousing(Connector):
    """JST GH cable-side female crimp housing (1.25 mm pitch)."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PITCH_MM:     ClassVar[float] = 1.25

    def _build_pinout(self) -> tuple[tuple[PinId, Direction, type], ...]:
        return tuple((PinId(i, f'p{i}'), Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))
    @property
    def FOOTPRINT(self) -> str:
        n = self._pin_count
        return f"Connector_JST:JST_GH_BM{n}B-GHS-TBT_1x{n:02d}-1MP_P1.25mm_Vertical"



declare_mating_pair(JSTGHBoardSide, JSTGHCableHousing)
