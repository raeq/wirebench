"""Project 3 — Light-Activated Switch (after R. A. Penfold, BP107).

A classic dawn / dusk sensor.  A cadmium-sulphide LDR sits in one
arm of a voltage divider; a fixed resistor in the other arm.  The
divider's midpoint feeds the non-inverting input of an op-amp
comparator whose inverting input is held at a reference voltage by
a second divider (set with a potentiometer).  When the scene's light
level rises past the trip point, the divider midpoint crosses the
reference and the comparator output snaps HIGH; an NPN transistor
in common-emitter saturated-switch mode then drives an indicator
LED (or, in Penfold's original, a relay coil).

Substitutions from the BP107 original:

- ORP12 cadmium-sulphide LDR → `Photoresistor(dark_ohms, light_ohms)`
  with values bracketing the ORP12's quoted 1 MΩ-dark / 400 Ω-light
  range.  The catalogue class is generic; ORP12 is one of many
  specimens that hits these numbers.
- 741 op-amp → `LM741`.  Topology-identical for our purposes.
- BC108 NPN switching transistor → `BC547`.  BC108 is the metal-can
  TO-18 ancestor; BC547 is the modern TO-92 equivalent and is the
  part actually stocked at every hobby electronics counter.
- VR1 10 kΩ pot (threshold trimmer) → `Resistor(5_000)` at mid-
  rotation, two-terminal rheostat.  The exact trip point belongs to
  the bench calibration step; topology validation doesn't care
  where the wiper sits.
- Relay coil + flyback diode → indicator LED + current-limit
  resistor.  Penfold's relay drives mains-AC loads (which wirebench
  doesn't model at the parameter level); the LED keeps the topology
  honest at the wirebench-side simulation while staying a sensible
  hobby substitution.

Source: BP107 — 30 Solderless Breadboard Projects, Book 1
        R. A. Penfold
        Bernard Babani Publishing, October 1982
        ISBN 0 85934 082 1
        Pages 34–37 (text), Fig. 9 (schematic), Fig. 10 (layout).
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
    LM741, BC547,
    LED, Photoresistor, Rail, Resistor,
    run_scenarios,
)


class LightActivatedSwitch(Circuit):
    """LDR + comparator + transistor switch driving an indicator LED.

    External-port surface:
        lit              Digital OUT mirror of the LED's anode net,
                         exposed so a downstream consumer can read
                         the switch state without poking at internal
                         ports.  Same pattern as `hello_led`.

    The static analysis path doesn't model the LDR's light response.
    Demo scenarios drive the LDR's t1 node (the divider midpoint)
    directly to simulate dark / dusk / bright; the actual on-bench
    behaviour comes from the photo-effect changing the LDR's
    resistance and shifting the divider midpoint past the threshold.
    """

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self) -> None:
        # ── Rails ───────────────────────────────────────────────────
        # Single 9 V supply (Penfold's PP6 / B1).  All ports declared
        # Analog so the comparator wire-up doesn't cross the typing
        # boundary; the LED takes the Digital twin rail for its
        # cathode return.
        self.vcc   = Rail(True,  signal_type=Analog)
        self.gnd   = Rail(False, signal_type=Analog)
        self.gnd_d = Rail(False)

        # ── Op-amp comparator ──────────────────────────────────────
        self.u1 = LM741(refdes_number=1)

        # ── LDR divider (R1 + LDR) ─────────────────────────────────
        # R1 sits in the bottom arm against GND; LDR sits in the top
        # arm against VCC.  Midpoint feeds IN_POS.  As light falls,
        # LDR resistance rises and the midpoint drops; the comparator
        # flips when the midpoint crosses the reference.
        self.ldr = Photoresistor(
            dark_ohms=1_000_000, light_ohms=400,
            refdes_number=2,
        )
        self.r1  = Resistor(10_000, refdes_number=1)

        # ── Reference divider (R2 + VR1) on IN_NEG ─────────────────
        # R2 to VCC, VR1 (wiper-as-rheostat) to GND.  Wiper position
        # picks the trip light level.
        self.r2  = Resistor(10_000, refdes_number=3)
        self.vr1 = Resistor(5_000,  refdes_number=4)  # 10 kΩ pot @ mid

        # ── Transistor switch + LED indicator ──────────────────────
        # Q1 base via R3 takes the comparator output; collector pulls
        # LED + R4 + LED-anode chain low when the comparator is HIGH.
        # Emitter to GND.  Same shape as Penfold's "comparator HIGH
        # → switch ON → LED lit" relay drive.
        self.q1 = BC547(refdes_number=1)
        self.r3 = Resistor(4_700, refdes_number=5)    # base series R
        self.r4 = Resistor(470,   refdes_number=6)    # LED limit
        self.d1 = LED('red', refdes_number=1)

        # ── Wiring ─────────────────────────────────────────────────

        # Op-amp supply.
        wire(self.vcc.out, self.u1.V_POS)
        wire(self.gnd.out, self.u1.V_NEG)

        # LDR + R1 divider feeding IN_POS.
        # `dynamically_driven=True`: the midpoint is set by the
        # divider between the LDR (resistance varies with incident
        # light) and R1; the static check sees two BIDIR-Analog
        # passives meeting at a node with no driver, but the LDR
        # itself is the upstream source in the physical circuit.
        wire(self.vcc.out, self.ldr.t1)
        wire(self.ldr.t2, self.r1.t1, self.u1.IN_POS,
             dynamically_driven=True)
        wire(self.r1.t2, self.gnd.out)

        # Reference divider on IN_NEG.
        # `dynamically_driven=True`: same shape as IN_POS — the
        # divider midpoint between R2 and VR1 is driven by the rails
        # through two passives.
        wire(self.vcc.out, self.r2.t1)
        wire(self.r2.t2,  self.vr1.t1, self.u1.IN_NEG,
             dynamically_driven=True)
        wire(self.vr1.t2, self.gnd.out)

        # Comparator output → base resistor → BJT base.
        # `dynamically_driven=True`: the BJT's base sits between the
        # R3 series resistor and the transistor's input; the static
        # check sees a BIDIR-Analog passive (R3) meeting a BIDIR-Analog
        # transistor terminal at a node with no declared driver, but
        # the comparator output upstream drives the node through R3.
        wire(self.u1.OUT, self.r3.t1)
        wire(self.r3.t2, self.q1.b, dynamically_driven=True)

        # LED branch from VCC: VCC → R4 → LED anode → LED cathode →
        # collector → emitter → GND.  When the comparator is HIGH,
        # Q1 saturates, the collector pulls down toward emitter
        # (≈ GND), the LED forward-biases through R4, and the LED
        # lights.
        wire(self.vcc.out, self.r4.t1)
        wire(self.r4.t2, self.d1.anode)
        # LED's cathode goes to Q1's collector.  LED.cathode is
        # Direction.IN, so this is a real driver-to-IN wire; no
        # `dynamically_driven` annotation needed.
        wire(self.d1.cathode, self.q1.c)
        wire(self.q1.e, self.gnd_d.out)

        super().__init__(
            ports={'lit': self.d1.anode},
        )

    @property
    def lit(self) -> bool | None:
        return self.d1.lit

    def __call__(self) -> bool | None:
        """No external signal interface — the design is autonomous
        once power is applied.  Evaluating the design propagates the
        Rail drives through the divider, comparator, and transistor;
        the LED's `lit` reflects the result.

        Under the framework's voltage-only graph the LDR is opaque,
        so this returns `None` (undriven) by default — a real bench
        build instead has the LDR's resistance set by ambient light,
        which the simulator can't model.
        """
        self.evaluate()
        return self.lit

    def __repr__(self) -> str:
        return f"LightActivatedSwitch(lit={self.lit!r})"


def _main() -> None:
    run_scenarios(
        LightActivatedSwitch(),
        scenarios=[
            ("power applied (LDR opaque under graph eval)", ()),
        ],
        columns=[
            ("d1", lambda c, a, k:
             'on' if c.d1.lit else 'off' if c.d1.lit is False else '?'),
        ],
    )


if __name__ == '__main__':
    _main()
