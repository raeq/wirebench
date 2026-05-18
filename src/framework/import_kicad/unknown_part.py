"""`UnknownPart` — the placeholder chip class for KiCad parts that
don't resolve to a known wirebench class.

The import path defaults to *non-strict*: instead of refusing the
whole netlist when one unmapped part appears, we substitute an
`UnknownPart` whose pin count and pin names mirror what the netlist
declared.  The resulting circuit constructs cleanly and participates
in logical-net walking; users discover which parts need a wirebench-
side class and fill them in as a follow-up.

`BARE_FIRMWARE_DRIVEN = True` opts the placeholder out of the
construction-time "every OUT pin needs an internal driver" invariant
— there's no way to know from the netlist whether a pin is meant to
drive or just expose a signal, and we don't want a partial import to
fail before the user can inspect it.
"""
from __future__ import annotations

from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import ELECTRICAL, GroundDomain
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Digital


def make_unknown_part_class(
    name: str,
    pin_specs: list[tuple[int, str]],
    *,
    refdes_prefix: str = 'U',
    footprint: str | None = None,
) -> type[Chip]:
    """Synthesise an `UnknownPart`-style Chip subclass.

    Each call produces a fresh class so two different KiCad parts
    that both fall back to UnknownPart don't share their pin maps.
    The class is registered into wirebench's part registry under the
    given `name` so save/load round-trips work the same way they do
    for catalogue parts.

    `pin_specs` is the list of `(pin_number, pin_name)` pairs the
    netlist declared.  Direction defaults to BIDIR because the
    netlist doesn't constrain it.
    """
    safe_pin_specs = tuple(pin_specs)
    class_footprint = footprint

    class UnknownPart(Chip):
        __slots__ = ('_refdes_number',)
        REFDES_PREFIX: ClassVar[str] = refdes_prefix
        FOOTPRINT:     ClassVar[str | None] = class_footprint
        BARE_FIRMWARE_DRIVEN: ClassVar[bool] = True
        IMPORTED_FROM_KICAD: ClassVar[bool] = True

        @validate_call(config={'arbitrary_types_allowed': True})
        def __init__(self, *, refdes_number: RefdesNumber) -> None:
            validate_refdes(self.REFDES_PREFIX, refdes_number)
            self._refdes_number = refdes_number
            pins = [
                Pin(
                    PinId(number=number, name=pin_name),
                    direction=Direction.BIDIR,
                    domain=ELECTRICAL,
                    mandatory=False,
                    signal_type=Digital,
                )
                for number, pin_name in safe_pin_specs
            ]
            super().__init__(pins=pins, cells=[])

        @property
        def refdes(self) -> str:
            return f"{self.REFDES_PREFIX}{self._refdes_number}"

        @property
        def refdes_number(self) -> int:
            return self._refdes_number

        def __call__(self) -> None:  # pragma: no cover — placeholder
            self._assert_no_inputs_wired()

    UnknownPart.__name__ = name
    UnknownPart.__qualname__ = name
    return UnknownPart
