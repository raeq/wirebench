"""Project 27 — Crystal Set (after R. A. Penfold, BP107).

A crystal radio: the iconic *no-battery* receiver of the 1920s and
the entry-level set of every radio-club beginner since.  The
ferrite-rod aerial (L1) intercepts the local medium-wave EM field;
the variable capacitor (VC1) tunes the LC tank to resonate at the
chosen station's carrier frequency; the germanium diode (D1)
rectifies the modulated RF into the audio envelope; the high-
impedance crystal earpiece (EARP1) transduces that audio directly
to sound.

There is **no Rail** in the design.  The whole receiver runs on
the tens of microwatts of RF energy the antenna collects from the
environment, returned through the earth connection.  In wirebench
terms this is *the* boundary-case probe: can a Circuit be expressed
without any declared power supply?

Substitutions from the BP107 original:

- Denco MW5FR ferrite aerial coil → `FerriteAerial(henries=400e-6)`.
  400 µH is a typical value for a hand-wound coil on a 10 mm × 50 mm
  ferrite rod.
- Jackson Dielecon 300 pF solid-dielectric tuning capacitor →
  `VariableCapacitor(min_farads=10e-12, max_farads=300e-12)`.
  Sweeping the rotor across its range tunes the LC tank's resonant
  frequency from approximately 500 kHz (plates fully meshed) to
  2.5 MHz (plates fully open) — covering the broadcast MW band.
- OA90 germanium signal diode → `D_OA90`.  Vf ≈ 0.2 V is the
  *whole* reason for picking germanium over silicon — see the
  D_OA90 docstring for the discussion.
- 100 kΩ DC bias / load resistor → `Resistor(100_000)`.
- High-impedance crystal earpiece → `CrystalEarpiece()`.
- Antenna (long-wire) + earth connection → `Antenna()` + `Earth()`,
  the new wirebench classes that make the *environment-fed* topology
  expressible without using a declared Rail.

Source: BP107 — 30 Solderless Breadboard Projects, Book 1
        R. A. Penfold
        Bernard Babani Publishing, October 1982
        ISBN 0 85934 082 1
        Pages 131–134 (text), Fig. 62 (schematic), Fig. 63 (layout).
"""
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent.parent / 'src'
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from pydantic import validate_call

from wirebench import (  # noqa: E402
    Circuit, wire,
    D_OA90,
    Resistor,
    FerriteAerial, VariableCapacitor,
    Antenna, CrystalEarpiece, Earth,
    run_scenarios,
)


class CrystalSet(Circuit):
    """A four-component MW crystal radio: aerial, tuned tank, detector
    diode, earpiece.  No declared Rail — the whole receiver runs on
    the tens of microwatts the antenna captures.

    This demo is the *passive-only-with-environment-source* topology
    probe for the framework.  If it constructs cleanly, wirebench's
    expression surface is rich enough to model the most distinctive
    1920s circuit on the hobbyist canon; the test asserts zero
    `Rail` instances exist in the design as the formal expression
    of that claim.
    """

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self) -> None:
        # ── Environment connections ───────────────────────────────
        # `Antenna` and `Earth` are the wirebench-side expression
        # of the antenna-to-EM-field and earth-to-soil contacts.
        # Both are environment-fed; neither is a `Rail`.  Each lives
        # in its own refdes number-space ('A' for the antenna, 'E'
        # for the earth-ground terminal).
        self.ant   = Antenna(refdes_number=1)
        self.earth = Earth(refdes_number=1)

        # ── Tuned LC tank ─────────────────────────────────────────
        # L1 (ferrite aerial coil) in parallel with VC1 (tuning cap)
        # forms the band-pass network that selects which station the
        # receiver hears.  L1 doubles as the antenna pick-up itself.
        self.l1  = FerriteAerial(henries=400e-6, refdes_number=1)
        self.vc1 = VariableCapacitor(
            min_farads=10e-12, max_farads=300e-12,
            refdes_number=1,
        )

        # ── Detector + load ───────────────────────────────────────
        # D1's anode sees the modulated RF; cathode passes the
        # rectified envelope to the high-Z earpiece + DC-bias load.
        self.d1 = D_OA90(refdes_number=1)
        self.r1 = Resistor(100_000, refdes_number=1)

        # ── Audio transducer ──────────────────────────────────────
        # CrystalEarpiece is the high-impedance piezo transducer —
        # the only way to make microwatts of detected audio audible.
        self.earp1 = CrystalEarpiece(refdes_number=1)

        # ── Wiring ────────────────────────────────────────────────
        # The aerial taps into one side of the tank; the earth
        # references the other.  In Penfold's original layout the
        # earth side is also where the detector's load resistor
        # returns to and where the earpiece's negative terminal sits.

        # Tank: L1 ∥ VC1 between the antenna-fed node and the
        # earth-referenced node.
        wire(self.ant.ports['out'], self.l1.t1, self.vc1.t1, self.d1.anode)
        wire(self.l1.t2, self.vc1.t2, self.earth.ports['out'])

        # Detector load: D1 cathode → R1 → earth; the same node
        # drives the earpiece's hot side.
        # `dynamically_driven=True`: the diode's cathode is the
        # detected-audio output node; in the real circuit the
        # rectified RF envelope drives it.  The static check sees
        # only BIDIR passives meeting here and can't follow the
        # rectification through D1, so annotate.
        wire(self.d1.cathode, self.r1.t1, self.earp1.t1,
             dynamically_driven=True)
        wire(self.r1.t2, self.earp1.t2, self.earth.ports['out'])

        super().__init__()

    def __call__(self) -> None:
        """Self-running once antenna and earth are connected.  The
        whole receiver is passive; static graph evaluation can't
        propagate RF energy across an LC tank, but topology
        validation confirms the wire-up is correct.  Behavioural
        simulation belongs in a SPICE run with an AC source on the
        antenna terminal."""
        self.evaluate()
        return None

    def __repr__(self) -> str:
        return "CrystalSet()"


def _main() -> None:
    run_scenarios(
        CrystalSet(),
        scenarios=[
            ("antenna + earth connected, tuned to a MW station", ()),
        ],
        columns=[
            ("aerial.out",  lambda c, a, k: c.ant.ports['out'].value),
            ("audio.t1",    lambda c, a, k: c.earp1.ports['t1'].value),
            ("earth.out",   lambda c, a, k: c.earth.ports['out'].value),
        ],
    )


if __name__ == '__main__':
    _main()
