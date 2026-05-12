from typing import Annotated

from pydantic import Field, validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Digital


class Monostable(FactorNode):
    """LM555-style monostable-timer cell.

    A real 555 in monostable mode triggers on TRIG going below 1/3 Vcc
    (active-LOW pulse), drives OUT HIGH for `1.1 × R × C` seconds, then
    returns LOW.  Pin 4 (RESET) is active-LOW too: holding it low
    forces OUT LOW and inhibits further triggering.

    This cell models the same logical behaviour in a discrete-time
    voltage-only graph:

        trig    Digital IN  — falling edge fires the timer (idle HIGH).
        reset   Digital IN  — LOW asserts reset and clamps OUT LOW.
                              HIGH or undriven is normal operation.
        out     Digital OUT — HIGH while the pulse is in progress.

    The pulse duration is configured at construction; the surrounding
    circuit advances time by writing `_remaining_ms` directly before
    calling evaluate() — same Python-level escape hatch the thermometer
    demo uses for its firmware-model cell.
    """

    __slots__ = ('_ports', '_duration_ms', '_remaining_ms', '_prev_trig')

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        duration_ms: Annotated[float, Field(gt=0)],
        domain: GroundDomain = ELECTRICAL,
    ) -> None:
        self._duration_ms: float = float(duration_ms)
        self._remaining_ms: float = 0.0
        # `None` until the first evaluate sees the trigger line; this
        # blocks spurious edges at power-on regardless of whether the
        # trigger source starts HIGH or LOW.
        self._prev_trig: bool | None = None
        self._ports = {
            'trig':  Port('trig',  Direction.IN,  domain, mandatory=False, signal_type=Digital),
            'reset': Port('reset', Direction.IN,  domain, mandatory=False, signal_type=Digital),
            'out':   Port('out',   Direction.OUT, domain, mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def duration_ms(self) -> float:
        return self._duration_ms

    @property
    def remaining_ms(self) -> float:
        return self._remaining_ms

    @property
    def running(self) -> bool:
        return self._remaining_ms > 0.0

    def evaluate(self) -> None:
        trig = bool(Digital(self._ports['trig'].value))
        # Reset is active-LOW: explicit False asserts; HIGH or
        # undriven (None) is the normal-operation case.  Mirrors a
        # real 555 whose pin 4 sits HIGH via an internal pull-up
        # unless something actively grounds it.
        reset_asserted = self._ports['reset'].value is False

        if reset_asserted:
            self._remaining_ms = 0.0
            self._prev_trig = trig
            self._ports['out'].drive(False)
            return

        # Falling-edge trigger, only when idle — a second press during
        # the pulse is ignored, matching the LM555 datasheet.
        if (self._prev_trig is True and trig is False
                and self._remaining_ms <= 0.0):
            self._remaining_ms = self._duration_ms
        self._prev_trig = trig
        self._ports['out'].drive(self._remaining_ms > 0.0)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, trig: bool | None = True,
                 reset: bool | None = True) -> bool:
        """Standalone-test invocation: drive trig/reset, evaluate, and
        return the output level.  Time does not advance in this path;
        set `_remaining_ms` directly between calls to walk the pulse."""
        self._assert_no_inputs_wired()
        self._ports['trig'].drive(trig)
        self._ports['reset'].drive(reset)
        self.evaluate()
        return bool(self._ports['out'].value)

    def __repr__(self) -> str:
        return (f"Monostable(duration_ms={self._duration_ms!r}, "
                f"remaining_ms={self._remaining_ms!r})")
