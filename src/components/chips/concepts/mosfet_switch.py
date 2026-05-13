"""MOSFET-as-switch behavioural cell — circuit-level companion to
a passive MOSFET in a saturated-switch role.

Same precedent as `BJTSwitch` and `SeriesRectifier`: the MOSFET
itself stays Category A passive (BIDIR gate / drain / source); the
saturated-switch role is modelled by this cell wired alongside the
passive part.

`MOSFETSwitch` covers the **logic-level low-side switch** — the
typical hobby use of an N-channel MOSFET driving a load whose other
end sits on a positive rail.  Other roles (high-side P-channel,
analog switch, gate driver into capacitive load) are out of scope
today.

Behaviour:

  - N-channel: drain pulled to source when (V_gate − V_source) > V_GS_TH
  - P-channel: drain pulled to source when (V_source − V_gate) > V_GS_TH
  - Below threshold: drain is driven to None — same convention as
    `BJTSwitch`; downstream readers see "undefined" rather than 0 V
    because the actual off-state voltage depends on the surrounding
    pull-up / pull-down

The model is voltage-only and steady-state: it ignores R_DS(on),
gate capacitance, switching speed, body-diode behaviour, and
linear-region operation.  For accuracy, substitute a SPICE .MODEL.
"""
from __future__ import annotations

from typing import Literal

from pydantic import validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.registry import register
from framework.signals import Analog


@register('MOSFETSwitch')
class MOSFETSwitch(Part):
    """Saturated low-side / high-side switch behaviour, N or P channel.

    Ports
    -----
    gate    (IN,  Analog) — gate-driving signal
    source  (IN,  Analog) — source potential (typically a rail)
    drain   (OUT, Analog) — driven to source when FET on,
                            to None (undriven) when off

    Constructor takes the device channel (`'n'` or `'p'`) and a
    threshold voltage.  Use ~2.0 V for logic-level FETs
    (BS170, 2N7000, IRLB8721) and ~4.0 V for non-logic-level
    power FETs (IRFZ44N etc.).
    """

    __slots__ = ('_ports', '_channel', '_v_gs_th')

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        channel: Literal['n', 'p'],
        v_gs_th: float = 2.0,
        domain: GroundDomain = ELECTRICAL,
    ) -> None:
        self._channel = channel
        self._v_gs_th = float(v_gs_th)
        self._ports = {
            'gate':   Port('gate',   Direction.IN,  domain,
                           mandatory=False, signal_type=Analog),
            'source': Port('source', Direction.IN,  domain,
                           mandatory=False, signal_type=Analog),
            'drain':  Port('drain',  Direction.OUT, domain,
                           mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def channel(self) -> str:
        return self._channel

    @property
    def v_gs_th(self) -> float:
        return self._v_gs_th

    def evaluate(self) -> None:
        v_g_raw = self._ports['gate'].value
        v_s_raw = self._ports['source'].value
        v_g = float(v_g_raw) if v_g_raw is not None else 0.0
        v_s = float(v_s_raw) if v_s_raw is not None else 0.0
        if self._channel == 'n':
            on = (v_g - v_s) > self._v_gs_th
        else:  # p
            on = (v_s - v_g) > self._v_gs_th
        if on:
            self._ports['drain'].drive(v_s)
        else:
            self._ports['drain'].drive(None)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(
        self,
        gate: float | None,
        source: float | None = 0.0,
    ) -> float | None:
        self._assert_no_inputs_wired()
        self._ports['gate'].drive(gate)
        self._ports['source'].drive(source)
        self.evaluate()
        return self._ports['drain'].value  # type: ignore[no-any-return]

    def __repr__(self) -> str:
        return (f"MOSFETSwitch(channel={self._channel!r}, "
                f"V_GS_TH={self._v_gs_th}, "
                f"drain={self._ports['drain'].value!r})")
