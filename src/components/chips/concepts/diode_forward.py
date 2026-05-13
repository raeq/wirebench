"""Forward-conduction behavioural cell for series-element diodes.

The internal model that a forward-biased rectifier or reverse-
protection diode instantiates so the framework sees it as a real
driver between its anode and cathode.  Without this cell, a diode
in the middle of a supply chain (battery → diode → cap → regulator)
leaves every downstream net floating from the ERC walker's
perspective — there's an anode-side driver but no path through to
the cathode-side net.

Behaviour:

  - v_anode unknown → cathode = 0 V (treat as undriven / reverse-blocked)
  - v_anode ≤ V_F → cathode = 0 V (diode is off, no forward conduction)
  - v_anode  > V_F → cathode = v_anode − V_F (forward-conducting,
                                              minus the forward drop)

This is *not* the right model for diodes wired in OR-matrix
configurations (multiple cathodes tied to one net): each cathode is
declared `Direction.OUT`, and the framework's ERC short-circuit
check treats multiple OUTs on one net as a wiring error.  For
wired-OR designs, use the `DiodeOR` cell to model the logical
behaviour and leave the physical diode parts as passive BIDIRs.

The model is voltage-only and steady-state — it ignores reverse
leakage, recovery time, reverse breakdown, and the soft transition
near V_F.  For analogue / timing-sensitive simulation, substitute a
SPICE .MODEL.  At the framework's ERC / topology level this cell is
enough to make a diode look like a conductor with a drop.
"""
from __future__ import annotations

from typing import ClassVar

from pydantic import validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog


class DiodeForward(FactorNode):
    """Steady-state behavioural model of a forward-conducting diode.

    Ports
    -----
    anode   (IN,  Analog) — voltage applied at the anode terminal
    cathode (OUT, Analog) — voltage driven onto the cathode terminal
                            (= v_anode − V_F when forward-biased,
                            0 V otherwise)

    Constructor sets V_F (the forward voltage drop) — ~0.3 V for a
    Schottky, ~0.7 V for a silicon signal diode, ~1.0 V under load
    for a silicon rectifier.
    """

    __slots__ = ('_v_f', '_ports')

    V_F: ClassVar[float] = 0.7   # default — silicon signal diode

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        v_f: float,
        domain: GroundDomain = ELECTRICAL,
    ) -> None:
        self._v_f = float(v_f)
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
    def v_f(self) -> float:
        return self._v_f

    def evaluate(self) -> None:
        v_anode_raw = self._ports['anode'].value
        v_anode = float(v_anode_raw) if v_anode_raw is not None else 0.0
        if v_anode > self._v_f:
            self._ports['cathode'].drive(v_anode - self._v_f)
        else:
            self._ports['cathode'].drive(0.0)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, anode: float | None) -> float:
        self._assert_no_inputs_wired()
        self._ports['anode'].drive(anode)
        self.evaluate()
        result = self._ports['cathode'].value
        return float(result) if result is not None else 0.0

    def __repr__(self) -> str:
        return (f"DiodeForward(V_F={self._v_f}, "
                f"cathode={self._ports['cathode'].value!r})")
