"""Targeted topology test for the Penfold crystal-set demo.

The teaching point is *passive-only topology with environment-fed
energy*.  The canonical assertion: **zero Rail instances exist in
the circuit.**  If wirebench's framework forced a Rail for the
design to construct, this test would fail and the failure itself
would document the gap — but it doesn't, because the new `Antenna`
and `Earth` classes give the topology a Rail-free expression.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest

_DEMO_DIR = Path(__file__).resolve().parent.parent.parent / 'demos' / 'penfold_crystal_set'
if str(_DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(_DEMO_DIR))


@pytest.fixture
def crystal():
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        from penfold_crystal_set import CrystalSet
        return CrystalSet()


def test_zero_rails(crystal):
    """The crystal set's defining property: no declared power supply.

    `Rail` is wirebench's marker for a bench-supplied Vcc / GND tie;
    a passive-only design (powered entirely by what the Antenna
    captures from the environment) must contain zero Rail instances.

    If this assertion ever fires it means either:
      - the demo was edited to add a power supply (not faithful to
        the topology) — fix the demo, *or*
      - the framework changed in a way that forces a Rail into the
        design (e.g. a constructor invariant now requires at least
        one power-rail driver) — file a finding the way Phase 2.7
        captured `dynamically_driven`.
    """
    from components.passives.rail import Rail
    rails = [fn for fn in crystal.parts if isinstance(fn, Rail)]
    assert rails == [], (
        f"Expected zero Rail instances; found {len(rails)}: {rails!r}.  "
        f"This is the canonical *passive-only* test — if the topology "
        f"now requires a Rail, the framework's expression surface has "
        f"narrowed and the demo's teaching point is broken."
    )


def test_antenna_and_earth_present(crystal):
    """Without `Antenna` and `Earth` there would be no environment-
    fed signal source and return path, and the LC tank would
    construct floating."""
    from components.transducers.antenna import Antenna
    from components.transducers.earth import Earth
    antennas = [fn for fn in crystal.parts if isinstance(fn, Antenna)]
    earths   = [fn for fn in crystal.parts if isinstance(fn, Earth)]
    assert len(antennas) == 1
    assert len(earths)   == 1


def test_lc_tank_present(crystal):
    """L1 (ferrite aerial) + C1 (variable cap) — the tuned tank."""
    from components.passives.ferrite_aerial import FerriteAerial
    from components.passives.variable_capacitor import VariableCapacitor
    inductors = [fn for fn in crystal.parts if isinstance(fn, FerriteAerial)]
    var_caps  = [fn for fn in crystal.parts if isinstance(fn, VariableCapacitor)]
    assert len(inductors) == 1
    assert len(var_caps)  == 1


def test_germanium_diode_present(crystal):
    """The detector is specifically germanium (V_F ≈ 0.2 V) — a
    silicon 1N4148 substitution wouldn't conduct on a microvolt
    antenna signal."""
    from components.diodes.oa90 import D_OA90
    germ = [fn for fn in crystal.parts if isinstance(fn, D_OA90)]
    assert len(germ) == 1


def test_crystal_earpiece_present(crystal):
    """High-impedance piezo earpiece — a moving-coil speaker is the
    wrong impedance for a microwatt-budget receiver."""
    from components.transducers.crystal_earpiece import CrystalEarpiece
    earpieces = [fn for fn in crystal.parts if isinstance(fn, CrystalEarpiece)]
    assert len(earpieces) == 1
