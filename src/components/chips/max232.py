from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital
from framework.wire import wire
from .concepts.rs232_driver import RS232Driver
from .concepts.constant_voltage import ConstantVoltage


@register('MAX232')
class MAX232(Chip):
    """Texas Instruments MAX232 — dual RS-232 driver/receiver with charge-pump (DIP-16).

    Composes two `RS232Driver` cells (one per TX/RX channel pair)
    plus two `ConstantVoltage` cells for the V_POS (+10 V) and
    V_NEG (-10 V) charge-pump rails.  Charge-pump capacitor pins
    (C1_POS, C1_NEG, C2_POS, C2_NEG) stay passive in the framework
    model — they're external-cap connection points and need no
    internal driver.

    TTL-side ports are Digital; RS-232-side ports are Analog with
    ±9 V swing modelled by the cell.
    """

    __slots__ = ('_refdes_number', '_ch1', '_ch2', '_vpos_drv', '_vneg_drv')

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-16_W7.62mm"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1,  'C1_POS',   Direction.IN,  Analog),
        (2,  'V_POS',    Direction.OUT, Analog),
        (3,  'C1_NEG',   Direction.IN,  Analog),
        (4,  'C2_POS',   Direction.IN,  Analog),
        (5,  'C2_NEG',   Direction.IN,  Analog),
        (6,  'V_NEG',    Direction.OUT, Analog),
        (7,  'T2OUT', Direction.OUT, Analog),
        (8,  'R2IN',  Direction.IN,  Analog),
        (9,  'R2OUT', Direction.OUT, Digital),
        (10, 'T2IN',  Direction.IN,  Digital),
        (11, 'T1IN',  Direction.IN,  Digital),
        (12, 'R1OUT', Direction.OUT, Digital),
        (13, 'R1IN',  Direction.IN,  Analog),
        (14, 'T1OUT', Direction.OUT, Analog),
        (15, 'GND',   Direction.IN,  Analog),
        (16, 'VCC',   Direction.IN,  Analog),
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        pins = [
            Pin(PinId(number, name), direction, domain,
                mandatory=False, signal_type=signal_type)
            for number, name, direction, signal_type in self._PIN_TABLE
        ]
        self._ch1 = RS232Driver(domain)
        self._ch2 = RS232Driver(domain)
        self._vpos_drv = ConstantVoltage(+10.0, domain)
        self._vneg_drv = ConstantVoltage(-10.0, domain)
        by_name = {pin.id.name: pin for pin in pins}
        # Channel 1
        wire(by_name['T1IN'].internal,  self._ch1.ports['tx_in'])
        wire(self._ch1.ports['tx_out'], by_name['T1OUT'].internal)
        wire(by_name['R1IN'].internal,  self._ch1.ports['rx_in'])
        wire(self._ch1.ports['rx_out'], by_name['R1OUT'].internal)
        # Channel 2
        wire(by_name['T2IN'].internal,  self._ch2.ports['tx_in'])
        wire(self._ch2.ports['tx_out'], by_name['T2OUT'].internal)
        wire(by_name['R2IN'].internal,  self._ch2.ports['rx_in'])
        wire(self._ch2.ports['rx_out'], by_name['R2OUT'].internal)
        # Charge-pump rails
        wire(self._vpos_drv.ports['out'], by_name['V_POS'].internal)
        wire(self._vneg_drv.ports['out'], by_name['V_NEG'].internal)
        super().__init__(pins=pins, cells=[
            self._ch1, self._ch2, self._vpos_drv, self._vneg_drv,
        ])

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> None:
        """Black-box package — no behavioural model. Pin states are
        observable via `chip.ports['<name>'].value`. For analog or
        timing-accurate behaviour, simulate the .SUBCKT in SPICE."""
        return None

    def __repr__(self) -> str:
        return f"MAX232(refdes={self.refdes!r})"
