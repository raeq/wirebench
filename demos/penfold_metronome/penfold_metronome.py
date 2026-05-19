"""Project 9 — Metronome (after R. A. Penfold, BP107).

An NE555 wired as an astable multivibrator clocks a small speaker
at an adjustable rate — anything from a leisurely 40 BPM to a
sprightly 240+ BPM, depending on the timing-resistor / capacitor
combination.  Penfold's design uses a panel pot in the upper timing
arm so the player can dial in the tempo by ear.

This demo *pairs* with `penfold_one_second_timer` to establish the
two classical astable families in the wirebench catalogue:
    - one_second_timer: op-amp relaxation oscillator with hysteresis
    - metronome:        NE555 astable with RC timing

Both are 1980s-era hobbyist staples; both teach a different way of
turning two capacitors and a few resistors into a square wave.

Substitutions from the BP107 original:

- NE555N timer → `NE555` (wirebench catalogue class — the framework's
  black-box model of the part).  Behavioural simulation of the 555's
  comparator-and-flip-flop internals belongs in SPICE; wirebench
  validates the topology around it.
- 8 Ω 50 mm moving-coil speaker → `Speaker(8)`.  Any small low-Z
  speaker with an audio-band response works on the bench.
- VR1 100 kΩ panel pot → `Resistor(50_000)` at mid-rotation.  Same
  rheostat substitution `penfold_one_second_timer` uses for its
  threshold pot.
- R1 4.7 kΩ (RA), VR1 + R2 series chain → standard 555 astable
  timing network.  C1 = 100 nF for an audio-rate output (frequency
  ≈ 1.44 / ((R1 + 2 × R2) × C1)).  R3 = 100 Ω, C2 = 10 µF AC-couple
  the output to the speaker so the 555's DC offset doesn't push
  current through the coil.

Source: BP107 — 30 Solderless Breadboard Projects, Book 1
        R. A. Penfold
        Bernard Babani Publishing, October 1982
        ISBN 0 85934 082 1
        Pages 57–60 (text), Fig. 26 (schematic), Fig. 27 (layout).
"""
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent.parent / 'src'
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from pydantic import validate_call

from wirebench import (  # noqa: E402
    Analog,
    Circuit, wire,
    NE555,
    Capacitor, Rail, Resistor,
    Speaker,
    run_scenarios,
)


class Metronome(Circuit):
    """NE555 astable driving a small speaker through an AC coupling
    capacitor.  Tempo is set by R1 + VR1 + C1.

    The 555 is a black-box in wirebench's voltage-only graph — its
    astable behaviour can't be evaluated without timing.  This demo
    validates the topology around it; behavioural simulation
    requires SPICE.
    """

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self) -> None:
        # ── Rails ───────────────────────────────────────────────────
        # 9 V supply (PP6 in Penfold's original).  Analog twin rails
        # for the 555's VCC / GND (declared Analog at the pin level);
        # Digital twin rail for the RESET tie-off and any other logic-
        # level pin.  Same dual-rail pattern the `dice` and
        # `penfold_reaction_game` demos use.
        self.vcc   = Rail(True,  signal_type=Analog)
        self.gnd   = Rail(False, signal_type=Analog)
        self.vcc_d = Rail(True)

        # ── Active part ────────────────────────────────────────────
        self.u1 = NE555(refdes_number=1)

        # ── Timing network ─────────────────────────────────────────
        # 555 astable: t_high = 0.693 × (R1 + VR1) × C1,
        #              t_low  = 0.693 × VR1 × C1.
        # At R1 = 4.7 kΩ, VR1 ≈ 50 kΩ, C1 = 100 nF the period is
        # ≈ 7.3 ms → 137 Hz — comfortably in the audible band.
        self.r1  = Resistor(4_700,   refdes_number=1)    # R_A
        self.vr1 = Resistor(50_000,  refdes_number=2)    # 100 kΩ pot @ mid
        self.c1  = Capacitor(100e-9, refdes_number=1)    # timing cap

        # ── CTRL-pin filter ────────────────────────────────────────
        # 10 nF from pin 5 to GND — keeps the internal divider quiet.
        self.c2 = Capacitor(10e-9, refdes_number=2)

        # ── Output coupling + speaker ──────────────────────────────
        # R3 + C3 AC-couple the 555's output to the speaker.  R3
        # limits peak current; C3 blocks the DC offset.
        self.r3 = Resistor(100,    refdes_number=3)
        self.c3 = Capacitor(10e-6, refdes_number=3)      # AC coupler
        self.ls1 = Speaker(impedance_ohms=8, refdes_number=1)

        # ── Wiring ─────────────────────────────────────────────────

        # Supply pins.
        wire(self.vcc.out, self.u1.VCC)
        wire(self.gnd.out, self.u1.GND)

        # RESET pin tied HIGH (Digital) for free-running operation.
        wire(self.vcc_d.out, self.u1.RESET)

        # Timing network: R1 between VCC and the VR1/DISCH junction;
        # VR1 between that junction and the THRES/TRIG node; C1 from
        # THRES/TRIG to GND.  DISCH is the 555's open-collector
        # discharge pin (OUT direction), so the R1/VR1/DISCH net has
        # a real driver and needs no annotation.  THRES/TRIG are IN-
        # direction pins; the cap-top node only has two BIDIR-Analog
        # passives meeting them, so it needs `dynamically_driven=True`.
        wire(self.vcc.out, self.r1.t1)
        wire(self.r1.t2, self.vr1.t1, self.u1.DISCH)
        wire(self.vr1.t2, self.u1.THRES, self.u1.TRIG, self.c1.t1,
             dynamically_driven=True)
        wire(self.c1.t2, self.gnd.out)

        # CONT (pin 5) filter cap to GND.
        wire(self.u1.CONT, self.c2.t1)
        wire(self.c2.t2, self.gnd.out)

        # Output → R3 → C3 → speaker → GND.
        # Two intermediate BIDIR-Analog nodes along the R3-C3-Speaker
        # chain need `dynamically_driven=True`: the 555's OUT pin is
        # the actual source, but the static check sees passives
        # meeting at each junction with no declared driver.
        wire(self.u1.OUT, self.r3.t1)
        wire(self.r3.t2, self.c3.t1, dynamically_driven=True)
        wire(self.c3.t2, self.ls1.t1, dynamically_driven=True)
        wire(self.ls1.t2, self.gnd.out)

        super().__init__()

    def __call__(self) -> None:
        """No external signal interface — the metronome is self-
        running once power is applied.  The 555 is opaque under
        graph evaluation; bench behaviour is the actual circuit
        producing audible clicks at the dial-in tempo."""
        self.evaluate()
        return None

    def __repr__(self) -> str:
        return "Metronome()"


def _main() -> None:
    run_scenarios(
        Metronome(),
        scenarios=[
            ("power applied (NE555 opaque under graph eval)", ()),
        ],
        columns=[
            ("ls1.t1", lambda c, a, k: c.ls1.ports['t1'].value),
        ],
    )


if __name__ == '__main__':
    _main()
