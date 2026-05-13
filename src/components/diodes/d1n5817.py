from typing import ClassVar

from pydantic import validate_call

from framework.circuit import Circuit
from framework.diode import Diode
from framework.ground import GroundDomain, ELECTRICAL
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from components.chips.concepts.diode_forward import DiodeForward


@register('D1N5817')
class D1N5817(Diode, Circuit):
    """1N5817 — Schottky barrier rectifier (20 V / 1 A, low V_F, DO-41).

    Wraps a private `DiodeForward` cell so the framework's ERC walker
    sees the diode as a real conductor with a forward drop — usable as
    a series rectifier or reverse-protection part in a DC supply chain
    without falling foul of the floating-net check.  V_F is modelled as
    0.3 V (typical Schottky drop at hobby-sized currents); V_R max =
    20 V; I_F avg = 1 A; I_FSM = 25 A.  The model is voltage-only and
    steady-state — for accurate analogue / reverse-leakage simulation,
    substitute a vendor SPICE .MODEL.
    """

    __slots__ = ('_cell', '_refdes_number')

    V_F: ClassVar[float] = 0.3   # Schottky forward voltage drop

    REFDES_PREFIX: ClassVar[str] = 'D'
    FOOTPRINT: ClassVar[str | None] = "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'anode': 1, 'cathode': 2}

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**A Schottky reads a lower forward voltage than a silicon "
        "diode on the multimeter's diode test.** Red probe on the "
        "anode (unmarked end), black on the cathode (banded end): a "
        "healthy 1N5817 reads about 0.2–0.3 V forward, not the 0.6 V "
        "you'd see from a 1N4001 — the low drop is the Schottky's "
        "defining feature. Reverse the probes and the meter reads OL. "
        "If you read 0.6 V forward, somebody put a silicon diode in "
        "the Schottky bin.",
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**The black band marks the cathode (− end)** — same convention "
        "as silicon diodes. The Schottky's marking matches the bar in "
        "the schematic symbol.",
        "**Use the 1N5817 wherever you'd use a 1N4001 but need lower "
        "voltage drop or faster switching.** Schottkys drop only ~0.3 V "
        "in forward bias (versus ~0.7 V for a silicon diode), so a "
        "switching-supply rectifier or a battery-OR diode loses less "
        "power as heat. The trade-off: Schottkys leak a small reverse "
        "current even when 'off' — over weeks they slowly drain the "
        "lower of two OR'd batteries, so don't use them for long-term "
        "battery backup arrangements.",
        "**This part only blocks 20 V reverse — don't use it where "
        "voltages exceed that.** A mains-rectifier transformer "
        "secondary, a 24 V motor flyback path, or anywhere ringing "
        "transients might exceed 20 V will pop the 1N5817. The 1N5819 "
        "(same package, 40 V reverse) handles more; above that, use a "
        "silicon diode like the 1N4007 instead.",
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._cell = DiodeForward(v_f=self.V_F, domain=domain)
        # The composite's boundary ports are *literally* the cell's
        # ports — same Port objects.  This makes the diode look like a
        # 2-pin leaf to external wiring (`wire(rail.out, d1.anode)`)
        # while the internal cell carries the forward-conduction
        # behaviour.  Same trick as a thin Chip with one cell whose
        # ports are the package pins.
        super().__init__(
            factor_nodes=[self._cell],
            ports={
                'anode':   self._cell.ports['anode'],
                'cathode': self._cell.ports['cathode'],
            },
        )

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, anode: float | None = None) -> float | None:
        self._assert_no_inputs_wired()
        if anode is not None:
            self.ports['anode'].drive(anode)
        self.evaluate()
        result = self.ports['cathode'].value
        return float(result) if result is not None else None

    def __repr__(self) -> str:
        return f"D1N5817(refdes={self.refdes!r})"
