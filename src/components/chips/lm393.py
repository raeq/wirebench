from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin
from framework.port import Direction
from framework.signals import Analog, Digital
from framework.wire import wire
from .concepts.comparator import Comparator


class LM393(Chip):
    """Texas Instruments LM393 — dual differential voltage comparator.

    Pins:
        v_plus_1, v_minus_1, out_1   — channel 1
        v_plus_2, v_minus_2, out_2   — channel 2

    Internally the chip composes two private Comparator cells.  The two
    channels share Vcc and GND but are otherwise independent.

    Real-world note: the LM393 outputs are open-collector and require an
    external pull-up resistor to register a logic HIGH.  This model
    drives a clean digital level for simulation; size the pull-up
    (typically 1–10 kΩ) when building the physical circuit.
    """

    __slots__ = ('_cells',)

    CHANNELS: int = 2

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._cells = tuple(Comparator(domain) for _ in range(self.CHANNELS))

        vp_pins, vm_pins, out_pins = [], [], []
        for i in range(1, self.CHANNELS + 1):
            vp_pins .append(Pin(f'v_plus_{i}',  Direction.IN,  domain, mandatory=False, signal_type=Analog))
            vm_pins .append(Pin(f'v_minus_{i}', Direction.IN,  domain, mandatory=False, signal_type=Analog))
            out_pins.append(Pin(f'out_{i}',     Direction.OUT, domain, mandatory=False, signal_type=Digital))

        for i, cell in enumerate(self._cells):
            wire(vp_pins[i].internal, cell.ports['v_plus'])
            wire(vm_pins[i].internal, cell.ports['v_minus'])
            wire(cell.ports['out'],   out_pins[i].internal)

        super().__init__(
            pins=vp_pins + vm_pins + out_pins,
            cells=list(self._cells),
        )

    def __call__(self, v_plus_1, v_minus_1, v_plus_2=None, v_minus_2=None) -> tuple:
        self._assert_no_inputs_wired()
        self._ports['v_plus_1'].drive(v_plus_1)
        self._ports['v_minus_1'].drive(v_minus_1)
        self._ports['v_plus_2'].drive(v_plus_2)
        self._ports['v_minus_2'].drive(v_minus_2)
        self.evaluate()
        return (self._ports['out_1'].value, self._ports['out_2'].value)

    def __repr__(self) -> str:
        return "LM393()"
