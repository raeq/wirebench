"""Optocoupler behavioural cell — the input LED plus output
phototransistor as a single behavioural unit.

A standard optocoupler has four pins: anode + cathode (input LED
side) and collector + emitter (output phototransistor side).
Current through the LED makes it emit IR, which the
phototransistor's base-equivalent picks up, switching the output
transistor on.

The cell drives the collector pin's internal face based on whether
the input LED is forward-biased above its V_F threshold (~1.2 V
for an IR LED).  When on, the collector is pulled to the emitter
potential (saturated phototransistor); when off, the collector is
driven to None — the actual off-state voltage depends on the
external pull-up the user adds.

For TRIAC-output optocouplers (MOC3021), use `TriacOptocoupler`
instead.
"""
from __future__ import annotations

from typing import ClassVar

from pydantic import validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog


class Optocoupler(FactorNode):
    """Phototransistor-output optocoupler cell.

    Ports
    -----
    anode     (IN,  Analog) — input LED anode
    cathode   (IN,  Analog) — input LED cathode
    emitter   (IN,  Analog) — output transistor emitter
    collector (OUT, Analog) — output transistor collector

    Class constant `V_F_LED` sets the input LED threshold; default
    1.2 V is typical for IR LEDs in standard optocouplers.
    """

    V_F_LED: ClassVar[float] = 1.2

    __slots__ = ('_ports',)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._ports = {
            'anode':     Port('anode',     Direction.IN,  domain,
                              mandatory=False, signal_type=Analog),
            'cathode':   Port('cathode',   Direction.IN,  domain,
                              mandatory=False, signal_type=Analog),
            'emitter':   Port('emitter',   Direction.IN,  domain,
                              mandatory=False, signal_type=Analog),
            'collector': Port('collector', Direction.OUT, domain,
                              mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    def evaluate(self) -> None:
        v_a_raw = self._ports['anode'].value
        v_k_raw = self._ports['cathode'].value
        v_e_raw = self._ports['emitter'].value
        v_a = float(v_a_raw) if v_a_raw is not None else 0.0
        v_k = float(v_k_raw) if v_k_raw is not None else 0.0
        v_e = float(v_e_raw) if v_e_raw is not None else 0.0
        led_on = (v_a - v_k) > self.V_F_LED
        if led_on:
            # Phototransistor saturated: collector ≈ emitter.
            self._ports['collector'].drive(v_e)
        else:
            self._ports['collector'].drive(None)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(
        self,
        anode: float | None,
        cathode: float | None = 0.0,
        emitter: float | None = 0.0,
    ) -> float | None:
        self._assert_no_inputs_wired()
        self._ports['anode'].drive(anode)
        self._ports['cathode'].drive(cathode)
        self._ports['emitter'].drive(emitter)
        self.evaluate()
        return self._ports['collector'].value  # type: ignore[no-any-return]

    def __repr__(self) -> str:
        return f"Optocoupler(collector={self._ports['collector'].value!r})"


class TriacOptocoupler(FactorNode):
    """TRIAC-output optocoupler (e.g. MOC3021) — the output side is a
    bidirectional TRIAC, not a phototransistor.

    Ports
    -----
    anode    (IN,  Analog) — input LED anode
    cathode  (IN,  Analog) — input LED cathode
    mt1      (IN,  Analog) — TRIAC main terminal 1 (zero-crossing-
                             switched in some variants; for the
                             framework, this is just a reader)
    mt2      (OUT, Analog) — TRIAC main terminal 2; driven to mt1
                             when the LED is on, None when off

    The framework can't model the bidirectional / zero-crossing
    behaviour of a real TRIAC; this cell models the on/off
    coupling for ERC purposes.  For accurate AC-switching
    simulation, SPICE is the right tool.
    """

    V_F_LED: ClassVar[float] = 1.2

    __slots__ = ('_ports',)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._ports = {
            'anode':   Port('anode',   Direction.IN,  domain,
                            mandatory=False, signal_type=Analog),
            'cathode': Port('cathode', Direction.IN,  domain,
                            mandatory=False, signal_type=Analog),
            'mt1':     Port('mt1',     Direction.IN,  domain,
                            mandatory=False, signal_type=Analog),
            'mt2':     Port('mt2',     Direction.OUT, domain,
                            mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    def evaluate(self) -> None:
        v_a_raw = self._ports['anode'].value
        v_k_raw = self._ports['cathode'].value
        v_mt1_raw = self._ports['mt1'].value
        v_a = float(v_a_raw) if v_a_raw is not None else 0.0
        v_k = float(v_k_raw) if v_k_raw is not None else 0.0
        v_mt1 = float(v_mt1_raw) if v_mt1_raw is not None else 0.0
        led_on = (v_a - v_k) > self.V_F_LED
        if led_on:
            self._ports['mt2'].drive(v_mt1)
        else:
            self._ports['mt2'].drive(None)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(
        self,
        anode: float | None,
        cathode: float | None = 0.0,
        mt1: float | None = 0.0,
    ) -> float | None:
        self._assert_no_inputs_wired()
        self._ports['anode'].drive(anode)
        self._ports['cathode'].drive(cathode)
        self._ports['mt1'].drive(mt1)
        self.evaluate()
        return self._ports['mt2'].value  # type: ignore[no-any-return]

    def __repr__(self) -> str:
        return f"TriacOptocoupler(mt2={self._ports['mt2'].value!r})"
