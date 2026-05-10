"""Passive components: resistors, LEDs (and capacitors, inductors when added).

A passive doesn't supply gain — it only stores, dissipates, or
redirects energy.  These are first-class consumer-facing parts (you
buy a 330 Ω resistor or a red LED), so they're re-exported here.
"""
from .led      import LED
from .resistor import Resistor
