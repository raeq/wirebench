"""JST PH series — 2.0 mm pitch wire-to-board housings.

Common on LiPo batteries, sensor breakouts, and small-format hobby
electronics.  `B*B-PH-K-S` is the board header; `PHR-*` is the cable
crimp housing.
"""
from __future__ import annotations

from typing import ClassVar

from framework.connector import Connector, declare_mating_pair
from framework.pin import PinId
from framework.port import Direction
from framework.signals import Analog


class JSTPHBoardSide(Connector):
    """JST PH board-side male header (2.0 mm pitch)."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PITCH_MM:     ClassVar[float] = 2.0

    def _build_pinout(self) -> tuple[tuple[PinId, Direction, type], ...]:
        return tuple((PinId(i, f'p{i}'), Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))


class JSTPHCableHousing(Connector):
    """JST PH cable-side female crimp housing (2.0 mm pitch)."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PITCH_MM:     ClassVar[float] = 2.0

    def _build_pinout(self) -> tuple[tuple[PinId, Direction, type], ...]:
        return tuple((PinId(i, f'p{i}'), Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))


declare_mating_pair(JSTPHBoardSide, JSTPHCableHousing)
