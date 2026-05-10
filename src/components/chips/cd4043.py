from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin
from framework.port import Direction
from framework.signals import Digital
from framework.wire import wire
from .concepts.nor_latch import NORLatch
from .concepts.tristate_buffer import TriStateBuffer


class CD4043(Chip):
    """Texas Instruments CD4043B — quad NOR-based RS latch with tri-state outputs.

    Pins:
        s_1, r_1 .. s_4, r_4         — set/reset inputs
        q_1, q_1_bar .. q_4, q_4_bar — outputs (tri-stated when OE=LOW)
        oe                           — chip-level output enable (active HIGH)

    Internally the chip composes four NORLatch cells and eight
    TriStateBuffer cells, connected by an internal OE distribution wire.

    OE behaviour
    ------------
    OE=1 — Q and /Q reflect each latch's state.
    OE=0 — Q and /Q are forced to high-impedance (None).

    OE distribution is a real internal wire from the OE pin's internal
    face to every tri-state buffer's enable input.  The topological sort
    over the internal mesh produces evaluation order automatically.

    OE has no integrated pull-up.  In a real circuit OE must always be
    tied to VDD or a control signal — left floating, the chip's outputs
    are undefined.
    """

    __slots__ = ('_latches', '_buf_q', '_buf_q_bar')

    CHANNELS: int = 4

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        # --- Cells: the chip's private implementation ---
        self._latches   = tuple(NORLatch(domain)       for _ in range(self.CHANNELS))
        self._buf_q     = tuple(TriStateBuffer(domain) for _ in range(self.CHANNELS))
        self._buf_q_bar = tuple(TriStateBuffer(domain) for _ in range(self.CHANNELS))

        # --- Pins: the chip's external surface ---
        # OE has no integrated pull-up — real CD4043 silicon requires it
        # to be tied to VDD or a control signal explicitly. Leaving OE
        # floating produces undefined outputs (None propagates through).
        oe = Pin('oe', Direction.IN, domain, mandatory=False, signal_type=Digital)
        s_pins, r_pins, q_pins, qb_pins = [], [], [], []
        for i in range(1, self.CHANNELS + 1):
            s_pins .append(Pin(f's_{i}',     Direction.IN,  domain, mandatory=False, signal_type=Digital))
            r_pins .append(Pin(f'r_{i}',     Direction.IN,  domain, mandatory=False, signal_type=Digital))
            q_pins .append(Pin(f'q_{i}',     Direction.OUT, domain, mandatory=False, signal_type=Digital))
            qb_pins.append(Pin(f'q_{i}_bar', Direction.OUT, domain, mandatory=False, signal_type=Digital))

        # --- Internal wiring: pins ↔ cells ---
        for i, latch in enumerate(self._latches):
            wire(s_pins[i].internal, latch.ports['s'])
            wire(r_pins[i].internal, latch.ports['r'])
            wire(latch.ports['q'],     self._buf_q[i].ports['a'])
            wire(latch.ports['q_bar'], self._buf_q_bar[i].ports['a'])
            wire(self._buf_q[i].ports['y'],     q_pins[i].internal)
            wire(self._buf_q_bar[i].ports['y'], qb_pins[i].internal)

        # Shared OE: one fan-out wire from oe.internal to all 8 buffer enables.
        wire(
            oe.internal,
            *(b.ports['oe'] for b in self._buf_q),
            *(b.ports['oe'] for b in self._buf_q_bar),
        )

        super().__init__(
            pins=[oe] + s_pins + r_pins + q_pins + qb_pins,
            cells=list(self._latches) + list(self._buf_q) + list(self._buf_q_bar),
        )

    def __call__(
        self,
        s_1: bool = False, r_1: bool = False,
        s_2: bool = False, r_2: bool = False,
        s_3: bool = False, r_3: bool = False,
        s_4: bool = False, r_4: bool = False,
        oe:  bool = True,
    ) -> tuple[tuple[bool | None, bool | None], ...]:
        self._assert_no_inputs_wired()
        sr = ((s_1, r_1), (s_2, r_2), (s_3, r_3), (s_4, r_4))
        for i, (s, r) in enumerate(sr, start=1):
            self._ports[f's_{i}'].drive(s)
            self._ports[f'r_{i}'].drive(r)
        self._ports['oe'].drive(oe)
        self.evaluate()
        return tuple(
            (self._ports[f'q_{i}'].value, self._ports[f'q_{i}_bar'].value)
            for i in range(1, self.CHANNELS + 1)
        )

    def __repr__(self) -> str:
        latches = ', '.join(str(l.ports['q'].value) for l in self._latches)
        return f"CD4043(q=({latches}))"
