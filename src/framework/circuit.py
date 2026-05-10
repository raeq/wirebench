from __future__ import annotations

import warnings

import networkx as nx  # type: ignore[import-untyped]

from framework.factor import FactorNode
from framework.port import Direction, Port
from framework.refdes import RefdesBearing


class Circuit(FactorNode):
    """A composite factor node: a set of factor nodes wired together.

    Nodes are implicit — they are created by wire() when ports are connected.
    `ports` is the boundary surface: a single dict of name → Port. Each
    Port already declares its Direction (IN, OUT, BIDIR), so an explicit
    inputs/outputs split is redundant and is rejected.

    Evaluation propagates signals through the internal graph in topological order.
    Cycles (SCCs) fall back to the declared order — fixed-point iteration is a
    future extension.
    """

    __slots__ = ('_factor_nodes', '_ports', '_eval_order')

    def __init__(
        self,
        factor_nodes: list[FactorNode],
        ports: dict[str, Port],
    ) -> None:
        self._factor_nodes = factor_nodes
        self._ports        = ports
        self._validate(factor_nodes)
        self._eval_order   = self._topological_sort(factor_nodes)

    def _validate(self, factor_nodes: list[FactorNode]) -> None:
        boundary = set(id(p) for p in self._ports.values())

        # A6: mandatory ports must be connected (boundary ports are exempt)
        unconnected = [
            f"'{type(fn).__name__}.{name}'"
            for fn in factor_nodes
            for name, port in fn.ports.items()
            if port.mandatory and not port.connected and id(port) not in boundary
        ]
        if unconnected:
            raise ValueError(
                f"Unconnected mandatory port(s): {', '.join(unconnected)}"
            )

        # Short-circuit detection. Two kinds of conflict:
        #   * 2+ OUT ports on the same node — unconditional drivers fighting.
        #   * 0 OUT + 2+ BIDIR ports on the same node — passive drivers
        #     fighting (two voltage sources pushing into the same wire).
        # A node with 1 OUT and N BIDIRs is fine: the OUT is the
        # unconditional driver, BIDIRs are passive readers (matches the
        # toposort writer/reader resolution in _topological_sort).
        node_outs:   dict[int, list[str]] = {}
        node_bidirs: dict[int, list[str]] = {}
        for fn in factor_nodes:
            for name, port in fn.ports.items():
                if port.node is None:
                    continue
                nid = id(port.node)
                label = f"'{type(fn).__name__}.{name}'"
                if port.direction is Direction.OUT:
                    node_outs.setdefault(nid, []).append(label)
                elif port.direction is Direction.BIDIR:
                    node_bidirs.setdefault(nid, []).append(label)
        shorted: list[list[str]] = []
        for nid in set(node_outs) | set(node_bidirs):
            outs   = node_outs.get(nid, [])
            bidirs = node_bidirs.get(nid, [])
            if len(outs) > 1:
                shorted.append(outs + bidirs)
            elif not outs and len(bidirs) > 1:
                shorted.append(bidirs)
        if shorted:
            detail = '; '.join(', '.join(group) for group in shorted)
            raise ValueError(f"Short circuit — multiple drivers on same node: {detail}")

        # Duplicate-refdes detection. Walks only refdes-bearing children
        # (chips and passives that match the RefdesBearing protocol).
        # Cells inside chips don't satisfy the protocol — they have no
        # REFDES_PREFIX — so they are skipped automatically. Chip's own
        # _validate is therefore a no-op for refdes: its factor_nodes are
        # only Pins and refdes-less cells.
        seen: dict[tuple[str, int], str] = {}
        collisions: list[str] = []
        for fn in factor_nodes:
            if not isinstance(fn, RefdesBearing):
                continue
            key = (fn.REFDES_PREFIX, fn.refdes_number)
            label = f"'{type(fn).__name__}.{fn.refdes}'"
            if key in seen:
                collisions.append(f"{seen[key]} and {label}")
            else:
                seen[key] = label
        if collisions:
            raise ValueError(
                f"Duplicate refdes: {'; '.join(collisions)}"
            )

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    def evaluate(self) -> None:
        for fn in self._eval_order:
            fn.evaluate()

    def _topological_sort(self, factor_nodes: list[FactorNode]) -> list[FactorNode]:
        fn_by_id = {id(fn): fn for fn in factor_nodes}

        g = nx.DiGraph()
        g.add_nodes_from(id(fn) for fn in factor_nodes)

        # Per node: collect OUT and BIDIR factor ids touching it.
        # OUT factors are unconditional writers; BIDIR factors are passive —
        # they write only if no OUT exists on the same node, otherwise they read.
        node_outs:   dict[int, set[int]] = {}
        node_bidirs: dict[int, set[int]] = {}
        node_ins:    dict[int, set[int]] = {}
        for fn in factor_nodes:
            for port in fn.ports.values():
                if port.node is None:
                    continue
                nid = id(port.node)
                if port.direction is Direction.OUT:
                    node_outs.setdefault(nid, set()).add(id(fn))
                elif port.direction is Direction.BIDIR:
                    node_bidirs.setdefault(nid, set()).add(id(fn))
                else:
                    node_ins.setdefault(nid, set()).add(id(fn))

        # Resolve writer/reader role per node
        for nid in set(node_outs) | set(node_bidirs) | set(node_ins):
            outs   = node_outs.get(nid, set())
            bidirs = node_bidirs.get(nid, set())
            ins    = node_ins.get(nid, set())
            if outs:
                writers = outs
                readers = ins | bidirs
            else:
                # No OUT — BIDIRs are the writers; IN ports are readers.
                # Multiple BIDIRs on a passive-only node have no canonical
                # direction, so leave them all as both writers and readers
                # and rely on the cycle fallback if it forms one.
                writers = bidirs
                readers = ins | (bidirs if len(bidirs) > 1 else set())
            for w in writers:
                for r in readers:
                    if w != r:
                        g.add_edge(w, r)

        if not nx.is_directed_acyclic_graph(g):
            warnings.warn(
                "Circuit contains a feedback loop: evaluation order is undefined "
                "and results may be incorrect. Fixed-point iteration is not yet "
                "supported — restructure the circuit to remove the cycle, or "
                "model state explicitly inside a component (e.g. SR latch).",
                RuntimeWarning,
                stacklevel=4,
            )
            return factor_nodes

        return [fn_by_id[fn_id] for fn_id in nx.topological_sort(g)]
