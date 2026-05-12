"""`.circuitry` file format — save/load entry points.

A `.circuitry` file is JSON describing the structure of a design: its
parts (by refdes / synthesised id), their wiring, and any composed
boards or mates.  The format is the foundation for downstream consumers
(SPICE / KiCad / EDIF exporters, schematic visualisers); each reads
`.circuitry` files rather than walking the in-memory model.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from pydantic import ValidationError, validate_call

from framework.board import Board
from framework.circuit import Circuit
from framework.connector import Connector
from framework.factor import FactorNode
from framework.port import Port
from framework.refdes import RefdesBearing
from framework.registry import lookup
from framework.wire import wire
from framework.format_records import (
    AssemblyRecord, BoardRecord, CircuitRecord, CircuitryFile,
    ComponentRecord, MateRecord, RailRecord, WireRecord,
)


CURRENT_FORMAT_VERSION = '1.0.0'


# -----------------------------------------------------------------
# Saving
# -----------------------------------------------------------------

def _component_id(component: FactorNode, rail_ids: dict[int, str]) -> str:
    """Local id for port references: refdes if the component is
    refdes-bearing, otherwise a stable synthesised id (Rail_0,
    Rail_1, …) captured in rail_ids by identity."""
    if isinstance(component, RefdesBearing):
        return component.refdes
    if id(component) in rail_ids:
        return rail_ids[id(component)]
    raise ValueError(f"No id for component {component!r}")


def _component_to_record(
    component: FactorNode,
    rail_ids: dict[int, str],
) -> ComponentRecord:
    """Build a per-type record from a live component."""
    cls_name = type(component).__name__
    if cls_name == 'Resistor':
        return cast(ComponentRecord, _import('ResistorRecord')(
            refdes=component.refdes,                 # type: ignore[attr-defined]
            ohms=float(component._ohms),             # type: ignore[attr-defined]
        ))
    if cls_name == 'Capacitor':
        return cast(ComponentRecord, _import('CapacitorRecord')(
            refdes=component.refdes,                 # type: ignore[attr-defined]
            farads=float(component._farads),         # type: ignore[attr-defined]
        ))
    if cls_name == 'Inductor':
        return cast(ComponentRecord, _import('InductorRecord')(
            refdes=component.refdes,                 # type: ignore[attr-defined]
            henries=float(component._henries),       # type: ignore[attr-defined]
        ))
    if cls_name == 'Relay_SPDT':
        return cast(ComponentRecord, _import('Relay_SPDTRecord')(
            refdes=component.refdes,                 # type: ignore[attr-defined]
            pickup_voltage=float(component._pickup), # type: ignore[attr-defined]
        ))
    if cls_name == 'LED':
        return cast(ComponentRecord, _import('LEDRecord')(
            refdes=component.refdes,                 # type: ignore[attr-defined]
            color=component._color,                  # type: ignore[attr-defined]
        ))
    if cls_name == 'Rail':
        return cast(ComponentRecord, RailRecord(
            id=rail_ids[id(component)],
            level=bool(component._level),            # type: ignore[attr-defined]
        ))
    # Refdes-bearing chip / connector — class-specific args follow.
    record_cls = _import(f'{cls_name}Record')
    kwargs: dict[str, Any] = {'refdes': component.refdes}  # type: ignore[attr-defined]
    if isinstance(component, Connector):
        # Always emit pin_count and pitch_mm for parameterised connectors;
        # for fixed-geometry ones the record class doesn't declare them
        # and pydantic's extra='forbid' will reject — so only emit when
        # the record class has those fields.
        fields = record_cls.model_fields
        if 'pin_count' in fields:
            kwargs['pin_count'] = component.pin_count
        if 'pitch_mm' in fields:
            kwargs['pitch_mm'] = component.pitch_mm
    return cast(ComponentRecord, record_cls(**kwargs))


def _import(name: str) -> Any:
    from framework import format_records
    return getattr(format_records, name)


def _port_ref(component_id: str, port_name: str) -> str:
    return f"{component_id}.{port_name}"


def _collect_wires(
    components: list[FactorNode],
    rail_ids: dict[int, str],
) -> list[WireRecord]:
    """Walk every component's ports, group by Node id, emit one
    WireRecord per node touched by ≥ 2 board-level ports.

    A Node touched by only one board-level port is a dangling-but-wired
    pin (e.g. one mated connector pin where the partner is on a
    different board); we don't emit it here because it's not a wire at
    the board level.
    """
    by_node: dict[int, list[tuple[str, str]]] = {}
    for component in components:
        comp_id = _component_id(component, rail_ids)
        for port_name, port in component.ports.items():
            if port.node is None:
                continue
            by_node.setdefault(id(port.node), []).append((comp_id, port_name))
    wires: list[WireRecord] = []
    for refs in by_node.values():
        if len(refs) < 2:
            continue
        # Sort port refs lexicographically for determinism.
        sorted_refs = sorted(_port_ref(c, p) for c, p in refs)
        wires.append(WireRecord(ports=sorted_refs))
    # Sort wires by their first port-ref for determinism.
    return sorted(wires, key=lambda w: w.ports[0])


def _circuit_components_and_wires(
    circuit: Circuit,
) -> tuple[list[ComponentRecord], list[WireRecord], dict[int, str]]:
    """Build component records + wire records for a Circuit's direct
    factor_nodes.  Rails are given synthesised IDs assigned in encounter
    order."""
    rail_ids: dict[int, str] = {}
    rail_counter = 0
    for component in circuit._factor_nodes:
        if type(component).__name__ == 'Rail':
            rail_ids[id(component)] = f'Rail_{rail_counter}'
            rail_counter += 1
    component_records = [
        _component_to_record(c, rail_ids) for c in circuit._factor_nodes
    ]
    # Sort component records by refdes / id (deterministic output).
    def sort_key(r: ComponentRecord) -> str:
        return str(getattr(r, 'refdes', None) or getattr(r, 'id', '') or '')
    component_records.sort(key=sort_key)
    wire_records = _collect_wires(circuit._factor_nodes, rail_ids)
    return component_records, wire_records, rail_ids


def _circuit_to_record(circuit: Circuit) -> CircuitRecord:
    components, wires, rail_ids = _circuit_components_and_wires(circuit)
    surface_ports: dict[str, str] = {}
    for name, port in circuit._ports.items():
        # Find which factor_node owns this port.
        ref = _find_port_ref(port, circuit._factor_nodes, rail_ids)
        if ref is None:
            raise ValueError(
                f"Cannot resolve surface port {name!r} to a component"
            )
        surface_ports[name] = ref
    return CircuitRecord(
        components=components,
        wires=wires,
        surface_ports=dict(sorted(surface_ports.items())),
    )


def _board_to_record(board: Board) -> BoardRecord:
    components, wires, _rail_ids = _circuit_components_and_wires(board)
    return BoardRecord(
        refdes=board.refdes,
        name=board.name,
        revision=board.revision,
        components=components,
        wires=wires,
    )


def _assembly_to_record(circuit: Circuit) -> AssemblyRecord:
    """A Circuit whose factor_nodes are all Boards — i.e. a stacked
    assembly.  Boards' connectors that share nodes are emitted as
    MateRecords."""
    boards = [fn for fn in circuit._factor_nodes if isinstance(fn, Board)]
    if len(boards) != len(circuit._factor_nodes):
        raise ValueError(
            "Assembly Circuit must contain only Boards; found other types"
        )
    board_records = [_board_to_record(b) for b in boards]

    # Identify mate operations: for each pair of boards, walk their
    # connectors and check if their pin externals share nodes.
    mates: list[MateRecord] = []
    seen_pairs: set[frozenset[int]] = set()
    for i, b_a in enumerate(boards):
        for b_b in boards[i + 1:]:
            for c_a in b_a.connectors:
                for c_b in b_b.connectors:
                    if _connectors_mated(c_a, c_b):
                        key = frozenset({id(c_a), id(c_b)})
                        if key in seen_pairs:
                            continue
                        seen_pairs.add(key)
                        mates.append(MateRecord(
                            a=f'{b_a.refdes}.{c_a.refdes}',
                            b=f'{b_b.refdes}.{c_b.refdes}',
                        ))
    mates.sort(key=lambda m: (m.a, m.b))

    # Surface ports of the assembly: map name → "Boardrefdes.connector_refdes.pin_name"
    surface_ports: dict[str, str] = {}
    for name, port in circuit._ports.items():
        ref = _find_assembly_port_ref(port, boards)
        if ref is None:
            raise ValueError(
                f"Cannot resolve assembly surface port {name!r}"
            )
        surface_ports[name] = ref

    return AssemblyRecord(
        boards=sorted(board_records, key=lambda b: b.refdes),
        mates=mates,
        surface_ports=dict(sorted(surface_ports.items())),
    )


def _connectors_mated(a: Connector, b: Connector) -> bool:
    """True if any pin of connector a shares a node with any pin of
    connector b."""
    a_nodes = {id(p.external.node) for p in a.pins if p.external.node is not None}
    b_nodes = {id(p.external.node) for p in b.pins if p.external.node is not None}
    return bool(a_nodes & b_nodes)


def _find_port_ref(
    port: Port,
    components: list[FactorNode],
    rail_ids: dict[int, str],
) -> str | None:
    for component in components:
        for port_name, p in component.ports.items():
            if p is port:
                return _port_ref(_component_id(component, rail_ids), port_name)
    return None


def _find_assembly_port_ref(port: Port, boards: list[Board]) -> str | None:
    for board in boards:
        # Boards expose qualified surface ports like 'J1.p3'.
        for qualified_name, p in board._ports.items():
            if p is port:
                return f'{board.refdes}.{qualified_name}'
    return None


def _looks_like_assembly(circuit: Circuit) -> bool:
    """Heuristic: a Circuit is an assembly iff its factor_nodes are
    all Boards."""
    if not circuit._factor_nodes:
        return False
    return all(isinstance(fn, Board) for fn in circuit._factor_nodes)


def _to_record(root: FactorNode) -> AssemblyRecord | BoardRecord | CircuitRecord:
    if isinstance(root, Board):
        return _board_to_record(root)
    if isinstance(root, Circuit):
        if _looks_like_assembly(root):
            return _assembly_to_record(root)
        return _circuit_to_record(root)
    raise TypeError(
        f"save_circuitry root must be a Board, Assembly, or Circuit; "
        f"got {type(root).__name__}"
    )


@validate_call(config={'arbitrary_types_allowed': True})
def save_circuitry(root: FactorNode, path: Path | str) -> None:
    """Serialise a Circuit / Board / Assembly to a `.circuitry` file."""
    record = _to_record(root)
    file = CircuitryFile(format_version=CURRENT_FORMAT_VERSION, root=record)
    text = json.dumps(
        json.loads(file.model_dump_json()),  # decode/re-encode for indent control
        indent=2,
        sort_keys=False,
        ensure_ascii=False,
    )
    Path(path).write_text(text + '\n')


# -----------------------------------------------------------------
# Loading
# -----------------------------------------------------------------

def _refdes_number_from_refdes(refdes: str) -> int:
    """Extract the integer suffix from a refdes like 'R7' → 7."""
    import re
    m = re.match(r'^[A-Z]+(\d+)$', refdes)
    if m is None:
        raise ValueError(f"Cannot parse refdes_number from {refdes!r}")
    return int(m.group(1))


def _build_component(record: Any) -> FactorNode:
    """Instantiate a live FactorNode from a record."""
    cls = lookup(record.type)
    kwargs: dict[str, Any] = {}
    if hasattr(record, 'refdes'):
        kwargs['refdes_number'] = _refdes_number_from_refdes(record.refdes)
    if record.type == 'Resistor':
        kwargs['ohms'] = record.ohms
    elif record.type == 'Capacitor':
        kwargs['farads'] = record.farads
    elif record.type == 'Inductor':
        kwargs['henries'] = record.henries
    elif record.type == 'Relay_SPDT':
        kwargs['pickup_voltage'] = record.pickup_voltage
    elif record.type == 'LED':
        kwargs['color'] = record.color
    elif record.type == 'Rail':
        kwargs = {'level': record.level}   # Rail takes no refdes_number
    if hasattr(record, 'pin_count') and record.pin_count is not None:
        kwargs['pin_count'] = record.pin_count
    if hasattr(record, 'pitch_mm') and record.pitch_mm is not None:
        kwargs['pitch_mm'] = record.pitch_mm
    return cls(**kwargs)


def _resolve_port(
    ref: str,
    components_by_id: dict[str, FactorNode],
) -> Port:
    """Parse a port reference like 'U1.out_1' and return the live Port."""
    head, _, tail = ref.partition('.')
    if not tail:
        raise ValueError(f"Malformed port reference {ref!r}; expected 'id.port'")
    component = components_by_id.get(head)
    if component is None:
        raise ValueError(f"Unknown component id {head!r} in port reference {ref!r}")
    if tail not in component.ports:
        raise ValueError(
            f"Component {head!r} has no port {tail!r}; "
            f"known: {sorted(component.ports)}"
        )
    return component.ports[tail]


def _rebuild_circuit_components(
    component_records: list[Any],
) -> tuple[list[FactorNode], dict[str, FactorNode]]:
    """Build components from records; return (ordered list, id→component map)."""
    components: list[FactorNode] = []
    by_id: dict[str, FactorNode] = {}
    for rec in component_records:
        c = _build_component(rec)
        components.append(c)
        local_id = rec.refdes if hasattr(rec, 'refdes') else rec.id
        if local_id in by_id:
            raise ValueError(f"Duplicate component id {local_id!r}")
        by_id[local_id] = c
    return components, by_id


def _from_circuit_record(record: CircuitRecord) -> Circuit:
    components, by_id = _rebuild_circuit_components(record.components)
    for w in record.wires:
        ports = [_resolve_port(r, by_id) for r in w.ports]
        wire(*ports)
    surface_ports = {
        name: _resolve_port(ref, by_id)
        for name, ref in record.surface_ports.items()
    }
    return Circuit(factor_nodes=components, ports=surface_ports)


def _from_board_record(record: BoardRecord) -> Board:
    components, by_id = _rebuild_circuit_components(record.components)
    for w in record.wires:
        ports = [_resolve_port(r, by_id) for r in w.ports]
        wire(*ports)
    refdes_number = _refdes_number_from_refdes(record.refdes)
    return Board(
        name=record.name,
        revision=record.revision,
        components=components,
        refdes_number=refdes_number,
    )


def _from_assembly_record(record: AssemblyRecord) -> Circuit:
    boards: list[Board] = [_from_board_record(b) for b in record.boards]
    boards_by_refdes = {b.refdes: b for b in boards}

    # Apply mates.
    for m in record.mates:
        a_board_refdes, _, a_conn_refdes = m.a.partition('.')
        b_board_refdes, _, b_conn_refdes = m.b.partition('.')
        a_board = boards_by_refdes.get(a_board_refdes)
        b_board = boards_by_refdes.get(b_board_refdes)
        if a_board is None or b_board is None:
            raise ValueError(f"Mate {m.a}↔{m.b} references unknown board")
        a_conn = next((c for c in a_board.connectors if c.refdes == a_conn_refdes), None)
        b_conn = next((c for c in b_board.connectors if c.refdes == b_conn_refdes), None)
        if a_conn is None or b_conn is None:
            raise ValueError(f"Mate {m.a}↔{m.b} references unknown connector")
        from framework.mate import mate as mate_fn
        mate_fn(a_conn, b_conn)

    # Resolve assembly-level surface ports.
    surface_ports: dict[str, Port] = {}
    for name, ref in record.surface_ports.items():
        # ref like 'A1.J1.p3' — first segment is the board refdes.
        board_refdes, _, rest = ref.partition('.')
        board = boards_by_refdes.get(board_refdes)
        if board is None:
            raise ValueError(f"Surface port {name!r} references unknown board {board_refdes!r}")
        if rest not in board._ports:
            raise ValueError(
                f"Surface port {name!r} -> {ref!r}: board {board_refdes!r} "
                f"has no port {rest!r}"
            )
        surface_ports[name] = board._ports[rest]

    return Circuit(factor_nodes=list(boards), ports=surface_ports)


def _from_record(record: Any) -> FactorNode:
    if isinstance(record, AssemblyRecord):
        return _from_assembly_record(record)
    if isinstance(record, BoardRecord):
        return _from_board_record(record)
    if isinstance(record, CircuitRecord):
        return _from_circuit_record(record)
    raise TypeError(f"Unknown record type {type(record).__name__}")


def _check_format_version(version: str) -> None:
    major = int(version.split('.', 1)[0])
    expected_major = int(CURRENT_FORMAT_VERSION.split('.', 1)[0])
    if major != expected_major:
        raise ValueError(
            f"Unsupported .circuitry format version {version!r}; "
            f"this loader supports {expected_major}.x.x "
            f"(current is {CURRENT_FORMAT_VERSION})"
        )


@validate_call(config={'arbitrary_types_allowed': True})
def load_circuitry(path: Path | str) -> FactorNode:
    """Load a `.circuitry` file and reconstruct the in-memory model.

    Raises:
        pydantic.ValidationError — schema violation (unknown component
            type, bad refdes pattern, missing required field).
        ValueError — semantic violation (port reference doesn't resolve,
            unknown component id, wiring failure, unsupported major
            version).
        FileNotFoundError — path doesn't exist.
    """
    raw = Path(path).read_text()
    file = CircuitryFile.model_validate_json(raw)
    _check_format_version(file.format_version)
    return _from_record(file.root)
