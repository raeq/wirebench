from pydantic import validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Digital


class Buffer(FactorNode):
    """Single-bit digital passthrough cell.

    The cell's `output` mirrors `input` on each evaluate.  Same domain
    on both ports.  Used as a behavioural stand-in inside opaque
    level-translator chips (e.g. RS-232 line drivers / receivers)
    where the framework needs *something* to carry signal through the
    package even though the chip's silicon-level voltage translation
    is invisible at the digital logic layer.

    A None on the input port propagates as None on the output port —
    consistent with the framework's "undriven means None" convention,
    so a chip whose upstream net hasn't been driven yet stays
    undriven on the downstream side too.
    """

    __slots__ = ('_ports',)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._ports = {
            'input':  Port('input',  Direction.IN,  domain,
                           mandatory=False, signal_type=Digital),
            'output': Port('output', Direction.OUT, domain,
                           mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    def evaluate(self) -> None:
        v = self._ports['input'].value
        if v is None:
            self._ports['output'].drive(None)
        else:
            self._ports['output'].drive(bool(Digital(v)))

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, value: bool | None) -> bool | None:
        self._assert_no_inputs_wired()
        self._ports['input'].drive(value)
        self.evaluate()
        result: bool | None = self._ports['output'].value
        return result

    def __repr__(self) -> str:
        return f"Buffer(output={self._ports['output'].value!r})"
