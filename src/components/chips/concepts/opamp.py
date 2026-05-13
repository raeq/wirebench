"""Op-amp behavioural cell — the unit of design for every op-amp
chip in the catalogue (LM358, LM324, TL072, TL074, LM741, MCP6002,
LMV358, OPA2134).

A real op-amp has high open-loop gain (10^5–10^6); used without
feedback, its output saturates to whichever supply rail the inputs
favour.  At the framework's voltage-only ERC level, that saturation
behaviour is the *whole* model — the linear region (where feedback
keeps `V+ ≈ V−`) is too narrow to matter for topology validation,
and accurate linear-region gain belongs in SPICE.

So the cell behaves as a rail-to-rail comparator with analog
output: when `v_in_pos > v_in_neg`, drive `out` to `v_supply`; when
`v_in_pos < v_in_neg`, drive `out` to `v_gnd`; at exact equality,
drive the midpoint.  This matches the standard "high-gain ideal
op-amp" textbook model.

The cell has no notion of feedback — wiring `out` back to `v_in_neg`
through a resistor doesn't compute the unity-gain-buffer output the
way a SPICE simulation would.  Designs that depend on feedback
should rely on the cell solely for ERC validation and look to
SPICE for behavioural accuracy.

For multi-channel chips (LM358 dual, LM324 quad, TL074 quad),
instantiate one `OpAmp` per channel and share the chip's V_POS /
V_GND pin internal faces across all cells.
"""
from __future__ import annotations

from pydantic import validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog


class OpAmp(FactorNode):
    """Rail-to-rail saturating op-amp behaviour.

    Ports
    -----
    v_in_pos  (IN,  Analog) — non-inverting input
    v_in_neg  (IN,  Analog) — inverting input
    v_supply  (IN,  Analog) — positive supply rail
    v_gnd     (IN,  Analog) — negative supply (or ground)
    out       (OUT, Analog) — output, saturates to v_supply or v_gnd
    """

    __slots__ = ('_ports',)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._ports = {
            'v_in_pos': Port('v_in_pos', Direction.IN,  domain,
                             mandatory=False, signal_type=Analog),
            'v_in_neg': Port('v_in_neg', Direction.IN,  domain,
                             mandatory=False, signal_type=Analog),
            'v_supply': Port('v_supply', Direction.IN,  domain,
                             mandatory=False, signal_type=Analog),
            'v_gnd':    Port('v_gnd',    Direction.IN,  domain,
                             mandatory=False, signal_type=Analog),
            'out':      Port('out',      Direction.OUT, domain,
                             mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    def evaluate(self) -> None:
        vp_raw = self._ports['v_in_pos'].value
        vn_raw = self._ports['v_in_neg'].value
        vs_raw = self._ports['v_supply'].value
        vg_raw = self._ports['v_gnd'].value
        vp = float(vp_raw) if vp_raw is not None else 0.0
        vn = float(vn_raw) if vn_raw is not None else 0.0
        vs = float(vs_raw) if vs_raw is not None else 0.0
        vg = float(vg_raw) if vg_raw is not None else 0.0
        if vp > vn:
            self._ports['out'].drive(vs)
        elif vp < vn:
            self._ports['out'].drive(vg)
        else:
            self._ports['out'].drive((vs + vg) / 2.0)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(
        self,
        v_in_pos: float | None,
        v_in_neg: float | None,
        v_supply: float | None = 5.0,
        v_gnd: float | None = 0.0,
    ) -> float:
        self._assert_no_inputs_wired()
        self._ports['v_in_pos'].drive(v_in_pos)
        self._ports['v_in_neg'].drive(v_in_neg)
        self._ports['v_supply'].drive(v_supply)
        self._ports['v_gnd'].drive(v_gnd)
        self.evaluate()
        result = self._ports['out'].value
        return float(result) if result is not None else 0.0

    def __repr__(self) -> str:
        return f"OpAmp(out={self._ports['out'].value!r})"
