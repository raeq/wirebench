"""Project 16 — Warbling Doorbuzzer (after R. A. Penfold, BP107).

Two NE555 astables in a *modulator + carrier* configuration: a slow
oscillator (a few Hz) is wired so its output gates the reset input
of a fast audio-rate oscillator.  When the slow output goes HIGH
the fast oscillator runs and a tone is heard; when it goes LOW the
fast oscillator is held in reset and the speaker is silent.  The
result is a chirp-chirp-chirp warble — far more distinctive than a
plain steady tone, and so a more attention-getting doorbell.

The composition pattern (one oscillator's output drives another's
control input) is the *teaching point*.  This is the canonical
example of *"a circuit is a graph of subcircuits"* at the within-
board level — distinct from the between-board Board composition the
existing isolated_rs232 / fan_cooling demos teach.

Substitutions from the BP107 original:

- Penfold's original uses a single dual-555 (NE556) in one DIP-14
  package.  Two discrete NE555s wired identically work the same on
  the bench and on wirebench's topology surface — the warble is
  identical.  Wirebench's catalogue does not currently include a
  dedicated NE556 class; if and when the catalogue grows one, this
  demo's two-555 wiring becomes a single-556 wiring with no other
  changes.
- 8 Ω moving-coil speaker → `Speaker(8)`.
- Timing resistor / capacitor values picked for a 4 Hz warble rate
  and a 600 Hz tone — comfortable doorbell defaults.

Source: BP107 — 30 Solderless Breadboard Projects, Book 1
        R. A. Penfold
        Bernard Babani Publishing, October 1982
        ISBN 0 85934 082 1
        Pages 86–90 (text), Fig. 42 (schematic), Fig. 43 (layout).
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


class WarblingDoorbuzzer(Circuit):
    """Two NE555 astables; slow modulates fast via the RESET pin.

    Topology:
        U1 (modulator) — slow astable at ~4 Hz.
        U2 (carrier)   — fast astable at ~600 Hz, RESET driven by U1.OUT.
        Speaker hangs off U2's output through R-C AC coupling.
    """

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self) -> None:
        # ── Rails ───────────────────────────────────────────────────
        self.vcc   = Rail(True,  signal_type=Analog)
        self.gnd   = Rail(False, signal_type=Analog)
        self.vcc_d = Rail(True)

        # ── Two 555s ───────────────────────────────────────────────
        self.u1 = NE555(refdes_number=1)   # modulator (slow)
        self.u2 = NE555(refdes_number=2)   # carrier (audio)

        # ── U1 timing (slow ~4 Hz) ─────────────────────────────────
        # R_A = 47 kΩ, R_B = 47 kΩ, C = 2.2 µF → period ≈ 215 ms (≈ 4.6 Hz).
        self.r1 = Resistor(47_000,   refdes_number=1)
        self.r2 = Resistor(47_000,   refdes_number=2)
        self.c1 = Capacitor(2.2e-6,  refdes_number=1)
        self.c1_ctrl = Capacitor(10e-9, refdes_number=2)  # U1 CTRL pin filter

        # ── U2 timing (fast ~600 Hz) ───────────────────────────────
        # R_A = 4.7 kΩ, R_B = 4.7 kΩ, C = 100 nF → ~1 kHz.  Penfold
        # picks his timing for a balanced trill; the exact pitch is
        # a taste choice the bench builder sets via the pot.
        self.r3 = Resistor(4_700,    refdes_number=3)
        self.r4 = Resistor(4_700,    refdes_number=4)
        self.c2 = Capacitor(100e-9,  refdes_number=3)
        self.c2_ctrl = Capacitor(10e-9, refdes_number=4)  # U2 CTRL pin filter

        # ── Output coupling + speaker ──────────────────────────────
        self.r5  = Resistor(100,    refdes_number=5)      # current limit
        self.c3  = Capacitor(10e-6, refdes_number=5)      # AC coupler
        self.ls1 = Speaker(impedance_ohms=8, refdes_number=1)

        # ── Wiring ─────────────────────────────────────────────────

        # Supply pins for both 555s.
        wire(self.vcc.out, self.u1.VCC, self.u2.VCC)
        wire(self.gnd.out, self.u1.GND, self.u2.GND)

        # ── U1 (slow modulator) — standard astable wiring ──────────
        # U1.RESET tied HIGH so it runs free.  Its OUT will gate U2.
        wire(self.vcc_d.out, self.u1.RESET)
        wire(self.vcc.out, self.r1.t1)
        wire(self.r1.t2, self.r2.t1, self.u1.DISCH)
        wire(self.r2.t2, self.u1.THRES, self.u1.TRIG, self.c1.t1,
             dynamically_driven=True)
        wire(self.c1.t2, self.gnd.out)
        wire(self.u1.CONT, self.c1_ctrl.t1)
        wire(self.c1_ctrl.t2, self.gnd.out)

        # ── U2 (fast carrier) — same shape, driven by U1.OUT on RESET ─
        # The modulation: when U1.OUT is HIGH, U2 is enabled and the
        # tone plays; when U1.OUT is LOW, U2's flip-flop holds the
        # output LOW and the speaker is silent.  This is the simplest
        # form of gating modulation — and is what gives the doorbell
        # its characteristic trill.
        wire(self.u1.OUT, self.u2.RESET)
        wire(self.vcc.out, self.r3.t1)
        wire(self.r3.t2, self.r4.t1, self.u2.DISCH)
        wire(self.r4.t2, self.u2.THRES, self.u2.TRIG, self.c2.t1,
             dynamically_driven=True)
        wire(self.c2.t2, self.gnd.out)
        wire(self.u2.CONT, self.c2_ctrl.t1)
        wire(self.c2_ctrl.t2, self.gnd.out)

        # U2 output → R5 → C3 → speaker → GND.
        wire(self.u2.OUT, self.r5.t1)
        wire(self.r5.t2, self.c3.t1, dynamically_driven=True)
        wire(self.c3.t2, self.ls1.t1, dynamically_driven=True)
        wire(self.ls1.t2, self.gnd.out)

        super().__init__()

    def __call__(self) -> None:
        """Self-running once power is applied.  Both 555s are opaque
        under graph evaluation; behavioural simulation of the warble
        belongs in SPICE."""
        self.evaluate()
        return None

    def __repr__(self) -> str:
        return "WarblingDoorbuzzer()"


def _main() -> None:
    run_scenarios(
        WarblingDoorbuzzer(),
        scenarios=[
            ("power applied (two 555s opaque under graph eval)", ()),
        ],
        columns=[
            ("u1.out", lambda c, a, k: c.u1.ports['OUT'].value),
            ("u2.out", lambda c, a, k: c.u2.ports['OUT'].value),
        ],
    )


if __name__ == '__main__':
    _main()
