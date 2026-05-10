from typing import ClassVar

from framework.chip import Chip
from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin
from framework.port import Direction
from framework.refdes import validate_refdes
from framework.signals import Digital
from framework.wire import wire
from .concepts.nor_latch import NORLatch
from .concepts.tristate_buffer import TriStateBuffer


class CD4043(Chip):
    """Texas Instruments CD4043B — quad NOR-based RS latch with tri-state outputs.

    Pins:
        s_1, r_1 .. s_4, r_4 — set/reset inputs for each latch
        q_1 .. q_4           — outputs (tri-stated when OE=LOW)
        oe                   — chip-level output enable (active HIGH)

    Internally the chip composes four NORLatch cells and four
    TriStateBuffer cells, connected by an internal OE distribution
    wire.  Real CD4043B silicon does not bond /Q out to a package pin;
    if a consumer needs the inverted output, derive it externally with
    an inverter (e.g. one gate of an SN74HC04 or CD4069).

    OE behaviour
    ------------
    OE=1 — Q reflects each latch's state.
    OE=0 — Q is forced to high-impedance (None).

    OE distribution is a real internal wire from the OE pin's internal
    face to every tri-state buffer's enable input.  The topological sort
    over the internal mesh produces evaluation order automatically.

    OE has no integrated pull-up.  In a real circuit OE must always be
    tied to VDD or a control signal — left floating, the chip's outputs
    are undefined.
    """

    __slots__ = ('_latches', '_buf_q', '_refdes_number')

    CHANNELS: int = 4
    REFDES_PREFIX: ClassVar[str] = 'U'

    def __init__(self, domain: GroundDomain = ELECTRICAL, *, refdes_number: int) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        # --- Cells: the chip's private implementation ---
        # Each latch's q_bar internal port stays unwired — real silicon
        # generates it for the cross-coupling but does not bond it out.
        self._latches = tuple(NORLatch(domain)       for _ in range(self.CHANNELS))
        self._buf_q   = tuple(TriStateBuffer(domain) for _ in range(self.CHANNELS))

        # --- Pins: the chip's external surface ---
        oe = Pin('oe', Direction.IN, domain, mandatory=False, signal_type=Digital)
        s_pins, r_pins, q_pins = [], [], []
        for i in range(1, self.CHANNELS + 1):
            s_pins.append(Pin(f's_{i}', Direction.IN,  domain, mandatory=False, signal_type=Digital))
            r_pins.append(Pin(f'r_{i}', Direction.IN,  domain, mandatory=False, signal_type=Digital))
            q_pins.append(Pin(f'q_{i}', Direction.OUT, domain, mandatory=False, signal_type=Digital))

        # --- Internal wiring: pins ↔ cells ---
        for i, latch in enumerate(self._latches):
            wire(s_pins[i].internal, latch.ports['s'])
            wire(r_pins[i].internal, latch.ports['r'])
            wire(latch.ports['q'],          self._buf_q[i].ports['a'])
            wire(self._buf_q[i].ports['y'], q_pins[i].internal)

        # Shared OE: one fan-out wire from oe.internal to all 4 buffer enables.
        wire(oe.internal, *(b.ports['oe'] for b in self._buf_q))

        cells: list[FactorNode] = []
        cells.extend(self._latches)
        cells.extend(self._buf_q)
        super().__init__(
            pins=[oe] + s_pins + r_pins + q_pins,
            cells=cells,
        )

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    def __call__(
        self,
        s_1: bool = False, r_1: bool = False,
        s_2: bool = False, r_2: bool = False,
        s_3: bool = False, r_3: bool = False,
        s_4: bool = False, r_4: bool = False,
        *,
        oe:  bool,
    ) -> tuple[bool | None, ...]:
        self._assert_no_inputs_wired()
        sr = ((s_1, r_1), (s_2, r_2), (s_3, r_3), (s_4, r_4))
        for i, (s, r) in enumerate(sr, start=1):
            self._ports[f's_{i}'].drive(s)
            self._ports[f'r_{i}'].drive(r)
        self._ports['oe'].drive(oe)
        self.evaluate()
        return tuple(
            self._ports[f'q_{i}'].value
            for i in range(1, self.CHANNELS + 1)
        )

    def __repr__(self) -> str:
        latches = ', '.join(str(l.ports['q'].value) for l in self._latches)
        return f"CD4043(q=({latches}), refdes={self.refdes!r})"
