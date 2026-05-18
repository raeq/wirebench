"""Project 8 — One-Second Timer (after R. A. Penfold, BP107).

A relaxation oscillator built around a single op-amp configured as a
comparator with hysteresis.  The non-inverting input sits at a divider-
defined midpoint shifted by R3+VR1 (positive feedback for hysteresis);
the inverting input charges and discharges a capacitor through an
asymmetric RC network (R4∥D1 in series with R5, where D1 bypasses R4
during the discharge half-cycle).  The output oscillates at roughly
1 Hz and a brief LED flash on D2 marks each second.

This is wirebench's translation of Penfold's BP107 Project 8 — built as
a proof of capability that vintage hobbyist designs ingest cleanly into
the framework's construction-time validation.

Substitutions from the BP107 original:

- TL081CP single JFET-input op-amp → LM741 (single bipolar-input
  op-amp; same comparator-with-hysteresis topology; bias currents
  differ but topology is preserved).
- TIL209 red 5 mm LED → LED('red').
- VR1 100 kΩ linear carbon pot → Resistor(50_000) at mid-rotation.
  VR1 in this design is wired as a two-terminal rheostat (one fixed
  end + wiper); 50 kΩ is the mid-rotation value.  The exact frequency
  depends on calibration and is irrelevant for topology validation.
- S1 (SPST toggle) + B1 (9 V PP6) → Rail pair.  Real build would
  interpose S1 between B1 + and the VCC rail; the framework's
  topology check doesn't need the supply chain to validate the
  oscillator.
- R6 1 kΩ (single current-limit resistor in series with D2) →
  R6 510 Ω + R7 510 Ω, one on each side of D2.  wirebench's strict
  signal-typing requires a BIDIR-Analog conductor wildcard on each
  wire that crosses the Analog↔Digital boundary; a single resistor
  covers one of D2's two pins but not both.  Splitting R6 into a
  symmetric pair gives both pins their own wildcard.  Total current
  limit ≈ 1.02 kΩ, equivalent to Penfold's R6 within E12 tolerance.

Source: BP107 — 30 Solderless Breadboard Projects, Book 1
        R. A. Penfold
        Bernard Babani Publishing, October 1982
        ISBN 0 85934 082 1
        Pages 53–56 (text), Fig. 24 (schematic), Fig. 25 (layout).
"""
from __future__ import annotations

import sys
from pathlib import Path

# Path setup so this file runs standalone from anywhere in the repo.
_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / 'src'))

from wirebench import (  # noqa: E402  — sys.path tweak must precede import
    Analog,
    Circuit, wire,
    LED, Rail, Resistor, Capacitor,
    LM741,
    D1N4148,
    print_bom, run_scenarios,
)


class OneSecondTimer(Circuit):
    """Op-amp relaxation oscillator, ~1 Hz, brief LED flash per cycle."""

    def __init__(self) -> None:
        # ── Power rails ──────────────────────────────────────────────
        # 9 V from B1 (PP6) via S1 (SPST) in the original design.
        # The framework cares about the rail's drive, not the source.
        self.vcc = Rail(True,  signal_type=Analog)
        self.gnd = Rail(False, signal_type=Analog)

        # ── Op-amp comparator (IC1) ──────────────────────────────────
        # Penfold uses TL081CP; LM741 is the catalogue-available
        # bipolar-input equivalent with the same topology role.
        self.u1 = LM741(refdes_number=1)

        # ── Non-inverting input divider chain (R1, R2, R3, VR1) ──────
        # R1+R2 bias IN_POS to half-supply.  R3+VR1 form the
        # positive-feedback path from OUT back to IN_POS that gives
        # the hysteresis (shifting the comparator threshold by ±β·Vcc).
        self.r1  = Resistor(100_000,  refdes_number=1)  # 100 kΩ
        self.r2  = Resistor(100_000,  refdes_number=2)  # 100 kΩ
        self.r3  = Resistor(4_700,    refdes_number=3)  # 4.7 kΩ
        self.vr1 = Resistor(50_000,   refdes_number=4)  # 100 kΩ pot @ mid

        # ── Timing network (C2, R4, R5, D1) on the inverting input ───
        # C2 charges and discharges asymmetrically:
        #   charge half-cycle  → through R5 in series with R4 (slow)
        #   discharge half-cycle → D1 bypasses R4 (fast)
        # D1 anode at IN_NEG side, cathode at the R5/R4 junction.
        self.r4  = Resistor(10_000_000, refdes_number=5)  # 10 MΩ
        self.r5  = Resistor(220_000,    refdes_number=6)  # 220 kΩ
        self.c2  = Capacitor(100e-9,    refdes_number=2)  # 100 nF
        self.d1  = D1N4148(refdes_number=1)                # 1N4148

        # ── Supply decoupling ────────────────────────────────────────
        self.c1  = Capacitor(100e-6, refdes_number=1)  # 100 µF

        # ── Output indicator (R6, R7, D2) ────────────────────────────
        # Penfold's "briefly flashes" comes from output being HIGH
        # for most of the cycle.  When output drops LOW briefly, the
        # LED forward-biases:  VCC → R6 → D2 → R7 → OUT.
        # R6 + R7 split Penfold's single 1 kΩ — see module docstring.
        self.r6  = Resistor(510, refdes_number=7)  # VCC-side bridge
        self.r7  = Resistor(510, refdes_number=8)  # OUT-side bridge
        self.d2  = LED('red',     refdes_number=2) # TIL209-equivalent

        # ── Wiring ───────────────────────────────────────────────────

        # Op-amp supply pins (POWER + GROUND).
        wire(self.vcc.out, self.u1.V_POS)
        wire(self.gnd.out, self.u1.V_NEG)

        # Supply decoupling cap directly across the rails.
        wire(self.vcc.out, self.c1.t1)
        wire(self.gnd.out, self.c1.t2)

        # Non-inverting input net: R1 from VCC, R2 to GND, R3 toward
        # the VR1 chain back to the output.  All four meet at IN_POS.
        wire(self.vcc.out, self.r1.t1)
        wire(self.r1.t2,   self.u1.IN_POS, self.r2.t1, self.r3.t1)
        wire(self.r2.t2,   self.gnd.out)

        # Hysteresis return path: R3 → VR1 → output.
        wire(self.r3.t2,   self.vr1.t1)
        wire(self.vr1.t2,  self.u1.OUT)

        # Timing network on the inverting input.
        # IN_NEG sits between C2-to-GND, R4∥D1, and the rest of the
        # feedback chain reaching OUT through R5.
        wire(self.u1.IN_NEG, self.c2.t1, self.r4.t2, self.d1.anode)
        wire(self.gnd.out,   self.c2.t2)

        # R4 in parallel with D1 (D1 cathode at the OUT-side junction).
        wire(self.r4.t1,     self.d1.cathode, self.r5.t2)

        # R5 closes the feedback to the op-amp's own output node.
        wire(self.r5.t1,     self.u1.OUT)

        # Output indicator chain: VCC → R6 → D2 → R7 → OUT.
        # Two resistors split Penfold's single R6 = 1 kΩ to give wirebench's
        # strict signal-typing a BIDIR-Analog wildcard on each Analog↔Digital
        # wire (LED ports are Digital, VCC and OUT are Analog).
        wire(self.vcc.out,    self.r6.t1)
        wire(self.r6.t2,      self.d2.anode)
        wire(self.d2.cathode, self.r7.t1)
        wire(self.r7.t2,      self.u1.OUT)

        super().__init__()


def _main() -> None:
    """Construct the design and print its BOM."""
    design = OneSecondTimer()
    print_bom(design)
    run_scenarios(
        design,
        scenarios=[('power applied', ())],
        columns=[],
    )


if __name__ == '__main__':
    _main()
