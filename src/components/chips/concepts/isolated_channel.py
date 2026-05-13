from pydantic import validate_call

from framework.errors import PartConfigurationError
from framework.part import Part
from framework.ground import GroundDomain
from framework.port import Port, Direction
from framework.signals import Digital


class IsolatedChannel(Part):
    """Single-bit digital crossing of a galvanic isolation barrier.

    The cell's `input` port lives in one `GroundDomain`; its `output`
    port lives in a different `GroundDomain`.  On evaluate(), the
    cell mirrors input to output — same digital level — but the two
    ports are on physically distinct nets because they're in
    different ground domains and the framework's `wire()` refuses to
    connect ports across domains.

    Used inside digital-isolator chips (the ISOW784x family, the
    ISO7xxx family, etc.) where the package's transformer or
    capacitive barrier carries one logical bit between two electrical
    circuits whose grounds are separately referenced.  The cell does
    the boundary crossing the framework can't otherwise express,
    while still letting each side's wires obey the same-domain rule.
    """

    __slots__ = ('_ports', '_input_domain', '_output_domain')

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        input_domain: GroundDomain,
        output_domain: GroundDomain,
    ) -> None:
        if input_domain is output_domain:
            raise PartConfigurationError(
                f"IsolatedChannel needs two *distinct* ground domains; "
                f"both sides are in {input_domain.name!r} — use "
                f"components.chips.concepts.buffer.Buffer for a "
                f"same-domain passthrough."
            )
        self._input_domain  = input_domain
        self._output_domain = output_domain
        self._ports = {
            'input':  Port('input',  Direction.IN,  input_domain,
                           mandatory=False, signal_type=Digital),
            'output': Port('output', Direction.OUT, output_domain,
                           mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def input_domain(self) -> GroundDomain:
        return self._input_domain

    @property
    def output_domain(self) -> GroundDomain:
        return self._output_domain

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
        return (f"IsolatedChannel({self._input_domain.name!r} → "
                f"{self._output_domain.name!r}, "
                f"output={self._ports['output'].value!r})")
