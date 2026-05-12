from typing import Annotated

from pydantic import Field, validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog, Digital


class FanController(FactorNode):
    """Hysteretic temperature-switch + fan-driver cell.

    Models the macroscopic behaviour of a TMP302-style temperature
    switch driving a MOSFET-gated fan: at rest the fan is off, but
    when the sensed temperature crosses the upper trip point the fan
    turns on and stays on until the temperature falls below the
    lower trip point.  The Python attribute `_temperature_c` carries
    the sensed temperature; the cell's evaluate() applies the
    hysteresis rule and drives `fan_drive` HIGH while the fan should
    be running.

    Ports
    -----
        temperature_in  Analog  IN  — optional wire-driven sensed temp.
                       If left undriven, the cell uses `_temperature_c`
                       (set externally by the wrapping board).
        fan_drive       Digital OUT — HIGH while the fan is on.

    The trip thresholds default to the TIDA-00517 numbers
    (60 °C upper, 50 °C lower).  Trip-points and hysteresis are
    configurable so the cell can be reused for designs with other
    TMP302 variants or different MOSFET drivers.
    """

    __slots__ = ('_ports', '_trip_high_c', '_trip_low_c',
                 '_temperature_c', '_fan_on')

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        *,
        trip_high_c: Annotated[float, Field(gt=-273.15)] = 60.0,
        trip_low_c:  Annotated[float, Field(gt=-273.15)] = 50.0,
        domain: GroundDomain = ELECTRICAL,
    ) -> None:
        if trip_low_c >= trip_high_c:
            raise ValueError(
                f"trip_low_c ({trip_low_c}) must be below trip_high_c "
                f"({trip_high_c}) so the hysteresis window has a real width"
            )
        self._trip_high_c: float = float(trip_high_c)
        self._trip_low_c:  float = float(trip_low_c)
        # Power-on state: fan off, ambient temperature unknown (use
        # 0 °C as a safe starting point — well below any reasonable
        # over-temperature trip).
        self._temperature_c: float = 0.0
        self._fan_on:        bool  = False
        self._ports = {
            'temperature_in': Port('temperature_in', Direction.IN,  domain,
                                   mandatory=False, signal_type=Analog),
            'fan_drive':      Port('fan_drive',      Direction.OUT, domain,
                                   mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def trip_high_c(self) -> float:
        return self._trip_high_c

    @property
    def trip_low_c(self) -> float:
        return self._trip_low_c

    @property
    def temperature_c(self) -> float:
        return self._temperature_c

    @property
    def fan_on(self) -> bool:
        return self._fan_on

    def evaluate(self) -> None:
        # Prefer a wired temperature signal if present; otherwise use
        # the Python-level attribute the wrapping board sets each tick.
        wired = self._ports['temperature_in'].value
        temp = float(wired) if wired is not None else self._temperature_c

        # Hysteresis: cross UP to turn on, cross DOWN to turn off; the
        # zone between the two trip points holds the previous state.
        if temp >= self._trip_high_c:
            self._fan_on = True
        elif temp <= self._trip_low_c:
            self._fan_on = False
        # else: in the deadband, keep self._fan_on unchanged.

        self._ports['fan_drive'].drive(self._fan_on)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, temperature_c: float) -> bool:
        """Standalone-test invocation: set the ambient temperature,
        evaluate, and return the resulting fan state."""
        self._assert_no_inputs_wired()
        self._temperature_c = float(temperature_c)
        self.evaluate()
        return self._fan_on

    def __repr__(self) -> str:
        return (f"FanController(trip_high_c={self._trip_high_c!r}, "
                f"trip_low_c={self._trip_low_c!r}, "
                f"temperature_c={self._temperature_c!r}, "
                f"fan_on={self._fan_on!r})")
