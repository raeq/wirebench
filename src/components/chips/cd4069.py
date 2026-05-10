from framework.circuit import Circuit
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin
from framework.port import Direction
from framework.signals import Digital
from framework.wire import wire
from .concepts.inverter import Inverter


class CD4069(Circuit):
    """Texas Instruments CD4069UB — hex unbuffered inverter.

    The chip's external surface is its 12 signal pins (Vcc/GND not modelled):
        a_1 .. a_6 — gate inputs
        y_1 .. y_6 — gate outputs (y_i = NOT(a_i))

    Each pin is a `Pin` — a bonded-wire relay between the package and the
    silicon. Internally the chip composes six private Inverter cells.

    Supply voltage: 3 V – 18 V.  Propagation delay: ~30 ns at 5 V.

    The 'UB' suffix means unbuffered — one inversion stage per gate, not
    three.  This makes each gate usable as a linear amplifier or
    oscillator element when biased in the transition region, unlike the
    SN74HC04 which is hard-switched.  The cell-level Inverter does not
    model that distinction; for pure logic inversion the two parts are
    equivalent.

    Unused CMOS inputs must always be tied to GND or Vcc in real
    circuits — never left floating.
    """

    __slots__ = ['_gates']

    CHANNELS: int = 6

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._gates = tuple(Inverter(domain) for _ in range(self.CHANNELS))

        a_pins, y_pins = [], []
        for i in range(1, self.CHANNELS + 1):
            a_pins.append(Pin(f'a_{i}', Direction.IN,  domain, mandatory=False, signal_type=Digital))
            y_pins.append(Pin(f'y_{i}', Direction.OUT, domain, mandatory=False, signal_type=Digital))

        for i, gate in enumerate(self._gates):
            wire(a_pins[i].internal, gate.ports['a'])
            wire(gate.ports['y'],    y_pins[i].internal)

        ports = {p.external.name: p.external for p in a_pins + y_pins}
        super().__init__(
            factor_nodes=list(a_pins + y_pins) + list(self._gates),
            ports=ports,
        )

    def __call__(self, *inputs) -> tuple:
        if len(inputs) > self.CHANNELS:
            raise ValueError(f"CD4069 has {self.CHANNELS} channels; got {len(inputs)} inputs")
        wired = [n for n, p in self._ports.items()
                 if p.direction is Direction.IN and p.connected]
        if wired:
            raise RuntimeError(
                f"CD4069.__call__ refused: input pin(s) wired by an enclosing "
                f"circuit ({', '.join(wired)}); drive via the parent's "
                f"evaluate() instead."
            )
        for i in range(self.CHANNELS):
            v = inputs[i] if i < len(inputs) else False
            self._ports[f'a_{i+1}'].drive(v)
        self.evaluate()
        return tuple(self._ports[f'y_{i+1}'].value for i in range(self.CHANNELS))

    def __str__(self) -> str:
        return ' '.join(
            f'G{i+1}:{"H" if self._ports[f"y_{i+1}"].value else "L"}'
            for i in range(self.CHANNELS)
        )

    def __repr__(self) -> str:
        return 'CD4069()'
