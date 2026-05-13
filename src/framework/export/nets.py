"""Logical-net computation — extracted from `Circuit._validate`.

A *logical net* is a set of electrical Nodes joined through one or more
IS_CONDUCTOR components (Pin, primarily) plus the real (non-conductor)
ports attached to that extended copper region. Two Nodes joined by a
chip's bonded wire or a connector's spring contact are members of the
same logical net.

This is the canonical net-walker for the project. `Circuit._validate`
calls into it for ERC; export adapters call into it for netlist
generation.
"""
from __future__ import annotations

from dataclasses import dataclass

from framework.circuit import Circuit
from framework.part import Part
from framework.port import Port


@dataclass(frozen=True, slots=True)
class LogicalNet:
    """An extended electrical net.

    id     — stable integer index, unique within one walk's output;
              the order matches first-visited order during the walk
              so emission is deterministic.
    nodes  — frozenset of `id(node)` for every Node that composes
              this net.
    ports  — tuple of (owner, port) pairs of real (non-conductor)
              ports attached to this net.  Sorted by owner refdes
              (where applicable) then port name for deterministic
              emission.
    """
    id: int
    nodes: frozenset[int]
    ports: tuple[tuple[Part, Port], ...]


def _collect_components(roots: list[Part]) -> list[Part]:
    """Recursively flatten Circuit composites so Pins buried inside chips
    and connectors are visible to the net walker."""
    result: list[Part] = []
    stack: list[Part] = list(roots)
    while stack:
        fn = stack.pop()
        result.append(fn)
        if isinstance(fn, Circuit):
            stack.extend(fn.parts)
    return result


def _build_node_index(
    components: list[Part],
) -> dict[int, list[tuple[Part, Port]]]:
    """Index every connected Port by `id(node)`.

    For ports owned by a Pin (back-referenced via Port._owner), the
    recorded owner is the Pin — so the walker can call IS_CONDUCTOR
    and other_face on it.  Otherwise the recorded owner is the
    iterating part.
    """
    index: dict[int, list[tuple[Part, Port]]] = {}
    seen_ports: set[int] = set()
    for fn in components:
        for port in fn.ports.values():
            if id(port) in seen_ports:
                continue
            seen_ports.add(id(port))
            if port.node is None:
                continue
            owner = port._owner if port._owner is not None else fn
            index.setdefault(id(port.node), []).append((owner, port))
    return index


def _walk_logical_net(
    start_nid: int,
    index: dict[int, list[tuple[Part, Port]]],
) -> set[int]:
    """All Node ids reachable from `start_nid` through IS_CONDUCTOR
    components.  Stepping through `conductor.other_face(port)` jumps
    from one node to the next, growing the net until no more
    conductors are traversable."""
    net: set[int] = {start_nid}
    frontier: list[int] = [start_nid]
    while frontier:
        nid = frontier.pop()
        for owner, port in index.get(nid, []):
            if not getattr(owner, 'IS_CONDUCTOR', False):
                continue
            other = owner.other_face(port)
            if other.node is None:
                continue
            onid = id(other.node)
            if onid not in net:
                net.add(onid)
                frontier.append(onid)
    return net


def _port_sort_key(owner: Part, port: Port) -> tuple[str, str]:
    refdes = getattr(owner, 'refdes', '')
    return (str(refdes), port.name)


def compute_logical_nets(design: Part) -> list[LogicalNet]:
    """Walk `design` and return one LogicalNet per electrical net.

    The walker descends recursively through Circuit / Board / Chip
    composites and treats every Part with IS_CONDUCTOR=True as a
    pass-through. Each returned LogicalNet contains:

      - the set of underlying Node ids that compose it;
      - the real (non-conductor) ports attached to it, sorted for
        deterministic emission.
    """
    if isinstance(design, Circuit):
        roots = list(design.parts)
    else:
        roots = [design]
    components = _collect_components(roots)
    index = _build_node_index(components)

    nets: list[LogicalNet] = []
    visited: set[int] = set()
    next_id = 0
    # Iterate over node ids in first-encountered order for determinism.
    for fn in components:
        for port in fn.ports.values():
            if port.node is None:
                continue
            nid = id(port.node)
            if nid in visited:
                continue
            membership = _walk_logical_net(nid, index)
            visited |= membership

            real_ports: list[tuple[Part, Port]] = []
            seen_port_ids: set[int] = set()
            for member_nid in membership:
                for owner, p in index.get(member_nid, []):
                    if getattr(owner, 'IS_CONDUCTOR', False):
                        continue
                    if id(p) in seen_port_ids:
                        continue
                    seen_port_ids.add(id(p))
                    real_ports.append((owner, p))
            real_ports.sort(key=lambda op: _port_sort_key(*op))

            nets.append(LogicalNet(
                id=next_id,
                nodes=frozenset(membership),
                ports=tuple(real_ports),
            ))
            next_id += 1
    return nets
