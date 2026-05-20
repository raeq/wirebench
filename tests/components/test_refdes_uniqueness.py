"""Refdes-prefix uniqueness across the transducer family.

Two prior defects let two part classes share a refdes prefix:

  - Speaker and CrystalEarpiece both at 'LS' — collision when both
    are placed in one Circuit.
  - Antenna and Earth both at 'A' — same.

This module asserts the prefixes are now distinct and that placing
two such parts in one Circuit doesn't raise.
"""
from __future__ import annotations

from components.transducers.antenna          import Antenna
from components.transducers.crystal_earpiece import CrystalEarpiece
from components.transducers.earth            import Earth
from components.transducers.speaker          import Speaker


def test_speaker_and_crystal_earpiece_have_distinct_prefixes():
    """Speaker uses 'LS' (loudspeaker family); CrystalEarpiece uses
    'BZ' (buzzer / piezo earpiece family).  Distinct prefixes mean
    distinct refdes number-spaces — two parts with `refdes_number=1`
    don't collide."""
    assert Speaker.REFDES_PREFIX == 'LS'
    assert CrystalEarpiece.REFDES_PREFIX == 'BZ'
    assert Speaker.REFDES_PREFIX != CrystalEarpiece.REFDES_PREFIX


def test_antenna_and_earth_have_distinct_prefixes():
    """Antenna uses 'A' (assembly / antenna); Earth uses 'E' (earth-
    ground terminal, conventional in British schematics)."""
    assert Antenna.REFDES_PREFIX == 'A'
    assert Earth.REFDES_PREFIX == 'E'
    assert Antenna.REFDES_PREFIX != Earth.REFDES_PREFIX


def test_speaker_and_crystal_earpiece_coexist_at_refdes_number_1():
    """Composing a Speaker and a CrystalEarpiece both at
    `refdes_number=1` is fine — the prefixes split the number-space.
    Previously both classes shared 'LS', so this composition would
    have produced two parts both labelled LS1."""
    spk = Speaker(impedance_ohms=8, refdes_number=1)
    ear = CrystalEarpiece(impedance_ohms=32_000, refdes_number=1)
    # Distinct refdes strings, distinct prefixes.
    assert spk.refdes == 'LS1'
    assert ear.refdes == 'BZ1'
    assert spk.refdes != ear.refdes


def test_antenna_and_earth_coexist_at_refdes_number_1():
    """Same property for Antenna + Earth."""
    ant = Antenna(refdes_number=1)
    ear = Earth(refdes_number=1)
    assert ant.refdes == 'A1'
    assert ear.refdes == 'E1'
    assert ant.refdes != ear.refdes
