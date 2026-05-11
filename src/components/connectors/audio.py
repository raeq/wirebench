"""3.5 mm audio jacks and plugs — TRS (stereo) and TRRS (stereo + mic).

TRS: tip = left, ring = right, sleeve = GND.

TRRS pinout varies by standard:
  - CTIA (Apple / modern): tip = L, ring1 = R, ring2 = GND, sleeve = MIC.
  - OMTP (older Nokia, etc.): tip = L, ring1 = R, ring2 = MIC, sleeve = GND.
The codebase models contact identity only; the consumer decides which
wiring they want.  The naming `ring2`/`sleeve` matches the physical
contact position; semantic interpretation (GND vs MIC) is external.
"""
from __future__ import annotations

from typing import ClassVar

from framework.connector import Connector, declare_mating_pair
from framework.pin import PinId
from framework.port import Direction
from framework.signals import Analog
from framework.registry import register


_TRS_PINOUT = (
    (PinId(1, 'tip'),    Direction.BIDIR, Analog),
    (PinId(2, 'ring'),   Direction.BIDIR, Analog),
    (PinId(3, 'sleeve'), Direction.BIDIR, Analog),
)


@register('Audio3p5mmTRSJack')
class Audio3p5mmTRSJack(Connector):
    """3.5 mm TRS audio jack (board-side)."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PIN_COUNT     = 3
    PITCH_MM:     ClassVar[float] = 3.5  # tip-ring-sleeve separation, nominal
    PINOUT        = _TRS_PINOUT
    FOOTPRINT:    ClassVar[str | None] = "Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles"



@register('Audio3p5mmTRSPlug')
class Audio3p5mmTRSPlug(Connector):
    """3.5 mm TRS audio plug (cable-side)."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PIN_COUNT     = 3
    PITCH_MM:     ClassVar[float] = 3.5
    PINOUT        = _TRS_PINOUT
    FOOTPRINT:    ClassVar[str | None] = "Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles"



declare_mating_pair(Audio3p5mmTRSJack, Audio3p5mmTRSPlug)


_TRRS_PINOUT = (
    (PinId(1, 'tip'),    Direction.BIDIR, Analog),
    (PinId(2, 'ring1'),  Direction.BIDIR, Analog),
    (PinId(3, 'ring2'),  Direction.BIDIR, Analog),
    (PinId(4, 'sleeve'), Direction.BIDIR, Analog),
)


@register('Audio3p5mmTRRSJack')
class Audio3p5mmTRRSJack(Connector):
    """3.5 mm TRRS audio jack (4 contacts: tip/ring1/ring2/sleeve).
    Wiring convention (CTIA vs OMTP) is a consumer decision."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PIN_COUNT     = 4
    PITCH_MM:     ClassVar[float] = 3.5
    PINOUT        = _TRRS_PINOUT
    FOOTPRINT:    ClassVar[str | None] = "Connector_Audio:Jack_3.5mm_TRRS_QingPu_WQP-PJ398SM_Vertical"



@register('Audio3p5mmTRRSPlug')
class Audio3p5mmTRRSPlug(Connector):
    """3.5 mm TRRS audio plug."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PIN_COUNT     = 4
    PITCH_MM:     ClassVar[float] = 3.5
    PINOUT        = _TRRS_PINOUT
    FOOTPRINT:    ClassVar[str | None] = "Connector_Audio:Jack_3.5mm_TRRS_QingPu_WQP-PJ398SM_Vertical"



declare_mating_pair(Audio3p5mmTRRSJack, Audio3p5mmTRRSPlug)
