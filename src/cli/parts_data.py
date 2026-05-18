"""Shared registry walker — produces per-part descriptor dicts.

Consumed by the `wirebench parts` CLI subcommand (text + JSON output)
and by `scripts/render_parts_page.py` (Markdown doc-site page).  Lives
here, not in the framework, because it's a presentation-layer concern:
it parses docstrings, bins parts by base class, and exposes the
attributes downstream tooling cares about without prescribing any of
that to the framework itself.
"""
from __future__ import annotations

import inspect
import re
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
from components.relays.spdt        import Relay_SPDT


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
    (Relay_SPDT, 'relay'),
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
    """Join the docstring's first paragraph into a single one-line
    summary.  Python's `inspect.cleandoc` strips leading whitespace,
    after which we collapse the contiguous run of non-blank lines into
    one space-separated string — handles wrapped one-sentence
    summaries like BQ27546-G1's two-line opening verbatim."""
    doc = cls.__doc__
    if not doc:
        return cls.__name__
    cleaned = inspect.cleandoc(doc)
    paragraph_lines: list[str] = []
    for line in cleaned.splitlines():
        stripped = line.strip()
        if not stripped:
            break
        paragraph_lines.append(stripped)
    if not paragraph_lines:
        return cls.__name__
    return ' '.join(paragraph_lines)


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


_EMPTY_CELLS_PATTERN = re.compile(r"cells\s*=\s*(?:\[\s*\]|\(\s*\))")


def _has_behavioural_cell(cls: type) -> bool:
    """A chip is behavioural if its `__init__` instantiates cells —
    i.e. the chip models internal logic rather than just declaring
    a pin map.

    Detection: read the chip's `__init__` source and look for an
    explicit `cells=[]` or `cells=()` literal at the `super().__init__`
    call site.  Black-box sensor chips (BMP280, AM2302, …) and bare-
    firmware-driven MCUs (ATmega328P, …) use this pattern; their
    actual behaviour is supplied by the test scenario or a subclass.
    Anything else — every chip with named cell instances — counts as
    behavioural for the catalogue's purposes.
    """
    if not issubclass(cls, Chip) or cls is Chip:
        return False
    if getattr(cls, 'BARE_FIRMWARE_DRIVEN', False):
        return False
    try:
        source = inspect.getsource(cls.__init__)
    except (OSError, TypeError):
        # Inherited __init__ (rare for chips) means no own
        # implementation — treat as not behavioural.
        return False
    if _EMPTY_CELLS_PATTERN.search(source):
        return False
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
