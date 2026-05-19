"""Transducers: components that convert electrical energy to / from
another physical domain.

A speaker turns audio-band current into acoustic pressure; a crystal
earpiece is the high-impedance variant of the same idea; a piezo
buzzer converts a self-resonant drive into a fixed-frequency tone.
All sit at the *boundary* of the electrical domain — the framework
treats them as two-terminal Analog passives with a characteristic
load impedance, the same way it treats the LDR.
"""
from .antenna          import Antenna
from .crystal_earpiece import CrystalEarpiece
from .earth            import Earth
from .speaker          import Speaker

__all__ = ['Antenna', 'CrystalEarpiece', 'Earth', 'Speaker']
