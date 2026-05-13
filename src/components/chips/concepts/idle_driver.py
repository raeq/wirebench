"""Idle-driver placeholder cell — drives one OUT port to a fixed
idle value to satisfy the framework's "every OUT pin needs a
behavioural cell" invariant for chips whose actual behaviour is
protocol-driven, bus-driven, or otherwise too complex to model
behaviourally at this layer.

Used for: protocol-bus chips (I²C, SPI, 1-Wire) where the output
behaviour is determined by the bus master's interactions; sensors
whose digital outputs are protocol-encoded; specialty ICs whose
internal state machines aren't worth modelling for framework-level
ERC; interrupt / status / sync outputs that idle at a known
level until an event fires.

Pick the signal type (`Digital` / `Analog`) and the idle value at
construction.  The cell drives that value forever — Phase 9's
construction-time invariant is satisfied; the user's design wires
the chip up normally, and a real-world build does whatever the
chip's protocol actually does.

This is intentionally a low-fidelity model.  Demos that need
behavioural accuracy on these pins should reach for SPICE or a
cycle-accurate emulator.
"""
from __future__ import annotations

from typing import Any

from pydantic import validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction


class IdleDriver(Part):
    """Drives `out` to a fixed value (or None for "undriven").

    Ports
    -----
    out  (OUT, signal_type chosen at construction)
    """

    __slots__ = ('_ports', '_idle_value')

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        signal_type: type,
        idle_value: Any = None,
        domain: GroundDomain = ELECTRICAL,
    ) -> None:
        self._idle_value = idle_value
        self._ports = {
            'out': Port('out', Direction.OUT, domain,
                        mandatory=False, signal_type=signal_type),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def idle_value(self) -> Any:
        return self._idle_value

    def evaluate(self) -> None:
        self._ports['out'].drive(self._idle_value)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> Any:
        self._assert_no_inputs_wired()
        self.evaluate()
        return self._idle_value

    def __repr__(self) -> str:
        return f"IdleDriver(out={self._idle_value!r})"
