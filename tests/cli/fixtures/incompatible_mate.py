"""mate() between incompatible connector families → IncompatibleMateError.

The mate() call raises before Circuit.__init__ returns, but the
validator catches it the same way it catches any construction-time
error."""
from components.connectors.headers import Header2xNMale
from components.connectors.jst_ph import JSTPHCableHousing
from framework import Circuit, mate


class WrongMate(Circuit):
    def __init__(self) -> None:
        self.j1 = Header2xNMale(pin_count=40, pitch_mm=2.54, refdes_number=1)
        self.j2 = JSTPHCableHousing(pin_count=4, refdes_number=1)
        mate(self.j1, self.j2)
        super().__init__()
