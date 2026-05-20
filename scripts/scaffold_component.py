#!/usr/bin/env python3
"""Scaffold a new wirebench component class + matching test stub.

The framework's contributor-side discipline (`__slots__`, every
required ClassVar, callable interface, port shape, registry
decorator, refdes validation) is mechanical — and getting it right
from memory is the on-ramp friction the *strictness as adoption
friction* feedback named.  This script machine-applies that
boilerplate.  The contributor then fills in:

- The pin-specific port logic that the framework can't infer.
- The teaching strings (`VERIFY`, `GOTCHAS`) that need human
  judgement.
- Any cell composition for chips with OUT pins.

Usage:

    uv run scripts/scaffold_component.py \\
        --name MyPart \\
        --kind passive \\
        --refdes-prefix R \\
        --footprint "Resistor_SMD:R_0603_1608Metric" \\
        --pins "t1:bidir:Analog,t2:bidir:Analog" \\
        --description "My example passive"

Supported `--kind` values: `passive`, `chip`.  Other framework
component families (connector, diode, transistor, relay, transducer)
inherit through dedicated base classes whose shapes are too varied to
template usefully — for those, copy an existing example
(`src/components/connectors/*.py`, `src/components/diodes/*.py`, etc.)
and adapt.  The discipline checks in this script apply equally to
hand-written components.

The scaffold writes to `src/components/<kind>s/<snake_name>.py` and
`tests/components/test_<snake_name>.py` by default; pass
`--output-root <path>` to redirect (used by the contributor test
suite).
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------------- types


@dataclass(frozen=True)
class PinSpec:
    name: str
    direction: str  # 'in' / 'out' / 'bidir'
    signal_type: str  # 'Analog' / 'Digital'


@dataclass(frozen=True)
class ComponentSpec:
    class_name: str
    kind: str  # 'passive' | 'chip'
    refdes_prefix: str
    footprint: str
    pins: tuple[PinSpec, ...]
    description: str


# --------------------------------------------------------- parsing


_DIRECTIONS = {'in', 'out', 'bidir'}
_SIGNAL_TYPES = {'Analog', 'Digital'}
_KINDS = {'passive', 'chip'}


def _snake_case(name: str) -> str:
    """CamelCase → snake_case with acronym-aware splits.

    Splits happen at:
      - `XYZSomething` → `XYZ_Something`  (acronym followed by Word)
      - `aB`           → `a_B`            (lowercase to uppercase)

    Digits attach to whichever side they ran into in the source name —
    `LM7806` → `lm7806` (no underscore between the trailing letters
    and digits), `ATmega328P` → `atmega328p` (the trailing `P`
    stays attached because there's no preceding lowercase letter).
    """
    # First regex: split an all-caps acronym (≥ 2 caps) from a
    # following CapitalizedWord (`HTTPServer` → `HTTP_Server`).  The
    # `[A-Z][A-Z]+` floor of 2 caps prevents catastrophic backtracking
    # of single-letter prefixes (`ATmega` would otherwise split at
    # `A_Tmega` because the regex engine backs `[A-Z]+` down to `A`
    # to find a fit).  With the 2-cap floor, `ATmega` has no
    # consecutive-2-cap prefix followed by Cap+lowercase and stays
    # whole.
    s = re.sub(r'([A-Z][A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    # Second regex: split CamelCase boundaries — `aB` becomes `a_B`.
    # Catches `MyChip` → `My_Chip` and the post-acronym word split
    # introduced above.
    s = re.sub(r'([a-z])([A-Z])', r'\1_\2', s)
    return s.lower()


def _parse_pins(spec: str) -> tuple[PinSpec, ...]:
    """Parse `name:direction:signal_type,name:direction:signal_type` syntax."""
    pins: list[PinSpec] = []
    for entry in spec.split(','):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split(':')
        if len(parts) != 3:
            raise SystemExit(
                f"Pin spec entries must be 'name:direction:signal_type'; "
                f"got {entry!r}"
            )
        name, direction, signal_type = (p.strip() for p in parts)
        if direction not in _DIRECTIONS:
            raise SystemExit(
                f"Pin direction must be one of {sorted(_DIRECTIONS)}; "
                f"got {direction!r}"
            )
        if signal_type not in _SIGNAL_TYPES:
            raise SystemExit(
                f"Pin signal_type must be one of {sorted(_SIGNAL_TYPES)}; "
                f"got {signal_type!r}"
            )
        if not re.match(r'^[a-z][a-z0-9_]*$', name):
            raise SystemExit(
                f"Pin name must be snake_case starting with a letter; "
                f"got {name!r}"
            )
        pins.append(PinSpec(name=name, direction=direction,
                            signal_type=signal_type))
    if not pins:
        raise SystemExit("at least one pin must be specified")
    return tuple(pins)


def _parse_args(argv: list[str]) -> ComponentSpec:
    p = argparse.ArgumentParser(
        prog='scaffold_component',
        description=__doc__.splitlines()[0] if __doc__ else None,
    )
    p.add_argument('--name', required=True,
                   help='CamelCase class name (e.g. MyChip).')
    p.add_argument('--kind', required=True, choices=sorted(_KINDS),
                   help='Component family.')
    p.add_argument('--refdes-prefix', required=True,
                   help='IEEE-315 reference designator prefix (R, U, J, ...).')
    p.add_argument('--footprint', required=True,
                   help='KiCad footprint string (e.g. Package_DIP:DIP-8_W7.62mm).')
    p.add_argument('--pins', required=True,
                   help='Comma-separated pins as `name:direction:signal_type`. '
                        'Direction: in / out / bidir.  Signal type: Analog / Digital.')
    p.add_argument('--description', required=True,
                   help='One-line description for the class docstring.')
    p.add_argument('--output-root',
                   help='Repo root override (test harness uses this).  Defaults '
                        'to the repo root computed from this script.')
    args = p.parse_args(argv)

    if not re.match(r'^[A-Z][A-Za-z0-9_]*$', args.name):
        raise SystemExit(
            f"--name must be CamelCase starting with an uppercase letter; "
            f"got {args.name!r}"
        )
    if not re.match(r'^[A-Z]+$', args.refdes_prefix):
        raise SystemExit(
            f"--refdes-prefix must be one or more uppercase letters "
            f"(IEEE 315); got {args.refdes_prefix!r}"
        )

    return ComponentSpec(
        class_name=args.name,
        kind=args.kind,
        refdes_prefix=args.refdes_prefix,
        footprint=args.footprint,
        pins=_parse_pins(args.pins),
        description=args.description,
    )


# ----------------------------------------------------------- rendering


_DIRECTION_ENUM = {
    'in':    'Direction.IN',
    'out':   'Direction.OUT',
    'bidir': 'Direction.BIDIR',
}


def _imports_for(spec: ComponentSpec) -> str:
    """Build the imports block.  Pulls in only the signal types used
    by the pin spec — keeps the generated file tight and matches the
    style of the hand-written components.

    Chip scaffolds get the additional surface they need to satisfy
    `Chip.__init__`: `Pin`, `PinId`, `wire`, and `IdleDriver` as the
    placeholder cell that drives every OUT pin's internal face."""
    sig_types = sorted({p.signal_type for p in spec.pins})
    signals_import = f"from framework.signals import {', '.join(sig_types)}"
    if spec.kind == 'chip':
        return (
            f"from typing import Any, ClassVar\n"
            f"\n"
            f"from pydantic import validate_call\n"
            f"\n"
            f"from framework.chip import Chip\n"
            f"from framework.ground import GroundDomain, ELECTRICAL\n"
            f"from framework.pin import Pin, PinId\n"
            f"from framework.port import Direction\n"
            f"from framework.refdes import RefdesNumber, validate_refdes\n"
            f"from framework.registry import register\n"
            f"{signals_import}\n"
            f"from framework.wire import wire\n"
            f"\n"
            f"from .concepts.idle_driver import IdleDriver\n"
        )
    return (
        f"from typing import Any, ClassVar\n"
        f"\n"
        f"from pydantic import validate_call\n"
        f"\n"
        f"from framework.part import Part\n"
        f"from framework.ground import GroundDomain, ELECTRICAL\n"
        f"from framework.port import Port, Direction\n"
        f"from framework.refdes import RefdesNumber, validate_refdes\n"
        f"{signals_import}\n"
        f"from framework.registry import register\n"
    )


def _pin_numbers_block(spec: ComponentSpec) -> str:
    """`PIN_NUMBERS = {'t1': 1, 't2': 2, ...}` mapping in pin-order."""
    entries = ', '.join(f"'{p.name}': {i}" for i, p in enumerate(spec.pins, 1))
    return f"PIN_NUMBERS: ClassVar[dict[str, int]] = {{{entries}}}"


def _ports_block(spec: ComponentSpec) -> str:
    """The ports dict, one Port per pin, mandatory=True for IN/OUT/BIDIR
    (the scaffolded default — every declared pin matters; the
    contributor flips `mandatory=False` per pin if the part legitimately
    tolerates a dangling lead)."""
    lines = []
    for p in spec.pins:
        lines.append(
            f"            '{p.name}': Port("
            f"'{p.name}', {_DIRECTION_ENUM[p.direction]}, domain, "
            f"mandatory=True, signal_type={p.signal_type}),"
        )
    return '\n'.join(lines)


def _has_out(spec: ComponentSpec) -> bool:
    return any(p.direction == 'out' for p in spec.pins)


def _evaluate_body(spec: ComponentSpec) -> str:
    """`evaluate()` body — drive every OUT port with a placeholder so
    the scaffold output passes the framework's chip OUT-pin invariant
    (a Chip with an OUT pin must drive it).  The contributor replaces
    the placeholder logic with the real behaviour."""
    out_pins = [p for p in spec.pins if p.direction == 'out']
    if not out_pins:
        # No outputs to drive.  Passive shapes (resistor-like) have
        # this; the body stays a no-op.
        return (
            "        # No OUT pins to drive — passive part.  The\n"
            "        # framework's `evaluate()` for a passive is a\n"
            "        # no-op because terminal voltages aren't derivable\n"
            "        # from each other without solving Ohm's law.\n"
            "        pass"
        )
    drives = []
    for p in out_pins:
        if p.signal_type == 'Digital':
            drives.append(
                f"        self._ports['{p.name}'].drive(False)  # TODO: real logic"
            )
        else:
            drives.append(
                f"        self._ports['{p.name}'].drive(0.0)    # TODO: real logic"
            )
    return '\n'.join(drives)


def _call_signature(spec: ComponentSpec) -> tuple[str, str]:
    """Build the `__call__` signature + body using hardware pin names.

    Naming follows CLAUDE.md's rule: pin names, not application-layer
    names.  The body reads every IN/BIDIR port, drives every OUT port
    with a placeholder, then returns `None` (the framework's standard
    *callable-but-not-a-calculator* shape — the contributor adapts to
    the part's actual signal flow).
    """
    in_pins = [p for p in spec.pins if p.direction in ('in', 'bidir')]
    out_pins = [p for p in spec.pins if p.direction == 'out']

    def _annot(p: PinSpec) -> str:
        # __call__ accepts the Python primitive at the API surface;
        # internal canonicalisation through Port.drive() handles the
        # signal_type conversion.
        return 'float' if p.signal_type == 'Analog' else 'bool'

    args = ', '.join(f"{p.name}: {_annot(p)}" for p in in_pins)
    sig = f"    def __call__(self, {args}) -> None:" if args else \
          "    def __call__(self) -> None:"

    body_lines = []
    for p in in_pins:
        body_lines.append(
            f"        self._ports['{p.name}'].drive({p.name})"
        )
    if out_pins:
        body_lines.append("        self.evaluate()")
    elif not body_lines:
        body_lines.append("        pass")

    return sig, '\n'.join(body_lines)


def _class_body(spec: ComponentSpec) -> str:
    return (
        _chip_class_body(spec) if spec.kind == 'chip'
        else _passive_class_body(spec)
    )


def _shared_classvars(spec: ComponentSpec) -> str:
    """The six ClassVars every component class declares.  Identical
    across kinds — only the surrounding init / port machinery differs."""
    return f'''\
    REFDES_PREFIX: ClassVar[str] = '{spec.refdes_prefix}'
    FOOTPRINT: ClassVar[str | None] = "{spec.footprint}"
    {_pin_numbers_block(spec)}

    LAYOUT: ClassVar[dict[str, Any]] = {{
        # TODO: fill in the layout descriptor — see existing
        # components for examples (axial_2lead, dip, qfp, etc.).
    }}

    VERIFY: ClassVar[tuple[str, ...]] = (
        # TODO: one or more multimeter / bench-test instructions the
        # builder runs *before* powering the board, written as if
        # talking the user through it at the bench.
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        # TODO: zero or more assembly-time warnings — the things a
        # first-time builder gets wrong about this specific part.
    )
'''


def _passive_class_body(spec: ComponentSpec) -> str:
    call_sig, call_body = _call_signature(spec)
    return f'''\
@register('{spec.class_name}')
class {spec.class_name}(Part):
    """{spec.description}

    TODO: replace this docstring with the part's real behavioural
    description.  Include the manufacturer's pin table, the operating
    voltage range, and any framework-relevant gotchas the part is
    famous for.
    """

    __slots__ = ('_ports', '_refdes_number')

{_shared_classvars(spec)}
    @validate_call(config={{'arbitrary_types_allowed': True}})
    def __init__(
        self,
        domain: GroundDomain = ELECTRICAL,
        *,
        refdes_number: RefdesNumber,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._ports = {{
{_ports_block(spec)}
        }}

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def refdes(self) -> str:
        return f"{{self.REFDES_PREFIX}}{{self._refdes_number}}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    def evaluate(self) -> None:
{_evaluate_body(spec)}

{call_sig}
{call_body}

    def __str__(self) -> str:
        return self.refdes

    def __repr__(self) -> str:
        return f"{spec.class_name}(refdes={{self.refdes!r}})"
'''


def _chip_pin_construction(spec: ComponentSpec) -> str:
    """Build a Pin per declared port — the `Pin(PinId(n, 'name'), ...)`
    shape every concrete Chip uses."""
    lines = []
    for i, p in enumerate(spec.pins, 1):
        mandatory = 'True' if p.direction != 'out' else 'False'
        lines.append(
            f"        pin_{p.name} = Pin(\n"
            f"            PinId({i}, '{p.name}'),\n"
            f"            {_DIRECTION_ENUM[p.direction]},\n"
            f"            domain,\n"
            f"            mandatory={mandatory},\n"
            f"            signal_type={p.signal_type},\n"
            f"        )"
        )
    return '\n'.join(lines)


def _chip_cell_wiring(spec: ComponentSpec) -> tuple[str, str]:
    """For each OUT pin, instantiate an `IdleDriver` and wire its
    `out` port to `pin.internal`.  Satisfies the framework's "every
    OUT pin is internally driven" invariant — the scaffolded chip
    constructs without `BARE_FIRMWARE_DRIVEN`, and the contributor
    later replaces each `IdleDriver` with the real behavioural cell.

    Returns `(cells_decl, cells_list)` where `cells_decl` is the
    statements that build the cells and `cells_list` is the
    comma-joined expression for `super().__init__(cells=...)`.
    """
    out_pins = [p for p in spec.pins if p.direction == 'out']
    if not out_pins:
        return ('', '')
    decl_lines: list[str] = []
    cell_names: list[str] = []
    for p in out_pins:
        idle_val = 'False' if p.signal_type == 'Digital' else '0.0'
        cell_name = f"cell_{p.name}"
        decl_lines.append(
            f"        {cell_name} = IdleDriver("
            f"{p.signal_type}, idle_value={idle_val}, domain=domain)"
        )
        decl_lines.append(
            f"        wire({cell_name}.ports['out'], pin_{p.name}.internal)"
        )
        cell_names.append(cell_name)
    return ('\n'.join(decl_lines), ', '.join(cell_names))


def _chip_call_signature_and_body(spec: ComponentSpec) -> tuple[str, str]:
    """Build a concrete `__call__` for the chip scaffold — `Chip.__call__`
    is abstract, so every concrete Chip subclass must implement one.
    The scaffold's shape mirrors `SN74HC04.__call__`: take each IN /
    BIDIR pin as a keyword argument with a sensible default, drive
    the corresponding external port, run `evaluate()`, return the
    tuple of OUT-pin values."""
    in_pins = [p for p in spec.pins if p.direction in ('in', 'bidir')]
    out_pins = [p for p in spec.pins if p.direction == 'out']

    def _annot(p: PinSpec) -> str:
        return 'float | None' if p.signal_type == 'Analog' else 'bool | None'

    def _default(p: PinSpec) -> str:
        return '0.0' if p.signal_type == 'Analog' else 'False'

    if not in_pins:
        sig = "    def __call__(self) -> Any:"
    else:
        # Format on continuation lines for readability when many pins.
        args = ',\n        '.join(
            f"{p.name}: {_annot(p)} = {_default(p)}" for p in in_pins
        )
        sig = f"    def __call__(\n        self,\n        {args},\n    ) -> Any:"

    body_lines = ["        self._assert_no_inputs_wired()"]
    for p in in_pins:
        body_lines.append(f"        self._ports['{p.name}'].drive({p.name})")
    body_lines.append("        self.evaluate()")
    if out_pins:
        return_tuple = ', '.join(f"self._ports['{p.name}'].value" for p in out_pins)
        body_lines.append(f"        return ({return_tuple},)")
    else:
        body_lines.append("        return None")
    return sig, '\n'.join(body_lines)


def _chip_class_body(spec: ComponentSpec) -> str:
    pin_var_list = ', '.join(f"pin_{p.name}" for p in spec.pins)
    cell_decl, cell_list = _chip_cell_wiring(spec)
    cell_decl_block = ('\n' + cell_decl) if cell_decl else ''
    cell_arg = f"[{cell_list}]" if cell_list else '[]'
    call_sig, call_body = _chip_call_signature_and_body(spec)
    # `__slots__` for a Chip is empty by convention — Chip's own
    # `__slots__` carries the framework-needed members.  The scaffold
    # adds `_refdes_number` (chip-specific) and leaves room for the
    # contributor to add more if the part needs internal state.
    return f'''\
@register('{spec.class_name}')
class {spec.class_name}(Chip):
    """{spec.description}

    TODO: replace this docstring with the part's real behavioural
    description.  Include the manufacturer's pin table, the operating
    voltage range, and any framework-relevant gotchas the part is
    famous for.

    The scaffold wires every OUT pin to an `IdleDriver` cell as a
    placeholder so the framework's *every OUT pin is internally
    driven* invariant passes by construction.  Replace each
    `IdleDriver` with the real behavioural cell once you know the
    part's logic (concept cells live in
    `src/components/chips/concepts/`).
    """

    __slots__ = ('_refdes_number',)

{_shared_classvars(spec)}
    @validate_call(config={{'arbitrary_types_allowed': True}})
    def __init__(
        self,
        domain: GroundDomain = ELECTRICAL,
        *,
        refdes_number: RefdesNumber,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
{_chip_pin_construction(spec)}{cell_decl_block}
        super().__init__(
            pins=[{pin_var_list}],
            cells={cell_arg},
        )

    @property
    def refdes(self) -> str:
        return f"{{self.REFDES_PREFIX}}{{self._refdes_number}}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @validate_call(config={{'arbitrary_types_allowed': True}})
{call_sig}
{call_body}

    def __str__(self) -> str:
        return self.refdes

    def __repr__(self) -> str:
        return f"{spec.class_name}(refdes={{self.refdes!r}})"
'''


def render_component(spec: ComponentSpec) -> str:
    """Whole-file render: header comment + imports + class body."""
    return (
        f"# Scaffolded by scripts/scaffold_component.py — fill in the\n"
        f"# TODO blocks with this part's real specification.\n"
        f"{_imports_for(spec)}\n"
        f"\n"
        f"{_class_body(spec)}"
    )


def render_test_stub(spec: ComponentSpec) -> str:
    """A minimal test stub: construction, ports shape, port-direction
    and signal-type pinning per the spec.  The framework's broader
    test pattern (per-pin gotcha tests, per-cell behaviour tests)
    becomes the contributor's follow-up; this stub keeps the new
    class linted, importable, and refdes-validated."""
    snake = _snake_case(spec.class_name)
    module_path = f"components.{spec.kind}s.{snake}"
    pin_assertions = []
    for p in spec.pins:
        pin_assertions.append(
            f"    assert part.ports['{p.name}'].direction is "
            f"{_DIRECTION_ENUM[p.direction]}"
        )
        pin_assertions.append(
            f"    assert part.ports['{p.name}'].signal_type "
            f"is {p.signal_type}"
        )
    pin_block = '\n'.join(pin_assertions)
    return f'''\
"""Scaffolded tests for {spec.class_name} — extend as the part grows."""
from {module_path} import {spec.class_name}
from framework.port import Direction
from framework.signals import Analog, Digital


def _make() -> {spec.class_name}:
    return {spec.class_name}(refdes_number=1)


def test_constructs() -> None:
    part = _make()
    assert part.refdes == '{spec.refdes_prefix}1'


def test_port_shape() -> None:
    part = _make()
    expected = {set(p.name for p in spec.pins)!r}
    assert set(part.ports) == expected


def test_port_directions_and_signal_types() -> None:
    part = _make()
{pin_block}
'''


# --------------------------------------------------------- file output


def _component_target_path(spec: ComponentSpec, root: Path) -> Path:
    snake = _snake_case(spec.class_name)
    return root / 'src' / 'components' / f'{spec.kind}s' / f'{snake}.py'


def _test_target_path(spec: ComponentSpec, root: Path) -> Path:
    snake = _snake_case(spec.class_name)
    return root / 'tests' / 'components' / f'test_{snake}.py'


def _init_target_path(spec: ComponentSpec, root: Path) -> Path:
    return root / 'src' / 'components' / f'{spec.kind}s' / '__init__.py'


def _update_init_all(init_path: Path, class_name: str) -> bool:
    """Append `class_name` to the package `__init__.py`'s `__all__`
    list and add a matching `from .snake_name import ClassName` line
    above.  Idempotent — returns False if the name is already
    re-exported.
    """
    snake = _snake_case(class_name)
    text = init_path.read_text() if init_path.exists() else (
        f'"""Auto-generated component module.\n\n'
        f'Components live under their kind-specific subpackage; this\n'
        f'`__init__.py` re-exports them so callers can do\n'
        f'`from components.<kind>s import ClassName`.\n'
        f'"""\n\n__all__: list[str] = []\n'
    )
    if class_name in text:
        return False
    import_line = f"from .{snake} import {class_name}"
    # Insert the import after the last `from .<x> import ...` line, or
    # near the top of the module if there are none.
    lines = text.splitlines()
    last_import_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('from .'):
            last_import_idx = i
    if last_import_idx >= 0:
        lines.insert(last_import_idx + 1, import_line)
    else:
        # Place after the docstring or at top.
        insert_at = 0
        if lines and lines[0].startswith('"""'):
            # Find end of docstring.
            for i in range(1, len(lines)):
                if '"""' in lines[i]:
                    insert_at = i + 1
                    break
        lines.insert(insert_at, '')
        lines.insert(insert_at + 1, import_line)

    # Update __all__.  Handles both bracketed-list and append-style.
    new_text = '\n'.join(lines)
    if re.search(r'__all__\s*=\s*\[', new_text):
        new_text = re.sub(
            r"(__all__\s*=\s*\[)([^\]]*)\]",
            lambda m: _append_to_all_list(m.group(1), m.group(2), class_name),
            new_text,
            count=1,
        )
    else:
        new_text = new_text.rstrip() + f"\n\n__all__ = ['{class_name}']\n"
    init_path.write_text(new_text + ('\n' if not new_text.endswith('\n') else ''))
    return True


def _append_to_all_list(prefix: str, body: str, name: str) -> str:
    """Append `name` to a bracketed `__all__ = [...]` body, preserving
    existing entries and trailing-comma style."""
    stripped = body.strip()
    if not stripped:
        return f"{prefix}'{name}']"
    has_trailing_comma = stripped.endswith(',')
    sep = '' if has_trailing_comma else ', '
    new_body = body.rstrip().rstrip(',') + f"{sep} '{name}',"
    return f"{prefix}{new_body}]"


def write_scaffold(spec: ComponentSpec, root: Path) -> dict[str, Path]:
    """Materialise the scaffold under `root`.  Returns a dict mapping
    each emitted artefact's role (`component`, `test`, `init`) to its
    path so the caller (CLI or test) can inspect."""
    component_path = _component_target_path(spec, root)
    test_path = _test_target_path(spec, root)
    init_path = _init_target_path(spec, root)

    component_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.parent.mkdir(parents=True, exist_ok=True)

    if component_path.exists():
        raise SystemExit(
            f"Refusing to overwrite existing component file: {component_path}.  "
            f"Move the file out of the way or pass a different --name."
        )
    if test_path.exists():
        raise SystemExit(
            f"Refusing to overwrite existing test file: {test_path}.  "
            f"Move the file out of the way or pass a different --name."
        )

    component_path.write_text(render_component(spec))
    test_path.write_text(render_test_stub(spec))
    _update_init_all(init_path, spec.class_name)

    return {
        'component': component_path,
        'test': test_path,
        'init': init_path,
    }


def main(argv: list[str] | None = None) -> int:
    spec = _parse_args(list(sys.argv[1:] if argv is None else argv))
    args = sys.argv if argv is None else argv
    # Allow --output-root to override the inferred repo root.
    root_override = None
    if argv is None:
        # Reparse just to pull --output-root; argparse already validated.
        for i, tok in enumerate(args):
            if tok == '--output-root' and i + 1 < len(args):
                root_override = Path(args[i + 1])
    root = root_override or Path(__file__).resolve().parent.parent
    paths = write_scaffold(spec, root)
    print(f"Scaffolded:")
    for role, path in paths.items():
        print(f"  {role}: {path.relative_to(root)}")
    print(
        "\nNext steps:\n"
        f"  1. Open {paths['component'].relative_to(root)} and fill in the TODO\n"
        f"     blocks (VERIFY / GOTCHAS / pin logic).\n"
        f"  2. Open {paths['test'].relative_to(root)} and add behavioural\n"
        f"     tests beyond the construction shape.\n"
        f"  3. Run `uv run pytest {paths['test'].relative_to(root)}` to\n"
        f"     confirm the scaffolded class still passes after your edits.\n"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
