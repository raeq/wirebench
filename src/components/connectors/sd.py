"""SD-family memory card slots, and the cards themselves modelled as
connectors (their gold contacts are pins).  This lets a multi-board
model represent "card inserted in slot" via mate()."""
from __future__ import annotations

from typing import ClassVar

from framework.connector import Connector, declare_mating_pair
from framework.pin import PinId
from framework.port import Direction
from framework.signals import Analog
from framework.registry import register


# ------------------------------------------------------------- microSD
# 8-contact pinout per the SD specification.

_MICROSD_PINOUT = (
    (PinId(1, 'dat2'), Direction.BIDIR, Analog),
    (PinId(2, 'dat3'), Direction.BIDIR, Analog),
    (PinId(3, 'cmd'),  Direction.BIDIR, Analog),
    (PinId(4, 'vdd'),  Direction.BIDIR, Analog),
    (PinId(5, 'clk'),  Direction.BIDIR, Analog),
    (PinId(6, 'vss'),  Direction.BIDIR, Analog),
    (PinId(7, 'dat0'), Direction.BIDIR, Analog),
    (PinId(8, 'dat1'), Direction.BIDIR, Analog),
)


@register('MicroSDCardSlot')
class MicroSDCardSlot(Connector):
    """microSD card slot (board-side).  8 contacts."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PIN_COUNT     = 8
    PITCH_MM:     ClassVar[float] = 1.1
    PINOUT        = _MICROSD_PINOUT
    FOOTPRINT:    ClassVar[str | None] = "Connector_Card:microSD_HC_Hirose_DM3D-SF"



@register('MicroSDCard')
class MicroSDCard(Connector):
    """A microSD card — modelled as a connector because the gold
    contacts are its physical interface to the slot.  The card's
    internal storage controller is not modelled."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PIN_COUNT     = 8
    PITCH_MM:     ClassVar[float] = 1.1
    PINOUT        = _MICROSD_PINOUT
    FOOTPRINT:    ClassVar[str | None] = None



declare_mating_pair(MicroSDCardSlot, MicroSDCard)


# --------------------------------------------------------- full-size SD
# 9-contact pinout: the eight SD-bus contacts plus a card-detect
# mechanical switch on pin 9.

_SD_PINOUT = (
    (PinId(1, 'dat3'), Direction.BIDIR, Analog),
    (PinId(2, 'cmd'),  Direction.BIDIR, Analog),
    (PinId(3, 'vss1'), Direction.BIDIR, Analog),
    (PinId(4, 'vdd'),  Direction.BIDIR, Analog),
    (PinId(5, 'clk'),  Direction.BIDIR, Analog),
    (PinId(6, 'vss2'), Direction.BIDIR, Analog),
    (PinId(7, 'dat0'), Direction.BIDIR, Analog),
    (PinId(8, 'dat1'), Direction.BIDIR, Analog),
    (PinId(9, 'dat2'), Direction.BIDIR, Analog),
)


@register('SDCardSlot')
class SDCardSlot(Connector):
    """Full-size SD card slot (board-side).  9 contacts including
    card-detect."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PIN_COUNT     = 9
    PITCH_MM:     ClassVar[float] = 2.54
    PINOUT        = _SD_PINOUT
    FOOTPRINT:    ClassVar[str | None] = "Connector_Card:SD_TE_2041021"



@register('SDCard')
class SDCard(Connector):
    """A full-size SD card.  Modelled as a connector for the same
    reason as MicroSDCard."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PIN_COUNT     = 9
    PITCH_MM:     ClassVar[float] = 2.54
    PINOUT        = _SD_PINOUT
    FOOTPRINT:    ClassVar[str | None] = None



declare_mating_pair(SDCardSlot, SDCard)
