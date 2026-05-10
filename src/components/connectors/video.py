"""Video connectors — HDMI Type-A receptacle and plug."""
from __future__ import annotations

from typing import ClassVar

from framework.connector import Connector, declare_mating_pair
from framework.pin import PinId
from framework.port import Direction
from framework.signals import Analog


# HDMI 1.4 / 2.0 Type-A 19-pin pinout.
_HDMI_TYPE_A_PINOUT = (
    (PinId( 1, 'TMDS_data2_plus'),    Direction.BIDIR, Analog),
    (PinId( 2, 'TMDS_data2_shield'),  Direction.BIDIR, Analog),
    (PinId( 3, 'TMDS_data2_neg'),     Direction.BIDIR, Analog),
    (PinId( 4, 'TMDS_data1_plus'),    Direction.BIDIR, Analog),
    (PinId( 5, 'TMDS_data1_shield'),  Direction.BIDIR, Analog),
    (PinId( 6, 'TMDS_data1_neg'),     Direction.BIDIR, Analog),
    (PinId( 7, 'TMDS_data0_plus'),    Direction.BIDIR, Analog),
    (PinId( 8, 'TMDS_data0_shield'),  Direction.BIDIR, Analog),
    (PinId( 9, 'TMDS_data0_neg'),     Direction.BIDIR, Analog),
    (PinId(10, 'TMDS_clock_plus'),    Direction.BIDIR, Analog),
    (PinId(11, 'TMDS_clock_shield'),  Direction.BIDIR, Analog),
    (PinId(12, 'TMDS_clock_neg'),     Direction.BIDIR, Analog),
    (PinId(13, 'CEC'),                Direction.BIDIR, Analog),
    (PinId(14, 'utility_HEC_neg'),    Direction.BIDIR, Analog),
    (PinId(15, 'DDC_clock'),          Direction.BIDIR, Analog),
    (PinId(16, 'DDC_data'),           Direction.BIDIR, Analog),
    (PinId(17, 'GND'),                Direction.BIDIR, Analog),
    (PinId(18, 'plus_5V'),            Direction.BIDIR, Analog),
    (PinId(19, 'hot_plug_detect'),    Direction.BIDIR, Analog),
)


class HDMITypeAReceptacle(Connector):
    """HDMI Type-A receptacle (board-side)."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PIN_COUNT     = 19
    PITCH_MM:     ClassVar[float] = 0.5
    PINOUT        = _HDMI_TYPE_A_PINOUT


class HDMITypeAPlug(Connector):
    """HDMI Type-A plug (cable-side)."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PIN_COUNT     = 19
    PITCH_MM:     ClassVar[float] = 0.5
    PINOUT        = _HDMI_TYPE_A_PINOUT


declare_mating_pair(HDMITypeAReceptacle, HDMITypeAPlug)
