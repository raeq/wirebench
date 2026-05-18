"""Shared registry walker — produces per-part descriptor dicts.

Consumed by the `wirebench parts` CLI subcommand (text + JSON output)
and by `scripts/render_parts_page.py` (Markdown doc-site page).  Lives
here, not in the framework, because it's a presentation-layer concern:
it parses docstrings, bins parts by base class, and exposes the
attributes downstream tooling cares about without prescribing any of
that to the framework itself.
"""
from __future__ import annotations

from typing import Any, TypedDict

# Trigger component registration so the registry is fully populated.
import components.chips        # noqa: F401
import components.connectors   # noqa: F401
import components.diodes       # noqa: F401
import components.passives     # noqa: F401
import components.relays       # noqa: F401
import components.transistors  # noqa: F401
import framework.board         # noqa: F401

from framework.board     import Board
from framework.chip      import Chip
from framework.connector import Connector
from framework.diode     import Diode
from framework.part      import Part
from framework.pin       import Pin
from framework.pin_function import PinFunction, infer_pin_function
from framework.registry  import _REGISTRY
from framework.transistor import BJT, MOSFET

from components.passives.capacitor import Capacitor
from components.passives.cell      import Cell
from components.passives.inductor  import Inductor
from components.passives.led       import LED
from components.passives.rail      import Rail
from components.passives.resistor  import Resistor


KIND_BY_BASE: list[tuple[type, str]] = [
    # Order matters: Chip is a Circuit too, so check it before any
    # broader bases.  Likewise Board is a Circuit; classified here as
    # 'board' so the catalogue tells users a Board is something they
    # subclass, not a part they place.
    (Board, 'board'),
    (Chip, 'chip'),
    (Connector, 'connector'),
    (BJT, 'transistor'),
    (MOSFET, 'transistor'),
    (Diode, 'diode'),
    (Resistor, 'passive'),
    (Capacitor, 'passive'),
    (Inductor, 'passive'),
    (LED, 'passive'),
    (Rail, 'passive'),
    (Cell, 'passive'),
]


class PartDescriptor(TypedDict):
    class_name:           str
    module:               str
    refdes_prefix:        str | None
    kind:                 str
    description:          str
    footprint:            str | None
    pin_count:            int | None
    pin_functions:        dict[str, str | None] | None
    has_behavioural_cell: bool
    datasheet:            str | None


def _kind_of(cls: type) -> str:
    for base, label in KIND_BY_BASE:
        if issubclass(cls, base):
            return label
    # Concept cells (Inverter, NORLatch, …) are registered Parts that
    # aren't placeable parts in their own right — they're framework-
    # internal cells exposed through the registry only because the
    # save/load format needs to round-trip them.  Classify them so the
    # catalogue can show them as a separate row without misleading
    # users into thinking they're procurable.
    return 'cell'


def _description_of(cls: type) -> str:
    doc = cls.__doc__
    if not doc:
        return cls.__name__
    for line in doc.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return cls.__name__


def _pin_count_of(cls: type) -> int | None:
    pin_count = getattr(cls, 'PIN_COUNT', None)
    if isinstance(pin_count, int):
        return pin_count
    pinout = getattr(cls, 'PINOUT', None)
    if isinstance(pinout, tuple):
        return len(pinout)
    pin_table = getattr(cls, '_PIN_TABLE', None)
    if isinstance(pin_table, tuple):
        return len(pin_table)
    return None


def _pin_functions_of(cls: type) -> dict[str, str | None] | None:
    """For Chips: every package pin's effective function — the
    `PIN_FUNCTIONS` override map merged with the name-inferred default
    for each declared pin.  For non-chips: None (passives, connectors,
    rails don't carry pin-function metadata)."""
    if not issubclass(cls, Chip):
        return None
    overrides = getattr(cls, 'PIN_FUNCTIONS', {}) or {}
    pin_table = getattr(cls, '_PIN_TABLE', None)
    if not isinstance(pin_table, tuple):
        return dict(_stringify_pin_functions(overrides)) or None
    out: dict[str, str | None] = {}
    for row in pin_table:
        # Each row's first two fields are (pin_number, pin_name).
        if len(row) < 2:
            continue
        name = row[1]
        if name in overrides:
            fn = overrides[name]
        else:
            fn = infer_pin_function(name)
        out[name] = fn.value if isinstance(fn, PinFunction) else None
    return out


def _stringify_pin_functions(
    mapping: dict[str, PinFunction | None],
) -> dict[str, str | None]:
    return {
        name: (fn.value if isinstance(fn, PinFunction) else None)
        for name, fn in mapping.items()
    }


def _has_behavioural_cell(cls: type) -> bool:
    """A chip is behavioural if it has at least one cell that drives an
    OUT pin internally — i.e. the chip's `__init__` instantiates a
    cell.  The framework already enforces this invariant at
    construction (`_assert_every_out_pin_is_internally_driven`), so the
    test is structural: does the class subclass Chip AND have a non-
    empty `cells` argument path?

    Without instantiating, we can't directly observe what the chip
    constructor passes for `cells`.  Use a lighter proxy: assume any
    Chip subclass with a non-default `__init__` (i.e. not directly
    inheriting Chip.__init__) instantiates cells.  False positives are
    benign — the field reads as 'this chip models behaviour' rather
    than 'this chip's pins are externally driven only'.
    """
    if not issubclass(cls, Chip):
        return False
    # Bare-firmware-driven chips (ATmega328P et al.) explicitly opt out
    # of the cell requirement; report them as non-behavioural in the
    # structural sense the catalogue cares about.
    if getattr(cls, 'BARE_FIRMWARE_DRIVEN', False):
        return False
    # The Chip base provides a no-op `__init__` only in its abstract
    # form; every concrete chip overrides.  Use that as the signal.
    return cls.__init__ is not Chip.__init__


def _refdes_prefix_of(cls: type) -> str | None:
    prefix = getattr(cls, 'REFDES_PREFIX', None)
    if isinstance(prefix, str) and prefix:
        return prefix
    return None


def _footprint_of(cls: type) -> str | None:
    """Footprint at the class level only.  `Part.FOOTPRINT` is
    declared as an instance `@property` that returns None by default;
    fixed-geometry subclasses override it as a `ClassVar[str | None]`
    literal which we can read straight off the class.  Parameterised
    parts (connector families) override it as another @property whose
    value depends on instance state — those land here as None, which
    the catalogue page can render as 'various'."""
    value = cls.__dict__.get('FOOTPRINT')
    if isinstance(value, str) or value is None:
        return value
    # @property descriptors, methods, etc. — no class-level constant.
    return None


def descriptor_for(cls: type) -> PartDescriptor:
    return PartDescriptor(
        class_name=cls.__name__,
        module=cls.__module__,
        refdes_prefix=_refdes_prefix_of(cls),
        kind=_kind_of(cls),
        description=_description_of(cls),
        footprint=_footprint_of(cls),
        pin_count=_pin_count_of(cls),
        pin_functions=_pin_functions_of(cls),
        has_behavioural_cell=_has_behavioural_cell(cls),
        datasheet=getattr(cls, 'DATASHEET', None),
    )


def all_parts() -> list[PartDescriptor]:
    """Every registered part, sorted by class name for determinism."""
    return [descriptor_for(_REGISTRY[name]) for name in sorted(_REGISTRY)]


# --------------------------------------------------------------- filters


def filter_parts(
    parts: list[PartDescriptor],
    *,
    prefix: str | None = None,
    kind: str | None = None,
    has_cell: bool = False,
    has_footprint: bool = False,
    pin_function: str | None = None,
) -> list[PartDescriptor]:
    """Apply filters in AND composition; return the surviving rows."""
    out = list(parts)
    if prefix is not None:
        out = [p for p in out if p['refdes_prefix'] == prefix]
    if kind is not None:
        out = [p for p in out if p['kind'] == kind]
    if has_cell:
        out = [p for p in out if p['has_behavioural_cell']]
    if has_footprint:
        out = [p for p in out if p['footprint']]
    if pin_function is not None:
        wanted = pin_function.lower()
        out = [
            p for p in out
            if p['pin_functions']
            and any(
                (f or '').lower() == wanted for f in p['pin_functions'].values()
            )
        ]
    return out


KNOWN_KINDS: tuple[str, ...] = (
    'board', 'chip', 'connector', 'diode', 'transistor',
    'passive', 'relay', 'cell',
)
