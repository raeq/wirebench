"""Networking connectors — RJ45 / 8P8C jack and plug."""
from __future__ import annotations

from typing import ClassVar

from framework.connector import Connector, declare_mating_pair
from framework.pin import PinId
from framework.port import Direction
from framework.signals import Analog


# T568B pinout — by far the more common termination in modern installs.
# (The codebase models contact identity only; T568B vs T568A is a wiring
# convention applied externally to the connector.)
_RJ45_T568B_PINOUT = (
    (PinId(1, 'pair_2_white_orange'), Direction.BIDIR, Analog),
    (PinId(2, 'pair_2_orange'),       Direction.BIDIR, Analog),
    (PinId(3, 'pair_3_white_green'),  Direction.BIDIR, Analog),
    (PinId(4, 'pair_1_blue'),         Direction.BIDIR, Analog),
    (PinId(5, 'pair_1_white_blue'),   Direction.BIDIR, Analog),
    (PinId(6, 'pair_3_green'),        Direction.BIDIR, Analog),
    (PinId(7, 'pair_4_white_brown'),  Direction.BIDIR, Analog),
    (PinId(8, 'pair_4_brown'),        Direction.BIDIR, Analog),
)


class RJ45Jack(Connector):
    """RJ45 / 8P8C modular jack, board-side.  T568B pin labels."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PIN_COUNT     = 8
    PITCH_MM:     ClassVar[float] = 1.02
    PINOUT        = _RJ45_T568B_PINOUT


class RJ45Plug(Connector):
    """RJ45 / 8P8C modular plug, cable-side."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PIN_COUNT     = 8
    PITCH_MM:     ClassVar[float] = 1.02
    PINOUT        = _RJ45_T568B_PINOUT


declare_mating_pair(RJ45Jack, RJ45Plug)
