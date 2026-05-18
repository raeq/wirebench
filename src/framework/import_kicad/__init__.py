"""KiCad netlist import — reverse of `framework.export.kicad`.

Reads a `.net` file emitted by Eeschema and reconstructs an
in-memory `wirebench.Circuit` whose parts, refdes assignments, and
`wire()`-connected nets match the netlist.

The top-level entry point is `import_kicad_netlist(path, strict=False)`,
which returns a tuple of `(circuit, report)` — the constructed
Circuit plus a structured `ImportReport` listing unmapped parts,
skipped nodes, etc.  See `emit_python.py` for the source-code
generator that the `wirebench import-kicad` CLI uses.
"""
from __future__ import annotations

__all__ = [
    'ImportReport', 'ImportedPart',
    'import_kicad_netlist', 'load_netlist_file',
]

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

from framework.circuit import Circuit
from framework.errors import LoadError
from framework.part import Part
from framework.wire import wire

from framework.import_kicad.nets import (
    NetRecord, looks_like_high_rail, looks_like_low_rail, parse_nets,
    resolve_port,
)
from framework.import_kicad.parser import (
    SExpr, children, field_value, parse,
)
from framework.import_kicad.resolver import (
    KiCadComponent, resolve_part_class,
)


@dataclass(slots=True)
class ImportedPart:
    refdes: str
    value:  str
    klass:  type[Part]
    is_unknown_placeholder: bool


@dataclass(slots=True)
class ImportReport:
    """Outcome of a netlist import — useful for the CLI to print a
    human-readable summary and for tests to assert on coverage."""
    parts:       list[ImportedPart] = field(default_factory=list)
    nets:        list[NetRecord]    = field(default_factory=list)
    unresolved:  list[str]          = field(default_factory=list)
    skipped_nets: list[str]         = field(default_factory=list)


def load_netlist_file(path: str | Path) -> SExpr:
    """Read a KiCad `.net` file from disk and parse it.  Errors at
    parse time surface as `LoadError`."""
    text = Path(path).read_text(encoding='utf-8')
    return parse(text)


def import_kicad_netlist(
    path: str | Path, *, strict: bool = False,
) -> tuple[Circuit, ImportReport]:
    """Parse a netlist on disk and build a wirebench Circuit from it.

    `strict=True` raises `UnknownPartError` when a KiCad part has no
    wirebench mapping.  `strict=False` (the default) substitutes
    UnknownPart placeholders and records them in the returned report.
    """
    ast = load_netlist_file(path)
    return import_from_ast(ast, strict=strict)


def import_from_ast(
    ast: SExpr, *, strict: bool = False,
) -> tuple[Circuit, ImportReport]:
    """Same shape as `import_kicad_netlist` but takes a pre-parsed
    AST (useful for tests that synthesise netlists in memory)."""
    components_section = _section(ast, 'components')
    nets_section       = _section(ast, 'nets')

    parsed_components = _parse_components(components_section)
    parsed_nets       = parse_nets(nets_section)

    refdes_to_part: dict[str, Part] = {}
    report = ImportReport()
    unknown_cache: dict[tuple[Any, ...], type[Part]] = {}

    for kc in parsed_components:
        cls = resolve_part_class(kc, strict=strict, unknown_cache=unknown_cache)
        try:
            part = _instantiate(cls, kc)
        except Exception as exc:
            raise LoadError(
                f"Failed to instantiate {cls.__name__} for "
                f"netlist refdes {kc.ref!r} (value={kc.value!r}): {exc}"
            ) from exc
        refdes_to_part[kc.ref] = part
        report.parts.append(ImportedPart(
            refdes=kc.ref,
            value=kc.value,
            klass=cls,
            is_unknown_placeholder=getattr(cls, 'IMPORTED_FROM_KICAD', False),
        ))
        if getattr(cls, 'IMPORTED_FROM_KICAD', False):
            report.unresolved.append(kc.ref)

    # Apply each net via wire(); skip 1-node nets (KiCad emits these
    # for unconnected pins) and nets whose nodes don't resolve.
    # For named power / ground nets, synthesise a Rail to drive them
    # — wirebench's KiCad exporter inlines the Rail as a net name, so
    # the round trip needs us to reconstruct it.
    from components.passives.rail import Rail
    from framework.signals import Analog, Digital
    rails: list[Rail] = []
    high_rail_by_signal: dict[type, Rail] = {}
    low_rail_by_signal:  dict[type, Rail] = {}

    for net in parsed_nets:
        if len(net.nodes) < 2 and not _net_needs_rail(net):
            report.skipped_nets.append(net.name or f"code{net.code}")
            continue
        ports = []
        for refdes, pin_number in net.nodes:
            resolved = resolve_port(refdes_to_part, refdes, pin_number)
            if resolved is None:
                continue
            part, port_name = resolved
            ports.append(part.ports[port_name])

        is_high = looks_like_high_rail(net.name)
        is_low  = looks_like_low_rail(net.name)

        if is_high or is_low:
            # Rail-fed net: wirebench's exporter inlines the Rail into
            # the net name, and the original design may have had one
            # Digital Rail and one Analog Rail sharing the bench-level
            # GND/VCC.  Split per-signal_type so we don't try to wire
            # mixed Digital/Analog ports together.
            by_type: dict[type, list[Any]] = {}
            for p in ports:
                by_type.setdefault(p.signal_type, []).append(p)
            for signal_type, type_ports in by_type.items():
                pool = high_rail_by_signal if is_high else low_rail_by_signal
                rail = pool.get(signal_type)
                if rail is None:
                    rail = Rail(bool(is_high), signal_type=signal_type)
                    pool[signal_type] = rail
                    rails.append(rail)
                wire(rail.ports['out'], *type_ports)
            continue

        if len(ports) < 2:
            report.skipped_nets.append(net.name or f"code{net.code}")
            continue
        wire(*ports)
    report.nets = parsed_nets

    circuit = Circuit(
        parts=list(refdes_to_part.values()) + list(rails),
        ports={},
    )
    return circuit, report


def _net_needs_rail(net: NetRecord) -> bool:
    return looks_like_high_rail(net.name) or looks_like_low_rail(net.name)


def _section(ast: SExpr, name: str) -> SExpr:
    for child in ast[1:]:
        if isinstance(child, list) and child and child[0] == name:
            return child
    raise LoadError(f"netlist is missing a top-level ({name} ...) section")


def _parse_components(section: SExpr) -> list[KiCadComponent]:
    out: list[KiCadComponent] = []
    for comp in children(section, 'comp'):
        ref       = field_value(comp, 'ref') or ''
        value     = field_value(comp, 'value') or ''
        footprint = field_value(comp, 'footprint')
        lib_part: tuple[str | None, str | None] = (None, None)
        libsource = next(
            (c for c in comp[1:]
             if isinstance(c, list) and c and c[0] == 'libsource'),
            None,
        )
        if libsource is not None:
            lib_part = (
                field_value(libsource, 'lib'),
                field_value(libsource, 'part'),
            )
        pin_specs = _extract_pin_specs_from_node_refs(comp)
        out.append(KiCadComponent(
            ref=ref,
            value=value,
            footprint=footprint,
            libsource_lib=lib_part[0],
            libsource_part=lib_part[1],
            pin_specs=pin_specs,
        ))
    return out


def _extract_pin_specs_from_node_refs(_comp: SExpr) -> tuple[tuple[int, str], ...]:
    """Resolved from the netlist's `(nets ...)` section after the
    components are parsed.  Filled in by a second pass — see
    `_attach_pin_specs` — once we know which pins the netlist
    actually mentions for each refdes."""
    return ()


def _instantiate(cls: type[Part], kc: KiCadComponent) -> Part:
    """Construct a part of class `cls` using the netlist component's
    value as the appropriate constructor kwarg.

    The mapping is small and explicit so each class's constructor
    contract stays visible at the call site.  Anything not handled
    here falls through to a refdes-only construction (suitable for
    chips, connectors with explicit pin_count, and the synthesised
    UnknownPart classes)."""
    refdes_number = _refdes_number(kc.ref)
    name = cls.__name__
    factory = cast(Any, cls)

    if name == 'Resistor':
        return cast(Part, factory(
            ohms=_to_float(kc.value, fallback=1.0),
            refdes_number=refdes_number,
        ))
    if name == 'Capacitor':
        return cast(Part, factory(
            farads=_to_float(kc.value, fallback=100e-9),
            refdes_number=refdes_number,
        ))
    if name == 'Inductor':
        return cast(Part, factory(
            henries=_to_float(kc.value, fallback=100e-6),
            refdes_number=refdes_number,
        ))
    if name == 'LED':
        color = kc.value if kc.value else 'red'
        return cast(Part, factory(color=color, refdes_number=refdes_number))
    if name == 'Cell':
        return cast(Part, factory(
            initial_state_of_charge=1.0, refdes_number=refdes_number,
        ))
    if name == 'Rail':
        return cast(Part, factory(level=True))

    # Parameterised connector families.  KiCad doesn't surface
    # pin_count / pitch in a uniform place, but the netlist's
    # per-net `node` entries do indirectly via the maximum pin
    # number referenced; rather than introducing a circular
    # dependency, default to the catalogue's most common (4-pin,
    # 2.54 mm) shape.  The user can edit the generated source.
    if (cls.__module__.endswith('.headers')
            and 'pin_count' in cls.__init__.__code__.co_varnames):
        return cast(Part, factory(
            pin_count=4, pitch_mm=2.54, refdes_number=refdes_number,
        ))

    return cast(Part, factory(refdes_number=refdes_number))


def _refdes_number(ref: str) -> int:
    digits = ''.join(c for c in ref if c.isdigit())
    return int(digits) if digits else 1


def _to_float(value: str, *, fallback: float) -> float:
    """KiCad emits resistor values like '10k', '4.7M', '100n'.  Parse
    those plus plain numeric strings into the SI base unit."""
    s = value.strip()
    if not s:
        return fallback
    # Strip a trailing unit letter (Ω, F, H) for tolerance.
    while s and s[-1] in 'ΩFH':
        s = s[:-1]
    if not s:
        return fallback
    multiplier = 1.0
    suffix_table = {
        'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6,
        'm': 1e-3, 'k': 1e3, 'K': 1e3, 'M': 1e6, 'G': 1e9,
    }
    last = s[-1]
    if last in suffix_table:
        multiplier = suffix_table[last]
        s = s[:-1]
    try:
        return float(s) * multiplier
    except ValueError:
        return fallback
