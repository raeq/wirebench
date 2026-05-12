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
from .concepts.buffer import Buffer


@register('TRS3122E')
class TRS3122E(Chip):
    """Texas Instruments TRS3122E — full-duplex RS-232 line driver /
    receiver with 1.65-5.5 V logic supply and ±15 kV IEC-ESD-protected
    line pins (20-pin TSSOP).

    Two transmitter channels (logic TIN1/2 → RS-232 TOUT1/2) and two
    receiver channels (RS-232 RIN1/2 → logic ROUT1/2).  An internal
    charge pump on C1/C2/V+/V- generates ±5.5 V from a single VCC
    rail to drive the RS-232 line pins to the correct levels.

    The chip is modelled here with four internal `Buffer` cells —
    one per logic-level channel — to give the framework's voltage-
    only graph something to propagate.  The charge-pump dynamics and
    actual ±9 V line-level translation are not simulable in a steady-
    state graph; for our purposes the cells just mirror digital
    levels through the package, which is the only thing downstream
    logic actually observes.

    All pins sit in a single ground domain — TRS3122E is not an
    isolator, just a level translator.  Use it on the isolated side
    of an upstream digital isolator (e.g. ISOW7841) and pass the
    isolator's iso-side domain when constructing it.
    """

    __slots__ = ('_tx1', '_tx2', '_rx1', '_rx2', '_refdes_number', '_domain')

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm"

    # The TRS3122E lives entirely on one side of an isolation barrier
    # (see the iso-RS-232 demo); serialise the chosen ground domain
    # so loaded designs reconstruct in the right one rather than
    # always defaulting to ELECTRICAL.
    SERIALIZE_KWARGS: ClassVar[tuple[str, ...]] = ('domain',)

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        ( 1, 'VL',       Direction.IN,  Analog),    # logic-side supply
        ( 2, 'VCC',      Direction.IN,  Analog),    # charge-pump supply
        ( 3, 'GND',      Direction.IN,  Analog),
        ( 4, 'C1+',      Direction.IN,  Analog),    # charge-pump flying cap
        ( 5, 'V+',       Direction.OUT, Analog),    # +5.5 V pump output
        ( 6, 'C1-',      Direction.IN,  Analog),
        ( 7, 'C2+',      Direction.IN,  Analog),
        ( 8, 'C2-',      Direction.IN,  Analog),
        ( 9, 'V-',       Direction.OUT, Analog),    # -5.5 V pump output
        (10, 'TIN2',     Direction.IN,  Digital),
        (11, 'ROUT2',    Direction.OUT, Digital),
        (12, 'TOUT2',    Direction.OUT, Digital),   # RS-232 line out
        (13, 'RIN2',     Direction.IN,  Digital),   # RS-232 line in
        (14, 'GND',      Direction.IN,  Analog),
        (15, 'TIN1',     Direction.IN,  Digital),
        (16, 'ROUT1',    Direction.OUT, Digital),
        (17, 'RIN1',     Direction.IN,  Digital),
        (18, 'TOUT1',    Direction.OUT, Digital),
        (19, 'SHDN',     Direction.IN,  Digital),   # active-LOW shutdown
        (20, 'INVALID',  Direction.OUT, Digital),   # active-LOW receiver-valid
    )

    # Channel mappings: input pin name -> (output pin name, role).
    _CHANNELS: ClassVar[tuple[tuple[str, str, str], ...]] = (
        ('TIN1', 'TOUT1', 'tx1'),
        ('TIN2', 'TOUT2', 'tx2'),
        ('RIN1', 'ROUT1', 'rx1'),
        ('RIN2', 'ROUT2', 'rx2'),
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._domain        = domain

        pins = [
            Pin(PinId(number, name), direction, domain,
                mandatory=False, signal_type=signal_type)
            for number, name, direction, signal_type in self._PIN_TABLE
        ]
        by_name = {p.id.name: p for p in pins}

        # Behavioural cells — one Buffer per logic-level channel.
        self._tx1 = Buffer(domain)
        self._tx2 = Buffer(domain)
        self._rx1 = Buffer(domain)
        self._rx2 = Buffer(domain)
        cells = [self._tx1, self._tx2, self._rx1, self._rx2]

        # Wire each cell between its input pin's internal face and
        # its output pin's internal face.  Two TX cells drive the
        # RS-232 line outputs; two RX cells drive the logic-side
        # outputs from RS-232 inputs.
        cell_by_role = {'tx1': self._tx1, 'tx2': self._tx2,
                        'rx1': self._rx1, 'rx2': self._rx2}
        for in_name, out_name, role in self._CHANNELS:
            cell = cell_by_role[role]
            wire(by_name[in_name].internal,    cell.ports['input'])
            wire(cell.ports['output'],         by_name[out_name].internal)

        # Same OUT-after-cell ordering trick as CD4017 / ISOW7841.
        in_pin_names  = {in_name for in_name, _, _ in self._CHANNELS}
        out_pin_names = {out_name for _, out_name, _ in self._CHANNELS}
        input_pins  = [p for p in pins if p.id.name in in_pin_names]
        output_pins = [p for p in pins if p.id.name in out_pin_names]
        other_pins  = [p for p in pins
                       if p.id.name not in in_pin_names
                       and p.id.name not in out_pin_names]
        self._ports_by_number = {pin.id.number: pin.external for pin in pins}
        self._port_map = PortMap(self._ports_by_number)
        Circuit.__init__(
            self,
            factor_nodes=input_pins + cells + output_pins + other_pins,
            ports=dict(self._port_map.items()),
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
        tin1: bool | None = None,
        tin2: bool | None = None,
        rin1: bool | None = None,
        rin2: bool | None = None,
    ) -> dict[str, bool | None]:
        """Standalone-test invocation: drive each logic / line input
        and read back the four channel outputs."""
        self._assert_no_inputs_wired()
        self._ports['TIN1'].drive(tin1)
        self._ports['TIN2'].drive(tin2)
        self._ports['RIN1'].drive(rin1)
        self._ports['RIN2'].drive(rin2)
        self.evaluate()
        return {
            'TOUT1': self._ports['TOUT1'].value,
            'TOUT2': self._ports['TOUT2'].value,
            'ROUT1': self._ports['ROUT1'].value,
            'ROUT2': self._ports['ROUT2'].value,
        }

    def __repr__(self) -> str:
        return f"TRS3122E(refdes={self.refdes!r})"
