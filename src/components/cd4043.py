from framework.circuit import Circuit
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin
from framework.port import Direction
from framework.signals import Digital
from framework.wire import wire
from .nor_latch import NORLatch
from .tristate_buffer import TriStateBuffer


class CD4043(Circuit):
    """Texas Instruments CD4043B — quad NOR-based RS latch with tri-state outputs.

    The chip's external surface is its 16 package pins:
        s_1, r_1 .. s_4, r_4         — set/reset inputs
        q_1, q_1_bar .. q_4, q_4_bar — outputs (tri-stated when OE=LOW)
        oe                           — chip-level output enable (active HIGH)

    Each pin is a `Pin` — a bonded-wire relay between the package and the
    silicon. Internally the chip composes a private circuit of NOR latches
    and tri-state buffers that consumers never see. The internal topology
    is an implementation detail; only the pins are part of the API.

    OE behaviour
    ------------
    OE=1 — Q and /Q reflect each latch's state.
    OE=0 — Q and /Q are forced to high-impedance (None).

    OE distribution is a real internal wire from the OE pin's internal face
    to every tri-state buffer's enable input. The chip's evaluation order
    is determined by the topological sort over the internal network — no
    imperative fan-out, no override of `evaluate`.
    """

    __slots__ = ['_latches', '_buf_q', '_buf_q_bar']

    CHANNELS: int = 4

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        # --- Cells: the chip's private implementation ---
        self._latches   = tuple(NORLatch(domain)       for _ in range(self.CHANNELS))
        self._buf_q     = tuple(TriStateBuffer(domain) for _ in range(self.CHANNELS))
        self._buf_q_bar = tuple(TriStateBuffer(domain) for _ in range(self.CHANNELS))

        # --- Pins: the chip's external API surface ---
        # OE has a weak pull-up: if no signal is asserted on the package pin
        # the chip behaves as if OE=HIGH (outputs enabled). Real CD4043
        # silicon doesn't do this — left-floating OE is forbidden — but
        # modelling the convenience here matches the previous behaviour.
        oe = Pin('oe', Direction.IN, domain, mandatory=False, signal_type=Digital, default=True)
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

        # OE distribution: a single fan-out wire from the OE pin to every
        # buffer's enable input. The topological sort sees this as a real
        # edge — no imperative drive, no evaluate override.
        wire(
            oe.internal,
            *(b.ports['oe'] for b in self._buf_q),
            *(b.ports['oe'] for b in self._buf_q_bar),
        )

        # --- Boundary surface visible to consumers: external pin faces ---
        ports = {'oe': oe.external}
        for i, p in enumerate(s_pins,  start=1): ports[f's_{i}']      = p.external
        for i, p in enumerate(r_pins,  start=1): ports[f'r_{i}']      = p.external
        for i, p in enumerate(q_pins,  start=1): ports[f'q_{i}']      = p.external
        for i, p in enumerate(qb_pins, start=1): ports[f'q_{i}_bar']  = p.external

        all_pins = [oe] + s_pins + r_pins + q_pins + qb_pins
        factor_nodes = (
            list(all_pins)
            + list(self._latches)
            + list(self._buf_q)
            + list(self._buf_q_bar)
        )
        super().__init__(factor_nodes=factor_nodes, ports=ports)

    def __call__(
        self,
        s_1=False, r_1=False,
        s_2=False, r_2=False,
        s_3=False, r_3=False,
        s_4=False, r_4=False,
        oe=True,
    ) -> tuple:
        # __call__ is the standalone-test entry point. If any input pin is
        # already wired by an enclosing circuit, calling the chip directly
        # would silently overwrite that signal — refuse instead.
        wired = [
            name for name, p in self._ports.items()
            if p.direction is Direction.IN and p.connected
        ]
        if wired:
            raise RuntimeError(
                f"CD4043.__call__ refused: input pin(s) wired by an enclosing "
                f"circuit ({', '.join(wired)}); drive via the parent's evaluate() "
                f"instead."
            )
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
        latches = ', '.join(str(l._q) for l in self._latches)
        return f"CD4043(q=({latches}))"
