"""Passive components: resistors, LEDs, rails (and capacitors, inductors
when added).

A passive doesn't supply gain — it only stores, dissipates, or
redirects energy.  These are first-class consumer-facing parts you'd
place on a board (a 330 Ω resistor, a red LED, a Vcc/GND rail tie), so
they're re-exported here.
"""
from .capacitor          import Capacitor
from .cell               import Cell
from .ferrite_aerial     import FerriteAerial
from .inductor           import Inductor
from .led                import LED
from .photoresistor      import Photoresistor
from .rail               import Rail
from .resistor           import Resistor
from .variable_capacitor import VariableCapacitor

__all__ = [
    'Capacitor', 'Cell', 'FerriteAerial', 'Inductor', 'LED', 'Photoresistor',
    'Rail', 'Resistor', 'VariableCapacitor',
]
