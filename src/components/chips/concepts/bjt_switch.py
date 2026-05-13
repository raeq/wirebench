"""BJT-as-switch behavioural cell — circuit-level companion to a
passive bipolar transistor in a saturated-switch role.

A bipolar transistor in the framework is **Category A passive**
(per the same precedent as diodes): its directional behaviour is
a property of the *circuit using it*, not of the part itself.  A
2N3904 in one design is a common-emitter switch driving a relay
coil; in another it's a common-collector follower; in a third
it's the input differential pair of an analog stage.  Baking one
role into the transistor class would commit it to that single
use; instead, the role-specific behavioural cell goes at the
circuit level alongside the passive part.

`BJTSwitch` is the cell for the **saturated common-emitter
switch** role — the typical hobby use of a BJT.  Wire it
alongside the passive transistor:

```python
self.q1 = Q2N3904(refdes_number=1)
self.q1_switch = BJTSwitch(polarity='npn')
wire(self.driving_signal, self.q1.b, self.q1_switch.ports['base'])
wire(self.q1.e,           self.gnd.out, self.q1_switch.ports['emitter'])
wire(self.q1.c,           self.load,    self.q1_switch.ports['collector'])
```

The physical Q1 appears on the BOM and on the netlist; the cell
drives the collector net from base / emitter / polarity.

Behaviour:

  - NPN: collector pulled to emitter when (V_base − V_emitter) > V_BE_ON
  - PNP: collector pulled to emitter when (V_emitter − V_base) > V_BE_ON
  - Below threshold: collector is driven to None (the framework's
    "undriven" value) — the cell is still an OUT driver in ERC
    terms but emits no value; any IN reading the net sees None,
    which is honest for an off transistor whose actual collector
    voltage is whatever the surrounding pull-up establishes (the
    framework's voltage-only graph can't propagate that)

For amplifier / linear-region roles, this cell is the wrong
model — a future `BJTAmplifier` could provide a small-signal
linear approximation, but it isn't in scope today.

For Darlington pairs (TIP120 etc.), instantiate with a higher
`v_be_on` (≈1.4 V — two BE junctions in series).
"""
from __future__ import annotations

from typing import Literal

from pydantic import validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.registry import register
from framework.signals import Analog


@register('BJTSwitch')
class BJTSwitch(FactorNode):
    """Saturated common-emitter switch behaviour, NPN or PNP.

    Ports
    -----
    base      (IN,  Analog) — base-driving signal
    emitter   (IN,  Analog) — emitter potential (typically a rail)
    collector (OUT, Analog) — driven to emitter when transistor on,
                              to None (undriven) when off

    Constructor takes the device polarity (`'npn'` or `'pnp'`)
    and optionally an override for the base-emitter turn-on
    voltage (default 0.7 V; pass ≈1.4 V for a Darlington).
    """

    __slots__ = ('_ports', '_polarity', '_v_be_on')

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        polarity: Literal['npn', 'pnp'],
        v_be_on: float = 0.7,
        domain: GroundDomain = ELECTRICAL,
    ) -> None:
        self._polarity = polarity
        self._v_be_on = float(v_be_on)
        self._ports = {
            'base':      Port('base',      Direction.IN,  domain,
                              mandatory=False, signal_type=Analog),
            'emitter':   Port('emitter',   Direction.IN,  domain,
                              mandatory=False, signal_type=Analog),
            'collector': Port('collector', Direction.OUT, domain,
                              mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def polarity(self) -> str:
        return self._polarity

    @property
    def v_be_on(self) -> float:
        return self._v_be_on

    def evaluate(self) -> None:
        v_b_raw = self._ports['base'].value
        v_e_raw = self._ports['emitter'].value
        v_b = float(v_b_raw) if v_b_raw is not None else 0.0
        v_e = float(v_e_raw) if v_e_raw is not None else 0.0
        if self._polarity == 'npn':
            on = (v_b - v_e) > self._v_be_on
        else:  # pnp
            on = (v_e - v_b) > self._v_be_on
        if on:
            # Saturated: collector pulled to emitter potential.
            self._ports['collector'].drive(v_e)
        else:
            # Off: collector is high-impedance; the pull-up
            # establishing the actual voltage is something the
            # voltage-only graph can't propagate.  Drive None so
            # downstream readers see "undefined" rather than 0 V.
            self._ports['collector'].drive(None)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(
        self,
        base: float | None,
        emitter: float | None = 0.0,
    ) -> float | None:
        self._assert_no_inputs_wired()
        self._ports['base'].drive(base)
        self._ports['emitter'].drive(emitter)
        self.evaluate()
        return self._ports['collector'].value  # type: ignore[no-any-return]

    def __repr__(self) -> str:
        return (f"BJTSwitch(polarity={self._polarity!r}, "
                f"V_BE={self._v_be_on}, "
                f"collector={self._ports['collector'].value!r})")
