"""Series-rectifier behavioural cell — circuit-level companion to a
forward-conducting diode in a supply chain.

A diode in series with a supply rail (reverse-polarity protection on
a battery input, the rectifier diode after a transformer secondary,
the freewheel-diode-as-rectifier in a flyback supply) must propagate
its anode voltage through to its cathode net minus the forward drop.
The physical diode in the framework is a `Category A passive` part —
it has no internal behavioural cell — so on its own the cathode-side
net has no driver and the framework's ERC walk flags it as floating.

`SeriesRectifier` is the circuit-level cell that supplies the
missing driver.  Instantiate it alongside the passive diode and wire
it in parallel: the anode net carries the upstream supply *and* the
cell's `input` port; the cathode net carries the downstream load
*and* the cell's `output` port.  The passive diode appears on the
BOM, on the schematic, and on the KiCad netlist — its purchase /
soldering / labelling are real; the cell exists only inside the
framework's evaluation graph to make ERC see the cathode-side net
as having a driver.

Same shape as the existing `DiodeOR` cell that handles wired-OR
matrices (see `components/chips/concepts/diode_or.py`) — a passive
diode plus a circuit-level cell that models the *function* the
diode performs in this particular topology, leaving the diode's
class free to be used in different roles in different designs.

When *not* to use this cell:

- **OR-matrix configurations** (multiple diodes' cathodes tied to
  one net) — use `DiodeOR` instead; that cell handles the
  highest-wins arithmetic for you.
- **Flyback / freewheel diodes** across a relay coil or motor —
  the diode sits on an already-driven net (the rail above it, the
  switch below); no cell is needed.
- **Voltage-clamp / decoupling diodes** — the surrounding net
  already has a driver; the diode is a marker.
- **Zener shunt regulators / crowbars** — use `ZenerShunt`
  instead (Phase 2 of the behavioural-cell audit).

The model is voltage-only and steady-state — for accurate
analogue / reverse-leakage / temperature simulation, substitute a
SPICE .MODEL on the underlying diode part.
"""
from __future__ import annotations

from pydantic import validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.registry import register
from framework.signals import Analog


@register('SeriesRectifier')
class SeriesRectifier(Part):
    """Steady-state forward-conducting-diode behaviour for a
    series-rectifier role.  Constructor takes the diode's forward
    voltage drop; `evaluate()` drives `output` to (input − V_F)
    above the forward threshold and to 0 V below it.

    Ports
    -----
    input   (IN,  Analog) — anode-side net (upstream supply)
    output  (OUT, Analog) — cathode-side net (downstream load)

    Patterned on `DiodeOR`: registered for save / load, no refdes
    (the cell is a framework-internal driver, not a procurable
    part — the physical diode on the same nets is what the BOM
    sees).
    """

    __slots__ = ('_ports', '_v_f')

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        v_f: float,
        domain: GroundDomain = ELECTRICAL,
    ) -> None:
        self._v_f = float(v_f)
        self._ports = {
            'input':  Port('input',  Direction.IN,  domain,
                           mandatory=False, signal_type=Analog),
            'output': Port('output', Direction.OUT, domain,
                           mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def v_f(self) -> float:
        return self._v_f

    def evaluate(self) -> None:
        v_in_raw = self._ports['input'].value
        v_in = float(v_in_raw) if v_in_raw is not None else 0.0
        if v_in > self._v_f:
            self._ports['output'].drive(v_in - self._v_f)
        else:
            self._ports['output'].drive(0.0)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, input: float | None) -> float:
        self._assert_no_inputs_wired()
        self._ports['input'].drive(input)
        self.evaluate()
        result = self._ports['output'].value
        return float(result) if result is not None else 0.0

    def __repr__(self) -> str:
        return (f"SeriesRectifier(V_F={self._v_f}, "
                f"output={self._ports['output'].value!r})")
