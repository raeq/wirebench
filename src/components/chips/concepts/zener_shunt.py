"""Zener-shunt behavioural cell — circuit-level companion to a
reverse-biased Zener acting as a voltage clamp / shunt regulator.

A passive Zener in a shunt-regulator topology:

    V_in ──[ series resistor R ]──┬── (clamped to V_Z + V_anode)
                                  │
                                Zener
                                  │
                                 GND

The cathode-side junction is *clamped* to V_anode + V_Z by the
Zener's reverse breakdown.  In the framework's voltage-only graph the
diode is a passive Category-A part (BIDIR anode/cathode); the series
resistor R is also opaque (no `evaluate` driver); so the
cathode-side net has no driver and ERC flags it as floating.

`ZenerShunt` is the circuit-level cell that supplies that driver in
this topology — same pattern as `SeriesRectifier`:
instantiate alongside the passive Zener and wire the cell's
`cathode` port to the same net as the diode's cathode, and the
cell's `anode` port to the diode's anode side (typically ground).

**When `ZenerShunt` is *not* the right cell**

If the cathode-side net already has a driver from elsewhere (a
linear regulator's OUTPUT pin, another behavioural cell, a Rail in
parallel), wiring the cell's OUT-direction `cathode` to that net
creates a second driver and the framework raises
`ShortCircuitError`.  The cell models the role "Zener is the
primary regulator of this net," not the role "Zener is a fail-safe
clamp on an already-driven net".

For fail-safe / crowbar uses (Zener wired across a regulated rail,
expected to conduct only on regulator failure), no cell is needed —
the rail already has a driver, the Zener sits there as a passive
component, and the framework is happy.  Adding `ZenerShunt` to that
topology would break ERC.

**Voltage-only-graph limitation**

The cell drives `cathode = anode + V_Z` unconditionally.  Real
silicon only clamps when the upstream source *would otherwise*
exceed that value; below the breakdown the Zener is high-impedance
and the upstream source wins.  The framework's evaluation order
isn't iterative — it can't compute "whichever value is lower
wins" between two would-be drivers.  For accurate clamp-voltage
simulation, substitute a SPICE .MODEL on the underlying Zener.
"""
from __future__ import annotations

from pydantic import validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.registry import register
from framework.signals import Analog


@register('ZenerShunt')
class ZenerShunt(Part):
    """Steady-state reverse-biased-Zener-as-shunt-clamp behaviour.

    Ports
    -----
    anode   (IN,  Analog) — the Zener's anode-side net (typically
                            ground)
    cathode (OUT, Analog) — the Zener's cathode-side net; driven
                            unconditionally to (V_anode + V_Z)

    Patterned on `SeriesRectifier` and `DiodeOR`: registered for
    save / load, no refdes (the cell is a framework-internal driver,
    not a procurable part — the physical Zener on the same nets is
    what the BOM sees).
    """

    __slots__ = ('_ports', '_v_z')

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        v_z: float,
        domain: GroundDomain = ELECTRICAL,
    ) -> None:
        self._v_z = float(v_z)
        self._ports = {
            'anode':   Port('anode',   Direction.IN,  domain,
                            mandatory=False, signal_type=Analog),
            'cathode': Port('cathode', Direction.OUT, domain,
                            mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def v_z(self) -> float:
        return self._v_z

    def evaluate(self) -> None:
        v_anode_raw = self._ports['anode'].value
        v_anode = float(v_anode_raw) if v_anode_raw is not None else 0.0
        self._ports['cathode'].drive(v_anode + self._v_z)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, anode: float | None) -> float:
        self._assert_no_inputs_wired()
        self._ports['anode'].drive(anode)
        self.evaluate()
        result = self._ports['cathode'].value
        return float(result) if result is not None else 0.0

    def __repr__(self) -> str:
        return (f"ZenerShunt(V_Z={self._v_z}, "
                f"cathode={self._ports['cathode'].value!r})")
