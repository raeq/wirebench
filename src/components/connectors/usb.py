"""USB connector families — Type-A, Type-B, Micro-B, Type-C.

Each family ships as a receptacle/plug pair.  Plug PINOUTs mirror the
receptacle's so positional mating wires VBUS-to-VBUS, D+-to-D+, etc.
"""
from __future__ import annotations

from typing import ClassVar

from framework.connector import Connector, declare_mating_pair
from framework.pin import PinId
from framework.port import Direction
from framework.signals import Analog


# ---------------------------------------------------------------- Type-A
# USB 2.0 only.  USB 3.x SuperSpeed receptacles are a separate part.

_USB_A_PINOUT = (
    (PinId(1, 'VBUS'),  Direction.BIDIR, Analog),
    (PinId(2, 'D_neg'), Direction.BIDIR, Analog),
    (PinId(3, 'D_pos'), Direction.BIDIR, Analog),
    (PinId(4, 'GND'),   Direction.BIDIR, Analog),
)


class USBAReceptacle(Connector):
    """Standard USB-A receptacle (board-side)."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PIN_COUNT     = 4
    PITCH_MM:     ClassVar[float] = 2.5  # nominal contact pitch on Type-A
    PINOUT        = _USB_A_PINOUT


class USBAPlug(Connector):
    """Standard USB-A plug (cable-side)."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PIN_COUNT     = 4
    PITCH_MM:     ClassVar[float] = 2.5
    PINOUT        = _USB_A_PINOUT


declare_mating_pair(USBAReceptacle, USBAPlug)


# ---------------------------------------------------------------- Type-B
_USB_B_PINOUT = (
    (PinId(1, 'VBUS'),  Direction.BIDIR, Analog),
    (PinId(2, 'D_neg'), Direction.BIDIR, Analog),
    (PinId(3, 'D_pos'), Direction.BIDIR, Analog),
    (PinId(4, 'GND'),   Direction.BIDIR, Analog),
)


class USBBReceptacle(Connector):
    """USB Type-B receptacle (square printer-style)."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PIN_COUNT     = 4
    PITCH_MM:     ClassVar[float] = 2.0
    PINOUT        = _USB_B_PINOUT


class USBBPlug(Connector):
    """USB Type-B plug."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PIN_COUNT     = 4
    PITCH_MM:     ClassVar[float] = 2.0
    PINOUT        = _USB_B_PINOUT


declare_mating_pair(USBBReceptacle, USBBPlug)


# ------------------------------------------------------------- Micro-B
_USB_MICRO_B_PINOUT = (
    (PinId(1, 'VBUS'),  Direction.BIDIR, Analog),
    (PinId(2, 'D_neg'), Direction.BIDIR, Analog),
    (PinId(3, 'D_pos'), Direction.BIDIR, Analog),
    (PinId(4, 'ID'),    Direction.BIDIR, Analog),
    (PinId(5, 'GND'),   Direction.BIDIR, Analog),
)


class USBMicroBReceptacle(Connector):
    """USB Micro-B receptacle."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PIN_COUNT     = 5
    PITCH_MM:     ClassVar[float] = 0.65
    PINOUT        = _USB_MICRO_B_PINOUT


class USBMicroBPlug(Connector):
    """USB Micro-B plug."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PIN_COUNT     = 5
    PITCH_MM:     ClassVar[float] = 0.65
    PINOUT        = _USB_MICRO_B_PINOUT


declare_mating_pair(USBMicroBReceptacle, USBMicroBPlug)


# ---------------------------------------------------------------- Type-C
# 24-pin full pinout per the USB-C standard. Both rows (A and B) are
# included; positional mating covers both insertion orientations
# because the pinout is symmetric.
_USB_C_PINOUT = (
    (PinId( 1, 'A1_GND'),  Direction.BIDIR, Analog),
    (PinId( 2, 'A2_TX1p'), Direction.BIDIR, Analog),
    (PinId( 3, 'A3_TX1n'), Direction.BIDIR, Analog),
    (PinId( 4, 'A4_VBUS'), Direction.BIDIR, Analog),
    (PinId( 5, 'A5_CC1'),  Direction.BIDIR, Analog),
    (PinId( 6, 'A6_Dp1'),  Direction.BIDIR, Analog),
    (PinId( 7, 'A7_Dn1'),  Direction.BIDIR, Analog),
    (PinId( 8, 'A8_SBU1'), Direction.BIDIR, Analog),
    (PinId( 9, 'A9_VBUS'), Direction.BIDIR, Analog),
    (PinId(10, 'A10_RX2n'), Direction.BIDIR, Analog),
    (PinId(11, 'A11_RX2p'), Direction.BIDIR, Analog),
    (PinId(12, 'A12_GND'), Direction.BIDIR, Analog),
    (PinId(13, 'B1_GND'),  Direction.BIDIR, Analog),
    (PinId(14, 'B2_TX2p'), Direction.BIDIR, Analog),
    (PinId(15, 'B3_TX2n'), Direction.BIDIR, Analog),
    (PinId(16, 'B4_VBUS'), Direction.BIDIR, Analog),
    (PinId(17, 'B5_CC2'),  Direction.BIDIR, Analog),
    (PinId(18, 'B6_Dp2'),  Direction.BIDIR, Analog),
    (PinId(19, 'B7_Dn2'),  Direction.BIDIR, Analog),
    (PinId(20, 'B8_SBU2'), Direction.BIDIR, Analog),
    (PinId(21, 'B9_VBUS'), Direction.BIDIR, Analog),
    (PinId(22, 'B10_RX1n'), Direction.BIDIR, Analog),
    (PinId(23, 'B11_RX1p'), Direction.BIDIR, Analog),
    (PinId(24, 'B12_GND'), Direction.BIDIR, Analog),
)


class USBCReceptacle(Connector):
    """USB Type-C receptacle (full 24-pin)."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PIN_COUNT     = 24
    PITCH_MM:     ClassVar[float] = 0.5
    PINOUT        = _USB_C_PINOUT


class USBCPlug(Connector):
    """USB Type-C plug (full 24-pin)."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PIN_COUNT     = 24
    PITCH_MM:     ClassVar[float] = 0.5
    PINOUT        = _USB_C_PINOUT


declare_mating_pair(USBCReceptacle, USBCPlug)
