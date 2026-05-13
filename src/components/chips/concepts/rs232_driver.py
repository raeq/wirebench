"""RS-232 driver/receiver behavioural cell.

A chip like the MAX232 has two roles per channel:

- **TX (driver)**: take a TTL-level digital input (0 V or VCC) and
  drive a corresponding RS-232 analog output at ±10 V — *inverted*
  per the RS-232 spec (logic 0 → +10 V "space", logic 1 → -10 V
  "mark").
- **RX (receiver)**: take an RS-232 analog input (anywhere from
  -15 V to +15 V) and drive a TTL-level digital output — also
  inverted (input < 0 V → output HIGH, input > 0 V → output LOW).

For framework topology purposes the inversion is what matters —
without the cell, both `T_OUT` and `R_OUT` chip pins would have
no driver and any net connected to them would float.  Output
levels are simplified: TX drives ±9 V (within typical MAX232
output range) and RX drives 0/5 V Digital.

The charge-pump rail outputs (`V_POS`, `V_NEG`) are not modelled
here — they're handled by the chip class instantiating a
`ChargePumpRails` cell or driving them to constants directly.
"""
from __future__ import annotations

from typing import ClassVar

from pydantic import validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog, Digital


class RS232Driver(FactorNode):
    """One TX / RX channel pair for an RS-232 line driver.

    Ports
    -----
    tx_in   (IN,  Digital) — TTL transmit input
    tx_out  (OUT, Analog)  — RS-232 transmit output (±9 V, inverted)
    rx_in   (IN,  Analog)  — RS-232 receive input
    rx_out  (OUT, Digital) — TTL receive output (inverted)
    """

    TX_HIGH: ClassVar[float] = -9.0   # RS-232 "mark" (logic 1)
    TX_LOW:  ClassVar[float] = +9.0   # RS-232 "space" (logic 0)

    __slots__ = ('_ports',)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._ports = {
            'tx_in':  Port('tx_in',  Direction.IN,  domain,
                           mandatory=False, signal_type=Digital),
            'tx_out': Port('tx_out', Direction.OUT, domain,
                           mandatory=False, signal_type=Analog),
            'rx_in':  Port('rx_in',  Direction.IN,  domain,
                           mandatory=False, signal_type=Analog),
            'rx_out': Port('rx_out', Direction.OUT, domain,
                           mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    def evaluate(self) -> None:
        # TX side: invert the TTL input and drive ±9 V.
        tx_in_v = self._ports['tx_in'].value
        if tx_in_v is None:
            self._ports['tx_out'].drive(None)
        else:
            high = bool(Digital(tx_in_v))
            self._ports['tx_out'].drive(self.TX_HIGH if high else self.TX_LOW)
        # RX side: invert the RS-232 input and drive TTL.  RS-232
        # convention: positive voltage = logic 0, negative = logic 1.
        rx_in_v = self._ports['rx_in'].value
        if rx_in_v is None:
            self._ports['rx_out'].drive(None)
        else:
            self._ports['rx_out'].drive(float(rx_in_v) < 0.0)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(
        self,
        tx_in: bool | None = None,
        rx_in: float | None = None,
    ) -> tuple[float | None, bool | None]:
        self._assert_no_inputs_wired()
        self._ports['tx_in'].drive(tx_in)
        self._ports['rx_in'].drive(rx_in)
        self.evaluate()
        return self._ports['tx_out'].value, self._ports['rx_out'].value

    def __repr__(self) -> str:
        return (f"RS232Driver(tx_out={self._ports['tx_out'].value!r}, "
                f"rx_out={self._ports['rx_out'].value!r})")
