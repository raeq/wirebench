"""DC barrel jacks and plugs.

The two common families differ in pin diameter; their mating partners
are kept distinct so a 2.1 mm plug cannot mate with a 2.5 mm jack.
"""
from __future__ import annotations

from typing import ClassVar

from framework.connector import Connector, declare_mating_pair
from framework.pin import PinId
from framework.port import Direction
from framework.signals import Analog


_BARREL_PINOUT = (
    (PinId(1, 'tip'),    Direction.BIDIR, Analog),
    (PinId(2, 'sleeve'), Direction.BIDIR, Analog),
)


# 5.5 mm OD × 2.1 mm ID centre-positive DC

class BarrelJack5p5x2p1(Connector):
    """5.5 mm × 2.1 mm DC barrel jack (board-side)."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PIN_COUNT     = 2
    PITCH_MM:     ClassVar[float] = 2.1
    PINOUT        = _BARREL_PINOUT


class BarrelPlug5p5x2p1(Connector):
    """5.5 mm × 2.1 mm DC barrel plug."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PIN_COUNT     = 2
    PITCH_MM:     ClassVar[float] = 2.1
    PINOUT        = _BARREL_PINOUT


declare_mating_pair(BarrelJack5p5x2p1, BarrelPlug5p5x2p1)


# 5.5 mm OD × 2.5 mm ID — mechanically incompatible with the 2.1 mm pair

class BarrelJack5p5x2p5(Connector):
    """5.5 mm × 2.5 mm DC barrel jack (board-side)."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PIN_COUNT     = 2
    PITCH_MM:     ClassVar[float] = 2.5
    PINOUT        = _BARREL_PINOUT


class BarrelPlug5p5x2p5(Connector):
    """5.5 mm × 2.5 mm DC barrel plug."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PIN_COUNT     = 2
    PITCH_MM:     ClassVar[float] = 2.5
    PINOUT        = _BARREL_PINOUT


declare_mating_pair(BarrelJack5p5x2p5, BarrelPlug5p5x2p5)
