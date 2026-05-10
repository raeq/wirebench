from framework.circuit import Circuit
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin
from framework.port import Direction
from framework.signals import Analog, Digital
from framework.wire import wire
from .concepts.comparator import Comparator


class LM393(Circuit):
    """Texas Instruments LM393 — dual differential voltage comparator.

    The chip's external surface is its 8 package pins:
        v_plus_1, v_minus_1, out_1   — channel 1
        v_plus_2, v_minus_2, out_2   — channel 2

    Each pin is a `Pin` — a bonded-wire relay between the package and the
    silicon. Internally the chip composes two private Comparator cells.
    The two channels share Vcc and GND but are otherwise independent.

    Real-world note: the LM393 outputs are open-collector and require an
    external pull-up resistor to register a logic HIGH.  This model
    drives a clean digital level for simulation; size the pull-up
    (typically 1–10 kΩ) when building the physical circuit.
    """

    __slots__ = ['_cells']

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

        ports = {p.external.name: p.external for p in vp_pins + vm_pins + out_pins}
        super().__init__(
            factor_nodes=list(vp_pins + vm_pins + out_pins) + list(self._cells),
            ports=ports,
        )

    def __call__(self, v_plus_1, v_minus_1, v_plus_2=None, v_minus_2=None) -> tuple:
        wired = [n for n, p in self._ports.items()
                 if p.direction is Direction.IN and p.connected]
        if wired:
            raise RuntimeError(
                f"LM393.__call__ refused: input pin(s) wired by an enclosing "
                f"circuit ({', '.join(wired)}); drive via the parent's "
                f"evaluate() instead."
            )
        self._ports['v_plus_1'].drive(v_plus_1)
        self._ports['v_minus_1'].drive(v_minus_1)
        self._ports['v_plus_2'].drive(v_plus_2)
        self._ports['v_minus_2'].drive(v_minus_2)
        self.evaluate()
        return (self._ports['out_1'].value, self._ports['out_2'].value)

    def __repr__(self) -> str:
        return "LM393()"
