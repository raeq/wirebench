"""Analog temperature-sensor cell — drives a single voltage output
proportional to a user-set temperature.

Used by linear analog temperature sensors like the TMP36, where the
output voltage is a simple affine function of the measured
temperature.  The user prescribes the temperature via the
`temperature_c` setter; the cell drives the output accordingly.
"""
from __future__ import annotations

from pydantic import validate_call

from framework.errors import PartParameterError
from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog


class AnalogTempSensor(FactorNode):
    """Linear analog temperature sensor (TMP36-style).

    Ports
    -----
    v_out  (OUT, Analog) — output voltage = (T_c × scale) + offset

    Construction takes `scale` (V/°C; default 0.01 = 10 mV/°C for
    the TMP36) and `offset` (V at 0 °C; default 0.5 V for the TMP36
    so the sensor reads correctly down to -50 °C without a negative
    supply).  Temperature is prescribed via the `temperature_c`
    setter on the cell — typical use is a parent demo writing it
    per scenario.
    """

    __slots__ = ('_ports', '_scale', '_offset', '_temperature_c')

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        scale: float = 0.01,
        offset: float = 0.5,
        initial_temperature_c: float = 25.0,
        domain: GroundDomain = ELECTRICAL,
    ) -> None:
        self._scale = float(scale)
        self._offset = float(offset)
        self._temperature_c = float(initial_temperature_c)
        self._ports = {
            'v_out': Port('v_out', Direction.OUT, domain,
                          mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def temperature_c(self) -> float:
        return self._temperature_c

    @temperature_c.setter
    def temperature_c(self, value: float) -> None:
        if not -100.0 <= value <= 200.0:
            raise PartParameterError(
                f"temperature_c must be in [-100, 200] °C; got {value!r}"
            )
        self._temperature_c = float(value)

    @property
    def output_voltage(self) -> float:
        return self._offset + self._temperature_c * self._scale

    def evaluate(self) -> None:
        self._ports['v_out'].drive(self.output_voltage)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, temperature_c: float | None = None) -> float:
        self._assert_no_inputs_wired()
        if temperature_c is not None:
            self.temperature_c = temperature_c
        self.evaluate()
        return self.output_voltage

    def __repr__(self) -> str:
        return (f"AnalogTempSensor(T={self._temperature_c}°C, "
                f"V_out={self.output_voltage:.3f})")
