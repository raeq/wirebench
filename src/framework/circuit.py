from __future__ import annotations
import warnings
import networkx as nx
from framework.factor import FactorNode
from framework.port import Port, Direction


class Circuit(FactorNode):
    """A composite factor node: a set of factor nodes wired together.

    Nodes are implicit — they are created by wire() when ports are connected.
    inputs and outputs are Port references on the boundary components.

    Evaluation propagates signals through the internal graph in topological order.
    Cycles (SCCs) fall back to the declared order — fixed-point iteration is a
    future extension.
    """

    __slots__ = ['_factor_nodes', '_inputs', '_outputs', '_eval_order']

    def __init__(
        self,
        factor_nodes: list[FactorNode],
        inputs: dict[str, Port],
        outputs: dict[str, Port],
    ) -> None:
        self._factor_nodes = factor_nodes
        self._inputs       = inputs
        self._outputs      = outputs
        self._validate(factor_nodes)
        self._eval_order   = self._topological_sort(factor_nodes)

    def _validate(self, factor_nodes: list[FactorNode]) -> None:
        boundary = set(id(p) for p in self._inputs.values()) | \
                   set(id(p) for p in self._outputs.values())

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

        # No two OUT ports may drive the same node (short circuit)
        node_drivers: dict[int, list[str]] = {}
        for fn in factor_nodes:
            for name, port in fn.ports.items():
                if port.direction is Direction.OUT and port.node is not None:
                    nid = id(port.node)
                    node_drivers.setdefault(nid, []).append(
                        f"'{type(fn).__name__}.{name}'"
                    )
        shorted = {nid: drivers for nid, drivers in node_drivers.items() if len(drivers) > 1}
        if shorted:
            detail = '; '.join(', '.join(d) for d in shorted.values())
            raise ValueError(f"Short circuit — multiple drivers on same node: {detail}")

    @property
    def ports(self) -> dict:
        return {**self._inputs, **self._outputs}

    def _evaluate(self) -> None:
        for fn in self._eval_order:
            fn._evaluate()

    def _topological_sort(self, factor_nodes: list[FactorNode]) -> list[FactorNode]:
        fn_by_id = {id(fn): fn for fn in factor_nodes}

        g = nx.DiGraph()
        g.add_nodes_from(id(fn) for fn in factor_nodes)

        # Per node: collect OUT and BIDIR factor ids touching it.
        # OUT factors are unconditional writers; BIDIR factors are passive —
        # they write only if no OUT exists on the same node, otherwise they read.
        node_outs:   dict[int, set] = {}
        node_bidirs: dict[int, set] = {}
        node_ins:    dict[int, set] = {}
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
