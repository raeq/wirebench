from __future__ import annotations
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
        return {}

    def _evaluate(self) -> None:
        for fn in self._eval_order:
            fn._evaluate()

    def _topological_sort(self, factor_nodes: list[FactorNode]) -> list[FactorNode]:
        fn_by_id = {id(fn): fn for fn in factor_nodes}

        g = nx.DiGraph()
        g.add_nodes_from(id(fn) for fn in factor_nodes)

        # node id → set of factor node ids that write to it
        node_writers: dict[int, set] = {}
        for fn in factor_nodes:
            for port in fn.ports.values():
                if port.node is not None and port.direction is Direction.OUT:
                    node_writers.setdefault(id(port.node), set()).add(id(fn))

        # edge: writer → reader, for each shared node
        for fn in factor_nodes:
            for port in fn.ports.values():
                if port.node is not None and port.direction is Direction.IN:
                    for writer_id in node_writers.get(id(port.node), ()):
                        if writer_id != id(fn):
                            g.add_edge(writer_id, id(fn))

        if not nx.is_directed_acyclic_graph(g):
            return factor_nodes  # cycles present — SCC fixed-point iteration TBD

        return [fn_by_id[fn_id] for fn_id in nx.topological_sort(g)]
