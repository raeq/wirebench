from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.drive_type import DriveType
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog, Digital
from framework.wire import wire
from framework.registry import register
from .concepts.comparator import Comparator


@register('LM393')
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

    __slots__ = ('_cells', '_refdes_number')

    CHANNELS: int = 2
    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-8_W7.62mm"
    # Both comparator outputs are open-collector — the silicon is an
    # uncommitted NPN whose collector is the OUT pin, so the chip can
    # sink LOW but cannot source HIGH on its own.  External pull-up
    # to a positive rail is required (the gotcha above documents this).
    PIN_DRIVE_TYPES: ClassVar[dict[str, "DriveType"]] = {
        'out_1': DriveType.OPEN_COLLECTOR,
        'out_2': DriveType.OPEN_COLLECTOR,
    }

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Wire a pull-up resistor (~10 kΩ to Vcc) on each output — "
        "the LM393's outputs can only pull LOW.** This is the most "
        "common LM393 mistake. The chip works fine, but without a "
        "pull-up the output node simply floats when the comparator "
        "wants to drive HIGH, and you see nothing on the breadboard. "
        "The pull-up gives the output something to drive against. "
        "(The technical name is 'open-collector output' — the chip's "
        "output transistor only sinks current; the pull-up sources it.)",
        "**You can tie two LM393 outputs together to make a 'this OR "
        "that' detector.** Wire the two outputs to a single shared "
        "pull-up resistor — if either comparator's input crosses its "
        "threshold, the shared node gets pulled LOW. Classic use: a "
        "window comparator that flags 'temperature too high *or* too "
        "low'. This trick works because of the open-collector "
        "structure; you couldn't do it with a normal opamp output.",
        "**Add a 1 MΩ resistor from the output back to the + input to "
        "stop the output flickering near the threshold.** With no "
        "feedback, tiny input noise repeatedly crosses the threshold "
        "and the output chatters between HIGH and LOW (you'll hear it "
        "if the output drives a speaker). The 1 MΩ creates a small "
        "amount of hysteresis — about 50 mV — that ignores the noise "
        "without significantly shifting the threshold.",
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *, refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._cells = tuple(Comparator(domain) for _ in range(self.CHANNELS))

        # 8-pin DIP datasheet pinout: pins 4 (GND) and 8 (VCC) omitted.
        #   ch 1: v_minus_1=2, v_plus_1=3, out_1=1
        #   ch 2: v_plus_2=5,  v_minus_2=6, out_2=7
        vp_numbers  = (3, 5)
        vm_numbers  = (2, 6)
        out_numbers = (1, 7)
        vp_pins, vm_pins, out_pins = [], [], []
        for i in range(self.CHANNELS):
            vp_pins .append(Pin(PinId(vp_numbers[i],  f'v_plus_{i+1}'),
                                Direction.IN,  domain, mandatory=False, signal_type=Analog))
            vm_pins .append(Pin(PinId(vm_numbers[i], f'v_minus_{i+1}'),
                                Direction.IN,  domain, mandatory=False, signal_type=Analog))
            out_pins.append(Pin(PinId(out_numbers[i], f'out_{i+1}'),
                                Direction.OUT, domain, mandatory=False, signal_type=Digital))

        for i, cell in enumerate(self._cells):
            wire(vp_pins[i].internal, cell.ports['v_plus'])
            wire(vm_pins[i].internal, cell.ports['v_minus'])
            wire(cell.ports['out'],   out_pins[i].internal)

        super().__init__(
            pins=vp_pins + vm_pins + out_pins,
            cells=list(self._cells),
        )

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(
        self,
        v_plus_1:  float | None,
        v_minus_1: float | None,
        v_plus_2:  float | None = None,
        v_minus_2: float | None = None,
    ) -> tuple[bool | None, bool | None]:
        self._assert_no_inputs_wired()
        self._ports['v_plus_1'].drive(v_plus_1)
        self._ports['v_minus_1'].drive(v_minus_1)
        self._ports['v_plus_2'].drive(v_plus_2)
        self._ports['v_minus_2'].drive(v_minus_2)
        self.evaluate()
        return (self._ports['out_1'].value, self._ports['out_2'].value)

    def __repr__(self) -> str:
        outs = tuple(self._ports[f'out_{i}'].value for i in range(1, self.CHANNELS + 1))
        return f"LM393(out={outs}, refdes={self.refdes!r})"
