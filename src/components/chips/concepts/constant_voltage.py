"""Constant-voltage driver cell — drives one OUT port to a fixed
analog value forever.

Useful for chip-internal rails that the framework's voltage-only
graph needs a driver on, but whose actual value is dictated by the
chip's internal circuitry rather than any input.  The MAX232's
V_POS / V_NEG charge-pump rails are the canonical case: they sit
at roughly +10 V and -10 V regardless of input, and any net
connected to them needs a driver.

Behaves like `Rail` but with an arbitrary analog voltage instead
of a Digital HIGH/LOW.
"""
from __future__ import annotations

from pydantic import validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog


class ConstantVoltage(Part):
    """Drives `out` to a fixed analog voltage set at construction.

    Ports
    -----
    out  (OUT, Analog) — driven to the configured voltage
    """

    __slots__ = ('_ports', '_voltage')

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        voltage: float,
        domain: GroundDomain = ELECTRICAL,
    ) -> None:
        self._voltage = float(voltage)
        self._ports = {
            'out': Port('out', Direction.OUT, domain,
                        mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def voltage(self) -> float:
        return self._voltage

    def evaluate(self) -> None:
        self._ports['out'].drive(self._voltage)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> float:
        self._assert_no_inputs_wired()
        self.evaluate()
        return self._voltage

    def __repr__(self) -> str:
        return f"ConstantVoltage({self._voltage} V)"
