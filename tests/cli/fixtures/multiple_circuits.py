"""Two distinct Circuit subclasses, neither requiring args.  Used to
test the 'multiple candidates without --class' error path."""
from components.passives.rail import Rail
from components.passives.resistor import Resistor
from framework import Circuit, wire


class DesignA(Circuit):
    def __init__(self) -> None:
        self.vcc = Rail(True)
        self.gnd = Rail(False)
        self.r1  = Resistor(330, refdes_number=1)
        wire(self.vcc.out, self.r1.t1)
        wire(self.r1.t2, self.gnd.out)
        super().__init__()


class DesignB(Circuit):
    def __init__(self) -> None:
        self.vcc = Rail(True)
        self.gnd = Rail(False)
        self.r1  = Resistor(470, refdes_number=1)
        wire(self.vcc.out, self.r1.t1)
        wire(self.r1.t2, self.gnd.out)
        super().__init__()
