from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.circuit import Circuit
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.port_map import PortMap
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog, Digital
from framework.wire import wire
from framework.registry import register
from .concepts.decade_counter import DecadeCounter


@register('CD4017')
class CD4017(Chip):
    """RCA / Texas Instruments CD4017 — CMOS decade Johnson counter
    with ten decoded outputs (DIP-16).

    Pins (the package's named external surface, exactly as the
    datasheet has them — note the non-sequential output ordering):

        1  Q5      9  Q8
        2  Q1     10  Q4
        3  Q0     11  Q9
        4  Q2     12  CO   (carry / ÷10, HIGH for counts 0..4)
        5  Q6     13  CE   (clock enable, active LOW)
        6  Q7     14  CLK
        7  Q3     15  RST
        8  VSS    16  VDD

    Internally the chip is a single `DecadeCounter` cell whose three
    control inputs (clk / inhibit / reset) and eleven outputs
    (q0..q9, co) are bonded to the relevant pin internal faces.  The
    counter advances on the rising edge of CLK while CE is LOW and
    RST is LOW; pulling RST HIGH at any time forces count to 0.

    Supply voltage: 3 V – 18 V (CMOS).  Typical maximum clock rate
    ~5 MHz at 10 V.  All unused outputs may be left open; unused
    inputs must be tied to VDD or VSS — never floating.
    """

    __slots__ = ('_counter', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-16_W7.62mm"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        ( 1, 'Q5',  Direction.OUT, Digital),
        ( 2, 'Q1',  Direction.OUT, Digital),
        ( 3, 'Q0',  Direction.OUT, Digital),
        ( 4, 'Q2',  Direction.OUT, Digital),
        ( 5, 'Q6',  Direction.OUT, Digital),
        ( 6, 'Q7',  Direction.OUT, Digital),
        ( 7, 'Q3',  Direction.OUT, Digital),
        ( 8, 'VSS', Direction.IN,  Analog),
        ( 9, 'Q8',  Direction.OUT, Digital),
        (10, 'Q4',  Direction.OUT, Digital),
        (11, 'Q9',  Direction.OUT, Digital),
        (12, 'CO',  Direction.OUT, Digital),
        (13, 'CE',  Direction.IN,  Digital),
        (14, 'CLK', Direction.IN,  Digital),
        (15, 'RST', Direction.IN,  Digital),
        (16, 'VDD', Direction.IN,  Analog),
    )

    # External pin name → cell port name.  VSS/VDD have no cell hookup;
    # they are off-graph supply.
    _CELL_HOOKUP: ClassVar[dict[str, str]] = {
        'CLK': 'clk',
        'CE':  'inhibit',
        'RST': 'reset',
        'Q0':  'q0', 'Q1': 'q1', 'Q2': 'q2', 'Q3': 'q3', 'Q4': 'q4',
        'Q5':  'q5', 'Q6': 'q6', 'Q7': 'q7', 'Q8': 'q8', 'Q9': 'q9',
        'CO':  'co',
    }

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._counter = DecadeCounter(domain)

        pins = [
            Pin(PinId(number, name), direction, domain,
                mandatory=False, signal_type=signal_type)
            for number, name, direction, signal_type in self._PIN_TABLE
        ]
        by_name = {p.id.name: p for p in pins}

        for pin_name, cell_port in self._CELL_HOOKUP.items():
            wire(by_name[pin_name].internal, self._counter.ports[cell_port])

        # Bypass Chip.__init__'s default `pins + cells` ordering: an
        # external Q_N → RST feedback wire (the canonical cycle-limit
        # idiom for this part) makes the parent's topological sort
        # fall back to declaration order.  If OUT pins evaluated
        # before the cell, their externals would still be stale (None)
        # while downstream readers consumed them.  Place IN pins
        # first, the counter cell next, OUT pins after — power pins
        # last — so the fallback order matches the actual dataflow.
        in_pin_names    = {'CLK', 'CE', 'RST'}
        out_pin_names   = {'Q0', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5',
                           'Q6', 'Q7', 'Q8', 'Q9', 'CO'}
        in_pins    = [p for p in pins if p.id.name in in_pin_names]
        out_pins   = [p for p in pins if p.id.name in out_pin_names]
        power_pins = [p for p in pins if p.id.name not in in_pin_names
                                       and p.id.name not in out_pin_names]
        self._ports_by_number = {pin.id.number: pin.external for pin in pins}
        self._port_map = PortMap(self._ports_by_number)
        Circuit.__init__(
            self,
            factor_nodes=in_pins + [self._counter] + out_pins + power_pins,
            ports=dict(self._port_map.items()),
        )

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @property
    def count(self) -> int:
        """Current internal counter state (0..9)."""
        return self._counter.count

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self,
                 clk: bool | None,
                 ce: bool | None = False,
                 rst: bool | None = False,
                 ) -> int:
        self._assert_no_inputs_wired()
        self._ports['CLK'].drive(clk)
        self._ports['CE'].drive(ce)
        self._ports['RST'].drive(rst)
        self.evaluate()
        return self._counter.count

    def __repr__(self) -> str:
        return f"CD4017(count={self._counter.count}, refdes={self.refdes!r})"
