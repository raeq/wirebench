from typing import ClassVar, Sequence

from pydantic import validate_call

from framework.errors import PartParameterError
from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.registry import register
from framework.signals import Digital


@register('DiodeOR')
class DiodeOR(Part):
    """Diode-OR matrix cell: out HIGH whenever any of its inputs is HIGH.

    Models the behaviour of a network of signal diodes whose anodes
    are tied to a set of source nodes and whose cathodes are commoned
    to drive a single load.  Each diode passes a HIGH on its anode
    through to the cathode; the load is HIGH whenever *any* source is
    HIGH.  Real diodes have a forward drop (~0.7 V for a 1N4148) and
    block reverse current — those properties make the wired-OR
    topology safe — but only the boolean OR behaviour matters in a
    logic-level graph.

    Companion to physical `Diode` parts on the netlist: the diodes are
    listed in the BOM and wired between source and load nodes, but
    they are opaque under graph evaluation.  This cell is what
    actually propagates the OR'd signal.
    """

    __slots__ = ('_ports', '_input_names')

    SERIALIZE_KWARGS: ClassVar[tuple[str, ...]] = ('input_names',)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        input_names: Sequence[str],
        domain: GroundDomain = ELECTRICAL,
    ) -> None:
        if len(input_names) < 1:
            raise PartParameterError("DiodeOR needs at least one input name")
        if len(set(input_names)) != len(input_names):
            raise PartParameterError(
                f"DiodeOR input names must be unique: {list(input_names)!r}"
            )
        if 'out' in input_names:
            raise PartParameterError("'out' is reserved for the output port")
        self._input_names = tuple(input_names)
        self._ports: dict[str, Port] = {
            name: Port(name, Direction.IN, domain,
                       mandatory=False, signal_type=Digital)
            for name in self._input_names
        }
        self._ports['out'] = Port('out', Direction.OUT, domain,
                                  mandatory=False, signal_type=Digital)

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def input_names(self) -> tuple[str, ...]:
        return self._input_names

    def evaluate(self) -> None:
        # bool(Digital(...)) canonicalises None → False and matches the
        # framework's standard cast for reading IN ports as booleans.
        result = any(bool(Digital(self._ports[n].value))
                     for n in self._input_names)
        self._ports['out'].drive(result)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, **kwargs: bool | None) -> bool:
        self._assert_no_inputs_wired()
        unknown = set(kwargs) - set(self._input_names)
        if unknown:
            raise PartParameterError(
                f"DiodeOR.__call__ got unknown input(s) {sorted(unknown)!r}; "
                f"expected one of {list(self._input_names)!r}"
            )
        for name in self._input_names:
            self._ports[name].drive(kwargs.get(name, False))
        self.evaluate()
        return bool(self._ports['out'].value)

    def __repr__(self) -> str:
        return f"DiodeOR(inputs={list(self._input_names)!r}, out={self._ports['out'].value!r})"
