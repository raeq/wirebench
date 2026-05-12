"""Electromechanical relays — coil-driven contact switches.

Each relay subclass exposes its coil terminals plus the contact
terminals (COM / NO / NC for SPDT, more for multi-pole variants).
The framework's voltage-only simulator cannot dynamically merge
nets the way a real contact does, so the contacts are wired as
BIDIR Analog conductor-wildcards (no signal propagation) and the
relay's switched state is exposed as a Python-level `closed_path`
property derived from the coil voltage.
"""
from .spdt import Relay_SPDT

__all__ = ['Relay_SPDT']
