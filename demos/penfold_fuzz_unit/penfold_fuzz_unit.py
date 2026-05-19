"""Project 30 — Fuzz Unit (after R. A. Penfold, BP107).

A guitar-effects *fuzz* pedal: a high-gain inverting op-amp stage
amplifies the guitar's input signal past the supply rails, where a
pair of back-to-back clipping diodes from the output to ground fold
the peaks into a square-wave-with-rounded-edges waveform.  The
clipping produces the characteristic *fuzz* / *distortion* timbre
that defined an entire era of rock guitar.

Topology:
    input jack → C1 (input cap) → R1 (input pull-down)
                              ↓
           IN_POS / IN_NEG of LM741 in inverting config
                              ↓
         OUT → R3 / R2 feedback divider (gain ≈ R3/R2 ≈ 470x)
                              ↓
       Clipping diodes D1/D2 anti-parallel to ground
                              ↓
              C2 (output cap) → VR1 (volume pot)
                              ↓
                     output jack tip

Substitutions from the BP107 original:

- Penfold's design uses two BC108 NPN transistors in a discrete
  two-stage amplifier.  This wirebench translation uses an LM741
  op-amp for the high-gain stage — same clipping behaviour, far
  simpler to express topologically.  The discrete two-BJT version
  is the equally-valid textbook variant; both produce the same
  square-wave-with-rounded-edges fuzz waveform.
- 1N914 silicon clipping diodes → `D1N4148` (same DO-35 part class).
- 1/4" mono input/output jacks → `Audio3p5mmTRSJack` ×2 in TS-only
  configuration (the tip is the signal, the sleeve is GND; the ring
  contact is left unconnected).  Hobby fuzz boxes use 1/4" but the
  framework's audio jack catalogue is 3.5 mm only; the topology is
  identical.
- VR1 100 kΩ volume pot → `Resistor(50_000)` at mid-rotation.

Source: BP107 — 30 Solderless Breadboard Projects, Book 1
        R. A. Penfold
        Bernard Babani Publishing, October 1982
        ISBN 0 85934 082 1
        Pages 145–end (text), Fig. 71 (schematic), Fig. 72 (layout).
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
    LM741, D1N4148,
    Capacitor, Rail, Resistor,
    run_scenarios,
)
from components.connectors.audio import Audio3p5mmTRSJack  # noqa: E402


class FuzzUnit(Circuit):
    """High-gain inverting op-amp + clipping-diode pair = fuzz.

    External-port surface (via the two audio jacks):
        input_tip / output_tip — signal pins exposed for downstream
        consumers that want to scope the design directly.

    The op-amp's high gain and the clipping diodes' Vf saturate the
    output around ±0.7 V.  In wirebench's voltage-only graph the
    saturation is approximated by the op-amp cell's rail-to-rail
    behaviour — close enough for topology validation; SPICE handles
    the audio-band frequency response.
    """

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self) -> None:
        # ── Rails ───────────────────────────────────────────────────
        # 9 V supply (standard guitar-pedal voltage — Penfold's PP6).
        self.vcc = Rail(True,  signal_type=Analog)
        self.gnd = Rail(False, signal_type=Analog)

        # ── Active part ────────────────────────────────────────────
        self.u1 = LM741(refdes_number=1)

        # ── Input and output jacks ─────────────────────────────────
        # TRS connectors in TS configuration: tip carries the audio
        # signal, sleeve returns to GND, ring is unused.
        self.input_jack  = Audio3p5mmTRSJack(refdes_number=1)
        self.output_jack = Audio3p5mmTRSJack(refdes_number=2)

        # ── Input coupling + bias ──────────────────────────────────
        self.c1 = Capacitor(100e-9, refdes_number=1)   # input AC cap
        self.r1 = Resistor(1_000_000, refdes_number=1) # input bias

        # ── Inverting amplifier ────────────────────────────────────
        # R2 = 1 kΩ input series; R3 = 470 kΩ feedback → gain ≈ 470x
        # so a 10 mV guitar pickup signal saturates well past the
        # ±0.7 V clipping range.
        self.r2 = Resistor(1_000,   refdes_number=2)
        self.r3 = Resistor(470_000, refdes_number=3)

        # ── Mid-rail bias divider ──────────────────────────────────
        # The op-amp's non-inverting input sits at VCC/2 so the
        # output can swing both ways from a single-supply rail.
        self.r4 = Resistor(100_000, refdes_number=4)
        self.r5 = Resistor(100_000, refdes_number=5)
        self.c2 = Capacitor(10e-6,  refdes_number=2)   # bias bypass

        # ── Clipping diode pair ────────────────────────────────────
        # Back-to-back: anode of D1 at OUT, cathode of D1 at GND;
        # anode of D2 at GND, cathode of D2 at OUT.  Together they
        # clamp the op-amp output to ±0.7 V.
        self.d1 = D1N4148(refdes_number=1)
        self.d2 = D1N4148(refdes_number=2)

        # ── Output coupling + volume pot ───────────────────────────
        self.c3  = Capacitor(220e-9, refdes_number=3)  # output AC cap
        self.vr1 = Resistor(50_000,  refdes_number=6)  # 100 kΩ pot @ mid

        # ── Wiring ─────────────────────────────────────────────────

        # Op-amp supply.
        wire(self.vcc.out, self.u1.V_POS)
        wire(self.gnd.out, self.u1.V_NEG)

        # Input jack: tip → C1 → R2 → IN_NEG.  Sleeve → GND.  Ring left
        # unconnected (mono).  R1 from tip-cap junction to GND biases
        # the input toward ground when no plug is inserted.
        wire(self.input_jack.ports['tip'], self.c1.t1)
        wire(self.c1.t2, self.r1.t1, self.r2.t1,
             dynamically_driven=True)
        wire(self.r1.t2, self.gnd.out)
        wire(self.r2.t2, self.u1.IN_NEG, self.r3.t1,
             dynamically_driven=True)
        wire(self.input_jack.ports['sleeve'], self.gnd.out)

        # IN_POS held at mid-rail by R4/R5 with C2 as bypass.
        wire(self.vcc.out, self.r4.t1)
        wire(self.r4.t2, self.r5.t1, self.u1.IN_POS, self.c2.t1,
             dynamically_driven=True)
        wire(self.r5.t2, self.gnd.out)
        wire(self.c2.t2, self.gnd.out)

        # Feedback: OUT → R3 → IN_NEG (already wired via R3.t2 above).
        wire(self.u1.OUT, self.r3.t2)

        # Clipping diode pair anti-parallel between OUT and GND.
        # `dynamically_driven=True`: the GND-side junction has two
        # passive BIDIRs (the two diode anode/cathode meeting GND);
        # in the actual circuit the diodes only conduct when the
        # op-amp pushes the OUT node past ±Vf.  Static check sees
        # no driver — annotate.
        wire(self.u1.OUT, self.d1.anode, self.d2.cathode)
        wire(self.d1.cathode, self.d2.anode, self.gnd.out)

        # Output coupling + volume + output jack tip.
        wire(self.u1.OUT, self.c3.t1)
        wire(self.c3.t2, self.vr1.t1, dynamically_driven=True)
        wire(self.vr1.t2, self.output_jack.ports['tip'],
             dynamically_driven=True)
        wire(self.output_jack.ports['sleeve'], self.gnd.out)

        super().__init__()

    def __call__(self) -> None:
        """Self-running once power is applied.  The op-amp + clipping
        diode topology can't be evaluated quantitatively under
        wirebench's voltage-only graph; the bench result is audible
        fuzz when a guitar is plugged in."""
        self.evaluate()
        return None

    def __repr__(self) -> str:
        return "FuzzUnit()"


def _main() -> None:
    run_scenarios(
        FuzzUnit(),
        scenarios=[
            ("power applied (no guitar plugged in)", ()),
        ],
        columns=[
            ("out.tip", lambda c, a, k:
             c.output_jack.ports['tip'].value),
        ],
    )


if __name__ == '__main__':
    _main()
