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
from .concepts.fuel_gauge import FuelGauge


@register('BQ27546G1')
class BQ27546G1(Chip):
    """Texas Instruments BQ27546-G1 — single-cell Li-Ion fuel gauge for
    pack-side integration (15-ball DSBGA, 2.61 × 1.96 mm).

    Reads the cell voltage on BAT, estimates state-of-charge with the
    patented Impedance Track™ algorithm by integrating coulombs across
    a 5-20 mΩ sense resistor between SRP/SRN, and reports the result
    over either I²C (SDA/SCL, slave) or HDQ (single-wire, slave) to a
    host MCU.  An NTC thermistor on TS lets the gauge correct for cell
    temperature; SE is a push-pull shutdown-enable output that goes
    LOW when the cell is too depleted to safely keep the system
    running.

    The chip is modelled here with one internal `FuelGauge` cell.  The
    framework's voltage-only graph can't run Impedance Track —
    coulomb-counting needs current and time, and the bus protocols
    (I²C, HDQ) need clocked transactions — so the cell falls back to
    the steady-state OCV-curve inverse the real silicon uses at
    power-on.  SDA / SCL / HDQ are still present as BIDIR Digital
    pins so the schematic-level pinout matches the datasheet; their
    *protocol* behaviour is out of scope.  The SoC estimate is
    exposed through the chip's `state_of_charge` property — the
    stand-in for "what bqStudio would print over I²C."

    Reference: SLUSC53B (datasheet, rev B, May 2018).
    """

    __slots__ = ('_gauge', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = (
        "Package_BGA:Texas_S-PVQFN-N15_2.61x1.96mm_DSBGA"
    )

    # Pin table per the BQ27546-G1 datasheet's Pin Functions section.
    # The pin "number" here is a 1-based ordinal that mirrors the
    # datasheet's row order; the actual silicon uses BGA coordinates
    # (A1..E3).  Number -> coordinate mapping is documented inline so
    # downstream layout tooling can recover the BGA position.
    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        ( 1, 'SRP',   Direction.IN,    Analog),    # A1  coulomb-counter (CELL- side)
        ( 2, 'HDQ',   Direction.BIDIR, Digital),   # A2  HDQ serial (open-drain)
        ( 3, 'SCL',   Direction.IN,    Digital),   # A3  I²C clock in
        ( 4, 'SRN',   Direction.IN,    Analog),    # B1  coulomb-counter (PACK- side)
        ( 5, 'TS',    Direction.IN,    Analog),    # B2  thermistor sense
        ( 6, 'SDA',   Direction.BIDIR, Digital),   # B3  I²C data (open-drain)
        ( 7, 'VSS',   Direction.IN,    Analog),    # C1  ground
        ( 8, 'VSS',   Direction.IN,    Analog),    # C2  ground
        ( 9, 'SE',    Direction.OUT,   Digital),   # C3  shutdown-enable (push-pull)
        (10, 'VCC',   Direction.OUT,   Analog),    # D1  regulator output / core supply
        (11, 'CE',    Direction.IN,    Digital),   # D2  chip enable (LDO disconnect when low)
        (12, 'NC1',   Direction.IN,    Digital),   # D3  reserved — do not connect
        (13, 'REGIN', Direction.IN,    Analog),    # E1  regulator input
        (14, 'BAT',   Direction.IN,    Analog),    # E2  cell-voltage sense
        (15, 'NC2',   Direction.IN,    Digital),   # E3  reserved — do not connect
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        domain: GroundDomain = ELECTRICAL,
        *,
        refdes_number: RefdesNumber,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number

        pins = [
            Pin(PinId(number, name), direction, domain,
                mandatory=False, signal_type=signal_type)
            for number, name, direction, signal_type in self._PIN_TABLE
        ]
        by_name: dict[str, Pin] = {}
        for p in pins:
            # VSS appears twice; keep the first occurrence — both pins
            # land on the same ground net at the board level anyway.
            by_name.setdefault(p.id.name, p)

        self._gauge = FuelGauge(domain=domain)

        # Wire the internal cell to the four analog inputs it actually
        # reads (BAT, TS, SRP, SRN) and the one digital output it
        # actually drives (SE).
        wire(by_name['BAT'].internal, self._gauge.ports['bat'])
        wire(by_name['TS' ].internal, self._gauge.ports['ts'])
        wire(by_name['SRP'].internal, self._gauge.ports['srp'])
        wire(by_name['SRN'].internal, self._gauge.ports['srn'])
        wire(self._gauge.ports['se'],      by_name['SE' ].internal)
        wire(self._gauge.ports['vcc_out'], by_name['VCC'].internal)

        # IN pins first, then the cell, then the OUT pin, then the
        # rest — same dataflow ordering trick CD4017 / ISOW7841 use to
        # give the topological sort a clean dataflow to walk.
        input_pin_names  = {'BAT', 'TS', 'SRP', 'SRN'}
        output_pin_names = {'SE', 'VCC'}
        input_pins  = [p for p in pins if p.id.name in input_pin_names]
        output_pins = [p for p in pins if p.id.name in output_pin_names]
        other_pins  = [p for p in pins
                       if p.id.name not in input_pin_names
                       and p.id.name not in output_pin_names]
        self._ports_by_number = {pin.id.number: pin.external for pin in pins}
        self._port_map = PortMap(self._ports_by_number)
        Circuit.__init__(
            self,
            factor_nodes=input_pins + [self._gauge] + output_pins + other_pins,
            ports=dict(self._port_map.items()),
        )

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @property
    def state_of_charge(self) -> float:
        """Most-recent SoC estimate (0..1) — stand-in for the value a
        host MCU would read from the gauge over I²C / HDQ."""
        return self._gauge.state_of_charge

    @property
    def shutdown_threshold(self) -> float:
        return self._gauge.shutdown_threshold

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(
        self,
        v_bat: float | None = None,
    ) -> dict[str, float | bool | None]:
        """Standalone-test invocation: drive BAT, evaluate the
        internal fuel gauge, and read back SoC and SE pin."""
        self._assert_no_inputs_wired()
        self._ports['BAT'].drive(v_bat)
        self.evaluate()
        return {
            'state_of_charge': self.state_of_charge,
            'SE':              self._ports['SE'].value,
        }

    def __repr__(self) -> str:
        return f"BQ27546G1(refdes={self.refdes!r})"
