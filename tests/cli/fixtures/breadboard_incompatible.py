"""A chip with a floating VCC pin → BreadboardIncompatibleError when
the assembly-guide ERC walks the design.

The ERC fires only when an export is requested, so the design runs
the export inline from __init__ — the same pattern used in the
prevention-benchmark reproducers."""
from framework import Circuit, wire
from framework.export import export_to_string
from wirebench import Analog, Rail, SN74HC04


class FloatingVCC(Circuit):
    def __init__(self) -> None:
        self.gnd = Rail(False, signal_type=Analog)
        self.u1  = SN74HC04(refdes_number=1)
        wire(self.gnd.ports['out'], self.u1.ports['GND'])
        # VCC deliberately left unwired.
        super().__init__()
        export_to_string(self, 'assembly_guide')
