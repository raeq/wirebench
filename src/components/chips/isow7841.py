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
from .concepts.isolated_channel import IsolatedChannel


@register('ISOW7841')
class ISOW7841(Chip):
    """Texas Instruments ISOW7841 — reinforced four-channel digital
    isolator with integrated isolated DC/DC power (16-pin SOIC-WB).

    The package straddles a galvanic-isolation barrier: pins 1-8 sit
    on the controller-side ('logic') domain, pins 9-16 on the
    isolated side ('iso').  Three channels (A, B, C) carry data from
    logic to iso; the fourth channel (D) reverses, carrying data
    from iso back to logic.  An on-chip transformer-driven converter
    derives a VISO rail on the secondary side from the primary-side
    VCC1 supply.

    In our voltage-only graph the DC/DC power generation is not
    simulable (transformer dynamics, charge-pump timing, etc.), and
    the channels themselves are modelled by `IsolatedChannel` concept
    cells whose ports straddle the two `GroundDomain` instances the
    Board passes in at construction.  Each cell connects to one logic-
    side pin and one iso-side pin via its internal port faces; the
    framework's wire() then enforces the rest of the same-domain
    rules everywhere else on the board.

    Use:
        from framework.ground import GroundDomain, ELECTRICAL
        ISOLATED = GroundDomain('isolated')
        u1 = ISOW7841(refdes_number=1,
                      logic_domain=ELECTRICAL,
                      iso_domain=ISOLATED)
    """

    __slots__ = ('_channels', '_refdes_number',
                 '_logic_domain', '_iso_domain')

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm"

    # Pin table: (number, name, direction, signal_type, 'logic' | 'iso').
    # Pins 1-8 = logic / primary side, pins 9-16 = isolated / secondary
    # side.  Within the logic side, channels A / B / C take their data
    # in on INA / INB / INC and channel D delivers its return data on
    # OUTD; the secondary side mirrors the inputs / outputs accordingly.
    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type, str], ...]] = (
        ( 1, 'VCC1',    Direction.IN,  Analog,  'logic'),
        ( 2, 'GND1',    Direction.IN,  Analog,  'logic'),
        ( 3, 'INA',     Direction.IN,  Digital, 'logic'),
        ( 4, 'INB',     Direction.IN,  Digital, 'logic'),
        ( 5, 'INC',     Direction.IN,  Digital, 'logic'),
        ( 6, 'OUTD',    Direction.OUT, Digital, 'logic'),    # reverse channel
        ( 7, 'GND1',    Direction.IN,  Analog,  'logic'),
        ( 8, 'EN1',     Direction.IN,  Digital, 'logic'),
        ( 9, 'EN2',     Direction.IN,  Digital, 'iso'),
        (10, 'GND2',    Direction.IN,  Analog,  'iso'),
        (11, 'IND',     Direction.IN,  Digital, 'iso'),      # reverse channel
        (12, 'OUTC',    Direction.OUT, Digital, 'iso'),
        (13, 'OUTB',    Direction.OUT, Digital, 'iso'),
        (14, 'OUTA',    Direction.OUT, Digital, 'iso'),
        (15, 'GND2',    Direction.IN,  Analog,  'iso'),
        (16, 'VISO',    Direction.OUT, Analog,  'iso'),
    )

    # Channel name -> (input pin name, output pin name, direction).
    # 'forward' is logic → iso; 'reverse' is iso → logic.
    _CHANNELS: ClassVar[tuple[tuple[str, str, str, str], ...]] = (
        ('A', 'INA', 'OUTA', 'forward'),
        ('B', 'INB', 'OUTB', 'forward'),
        ('C', 'INC', 'OUTC', 'forward'),
        ('D', 'IND', 'OUTD', 'reverse'),
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        *,
        refdes_number: RefdesNumber,
        logic_domain: GroundDomain = ELECTRICAL,
        iso_domain:   GroundDomain,
    ) -> None:
        if logic_domain is iso_domain:
            raise ValueError(
                f"ISOW7841 needs *distinct* logic and iso ground domains; "
                f"both are {logic_domain.name!r}"
            )
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._logic_domain  = logic_domain
        self._iso_domain    = iso_domain

        # Build pins with per-pin domain assignment.
        pins = []
        for number, name, direction, signal_type, side in self._PIN_TABLE:
            domain = logic_domain if side == 'logic' else iso_domain
            pins.append(Pin(PinId(number, name), direction, domain,
                            mandatory=False, signal_type=signal_type))
        by_name = {p.id.name: p for p in pins}

        # One IsolatedChannel cell per logical channel.  Forward
        # channels go logic → iso, the reverse channel goes iso →
        # logic.  Wiring within the chip connects each cell to the
        # corresponding pin's internal face on each side of the
        # barrier; each wire stays within a single ground domain so
        # the framework's same-domain rule is preserved.
        self._channels: dict[str, IsolatedChannel] = {}
        forward_pins, reverse_pins, power_pins = [], [], []
        for label, in_pin_name, out_pin_name, kind in self._CHANNELS:
            if kind == 'forward':
                cell = IsolatedChannel(input_domain=logic_domain,
                                       output_domain=iso_domain)
                forward_pins.append(by_name[out_pin_name])
            else:
                cell = IsolatedChannel(input_domain=iso_domain,
                                       output_domain=logic_domain)
                reverse_pins.append(by_name[out_pin_name])
            self._channels[label] = cell
            wire(by_name[in_pin_name].internal,  cell.ports['input'])
            wire(cell.ports['output'],            by_name[out_pin_name].internal)

        # Bypass Chip.__init__'s `pins + cells` ordering: lay out
        # factor_nodes so input pins come first, then the channel
        # cells, then the output pins, so the topological sort visits
        # them in dataflow order even when a feedback wire collapses
        # the graph to declaration order (same trick CD4017 uses for
        # its decade-counter feedback loop).
        in_pin_names  = {pname for _, pname, _, _ in self._CHANNELS}
        out_pin_names = {pname for _, _, pname, _ in self._CHANNELS}
        input_pins    = [p for p in pins if p.id.name in in_pin_names]
        output_pins   = [p for p in pins if p.id.name in out_pin_names]
        power_pins    = [p for p in pins
                         if p.id.name not in in_pin_names
                         and p.id.name not in out_pin_names]
        cells = list(self._channels.values())
        self._ports_by_number = {pin.id.number: pin.external for pin in pins}
        self._port_map = PortMap(self._ports_by_number)
        Circuit.__init__(
            self,
            factor_nodes=input_pins + cells + output_pins + power_pins,
            ports=dict(self._port_map.items()),
        )

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @property
    def logic_domain(self) -> GroundDomain:
        return self._logic_domain

    @property
    def iso_domain(self) -> GroundDomain:
        return self._iso_domain

    @property
    def channels(self) -> dict[str, IsolatedChannel]:
        """The four `IsolatedChannel` cells, keyed by channel label."""
        return self._channels

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(
        self,
        ina: bool | None = None,
        inb: bool | None = None,
        inc: bool | None = None,
        ind: bool | None = None,
    ) -> dict[str, bool | None]:
        """Standalone-test invocation: drive the four input pins
        (INA/B/C on the logic side, IND on the iso side) and read back
        the four output pin values (OUTA/B/C on iso, OUTD on logic)."""
        self._assert_no_inputs_wired()
        self._ports['INA'].drive(ina)
        self._ports['INB'].drive(inb)
        self._ports['INC'].drive(inc)
        self._ports['IND'].drive(ind)
        self.evaluate()
        return {
            'OUTA': self._ports['OUTA'].value,
            'OUTB': self._ports['OUTB'].value,
            'OUTC': self._ports['OUTC'].value,
            'OUTD': self._ports['OUTD'].value,
        }

    def __repr__(self) -> str:
        return (f"ISOW7841(refdes={self.refdes!r}, "
                f"logic_domain={self._logic_domain.name!r}, "
                f"iso_domain={self._iso_domain.name!r})")
