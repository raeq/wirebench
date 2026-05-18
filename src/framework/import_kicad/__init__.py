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
    'ImportReport', 'ImportedPart', 'WireGroup',
    'import_kicad_netlist', 'load_netlist_file',
]

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

from framework.circuit import Circuit
from framework.errors import LoadError
from framework.part import Part
from framework.port import Direction
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
    # Carried verbatim from the netlist so downstream consumers
    # (the Python-source emitter, mostly) can reproduce placeholder
    # parts with the same pin shape they had at import time.
    pin_specs: tuple[tuple[int, str], ...] = ()
    footprint: str | None                  = None


@dataclass(slots=True)
class WireGroup:
    """One emitted `wire(...)` call, post-rail-split.

    `rail_polarity` is `'+'` / `'-'` for synthesised power / ground
    rails (the source must instantiate a Rail to drive the net) or
    `None` for plain peer-to-peer nets.  `signal_type_name` is the
    string `'Digital'` / `'Analog'` for rail groups so the generator
    can construct the right Rail; it's None for non-rail nets.

    `nodes` is `(refdes, pin_number)` pairs — the same shape the
    parser produces but already split across signal types so a
    mixed-signal GND net becomes two WireGroups (one Digital, one
    Analog) and the emitter doesn't have to redo the split.
    """
    net_name:         str
    rail_polarity:    str | None
    signal_type_name: str | None
    nodes:            list[tuple[str, int]]


@dataclass(slots=True)
class ImportReport:
    """Outcome of a netlist import — useful for the CLI to print a
    human-readable summary and for tests to assert on coverage."""
    parts:       list[ImportedPart] = field(default_factory=list)
    nets:        list[NetRecord]    = field(default_factory=list)
    wire_groups: list[WireGroup]    = field(default_factory=list)
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

    pin_specs_by_refdes = _extract_pin_specs_from_nets(nets_section)
    parsed_components = _parse_components(
        components_section, pin_specs_by_refdes,
    )
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
            pin_specs=kc.pin_specs,
            footprint=kc.footprint,
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
        # Build parallel arrays: live Port for the wire() call, plus
        # (refdes, pin_number) for the WireGroup record the emitter
        # will read back.
        resolved_ports: list[Any] = []
        resolved_nodes: list[tuple[str, int]] = []
        for refdes, pin_number in net.nodes:
            resolved = resolve_port(refdes_to_part, refdes, pin_number)
            if resolved is None:
                continue
            part, port_name = resolved
            resolved_ports.append(part.ports[port_name])
            resolved_nodes.append((refdes, pin_number))

        is_high = looks_like_high_rail(net.name)
        is_low  = looks_like_low_rail(net.name)

        if is_high or is_low:
            # Split by signal_type first — a mixed-signal GND/VCC net
            # becomes independent per-type buckets so we never attempt
            # to wire Digital and Analog ports together.
            by_type: dict[type, tuple[list[Any], list[tuple[str, int]]]] = {}
            for port, node in zip(resolved_ports, resolved_nodes):
                bucket = by_type.setdefault(port.signal_type, ([], []))
                bucket[0].append(port)
                bucket[1].append(node)
            for signal_type, (type_ports, type_nodes) in by_type.items():
                # If any port in this signal-type bucket has Direction.OUT,
                # a chip already drives the net for that signal type.
                # Synthesising a Rail on top would add a second driver and
                # raise ShortCircuitError — wire directly instead.
                if any(p.direction is Direction.OUT for p in type_ports):
                    if len(type_ports) >= 2:
                        wire(*type_ports)
                        report.wire_groups.append(WireGroup(
                            net_name=net.name,
                            rail_polarity=None,
                            signal_type_name=None,
                            nodes=list(type_nodes),
                        ))
                    else:
                        report.skipped_nets.append(
                            net.name or f"code{net.code}"
                        )
                    continue
                pool = high_rail_by_signal if is_high else low_rail_by_signal
                rail = pool.get(signal_type)
                if rail is None:
                    rail = Rail(bool(is_high), signal_type=signal_type)
                    pool[signal_type] = rail
                    rails.append(rail)
                wire(rail.ports['out'], *type_ports)
                report.wire_groups.append(WireGroup(
                    net_name=net.name,
                    rail_polarity='+' if is_high else '-',
                    signal_type_name=signal_type.__name__,
                    nodes=list(type_nodes),
                ))
            continue

        if len(resolved_ports) < 2:
            report.skipped_nets.append(net.name or f"code{net.code}")
            continue
        wire(*resolved_ports)
        report.wire_groups.append(WireGroup(
            net_name=net.name,
            rail_polarity=None,
            signal_type_name=None,
            nodes=list(resolved_nodes),
        ))
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


def _parse_components(
    section: SExpr, pin_specs_by_refdes: dict[str, tuple[tuple[int, str], ...]],
) -> list[KiCadComponent]:
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
        out.append(KiCadComponent(
            ref=ref,
            value=value,
            footprint=footprint,
            libsource_lib=lib_part[0],
            libsource_part=lib_part[1],
            pin_specs=pin_specs_by_refdes.get(ref, ()),
        ))
    return out


def _extract_pin_specs_from_nets(
    nets_section: SExpr,
) -> dict[str, tuple[tuple[int, str], ...]]:
    """Walk every `(net ...)` in the netlist, collect each component
    refdes's referenced `(pin)` numbers + `(pinfunction)` names, and
    return a `{refdes: ((pin_number, pin_name), …)}` map.

    The map feeds back into `KiCadComponent.pin_specs` so the
    `UnknownPart` placeholder gets a Pin per pin number the netlist
    actually uses — without this back-fill, placeholder parts have
    zero pins and `resolve_port()` silently drops every node that
    mentions them."""
    by_refdes: dict[str, dict[int, str]] = {}
    for net in children(nets_section, 'net'):
        for node in children(net, 'node'):
            ref = field_value(node, 'ref')
            pin = field_value(node, 'pin')
            if ref is None or pin is None:
                continue
            try:
                pin_number = int(pin)
            except ValueError:
                continue
            name = field_value(node, 'pinfunction') or f"pin_{pin_number}"
            by_refdes.setdefault(ref, {})
            # First mention wins — later mentions of the same pin
            # would re-name it inconsistently across nets.
            by_refdes[ref].setdefault(pin_number, name)
    return {
        ref: tuple(sorted(pin_map.items()))
        for ref, pin_map in by_refdes.items()
    }


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
