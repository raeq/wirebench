"""Fixed PCB-mount screw terminal blocks.

Common pitches: 5.08 mm (industrial), 3.5 mm (compact), 2.54 mm
(signal-level).  No in-model mating partner — the "other end" is bare
wire, which is not a connector.
"""
from __future__ import annotations

from framework.connector import Connector
from framework.pin import PinId
from framework.port import Direction
from framework.signals import Analog


class ScrewTerminalBlock(Connector):
    """PCB-mount screw terminal block."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    # No PITCH_MM / PIN_COUNT class attributes — both are constructor
    # parameters.  MATES_WITH stays None (inherited).

    def _build_pinout(self) -> tuple[tuple[PinId, Direction, type], ...]:
        return tuple((PinId(i, f'p{i}'), Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))
