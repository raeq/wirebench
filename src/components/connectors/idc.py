"""IDC ribbon-cable connectors — boxed/shrouded dual-row headers and
their mating insulation-displacement sockets.  Used for programming
headers (10-pin SWD/ARM), internal PC cabling, modular synth power,
custom panel-to-board ribbons.
"""
from __future__ import annotations

from framework.connector import Connector, declare_mating_pair
from framework.pin import PinId
from framework.port import Direction
from framework.signals import Analog
from framework.registry import register


@register('IDC2xNMale')
class IDC2xNMale(Connector):
    """2×N shrouded male IDC header, board-side."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'

    def _build_pinout(self) -> tuple[tuple[PinId, Direction, type], ...]:
        return tuple((PinId(i, f'p{i}'), Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))


@register('IDC2xNSocket')
class IDC2xNSocket(Connector):
    """2×N female IDC ribbon-cable socket."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'

    def _build_pinout(self) -> tuple[tuple[PinId, Direction, type], ...]:
        return tuple((PinId(i, f'p{i}'), Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))


declare_mating_pair(IDC2xNMale, IDC2xNSocket)
