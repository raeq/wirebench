from __future__ import annotations

import warnings

import networkx as nx  # type: ignore[import-untyped]

from pydantic import validate_call

from framework.factor import FactorNode
from framework.pin import Pin
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

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        factor_nodes: list[FactorNode],
        ports: dict[str, Port],
    ) -> None:
        self._factor_nodes = factor_nodes
        self._ports        = ports
        self._validate(factor_nodes)
        self._eval_order   = self._topological_sort(factor_nodes)

    # -----------------------------------------------------------------
    # Validation
    # -----------------------------------------------------------------

    def _validate(self, factor_nodes: list[FactorNode]) -> None:
        boundary = set(id(p) for p in self._ports.values())

        # A6: mandatory ports must be connected (boundary ports are exempt).
        # Only direct factor_nodes — child Circuits validated their own
        # internals at construction.
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

        # Net-aware short-circuit / floating detection.  Delegated to
        # framework.export.nets — the canonical IS_CONDUCTOR walker.
        # Drivers and readers are counted only on real (non-conductor)
        # ports of each net — exactly the behaviour KiCad / Altium /
        # OrCAD ERC implement when reporting shorts across PCB
        # boundaries.
        from framework.export.nets import compute_logical_nets
        shorts: list[str] = []
        floats: list[str] = []
        for net in compute_logical_nets(self):
            outs   = [(o, p) for (o, p) in net.ports if p.direction is Direction.OUT]
            bidirs = [(o, p) for (o, p) in net.ports if p.direction is Direction.BIDIR]

            if len(outs) > 1:
                shorts.append(', '.join(
                    f"'{type(o).__name__}.{p.name}'" for o, p in outs))
            elif len(outs) == 0 and len(bidirs) > 1:
                floats.append(', '.join(
                    f"'{type(o).__name__}.{p.name}'" for o, p in bidirs))

        if shorts:
            raise ValueError(
                "Short circuit on logical net — multiple drivers: "
                + '; '.join(shorts)
            )
        if floats:
            raise ValueError(
                "Floating logical net — multiple passive BIDIRs with no driver: "
                + '; '.join(floats)
            )

        # Duplicate-refdes detection. Walks only refdes-bearing children
        # of the *direct* factor_nodes — child Boards/Circuits manage
        # their own internal refdes namespace.
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

    def _flatten_for_toposort(self, factor_nodes: list[FactorNode]) -> list[FactorNode]:
        """Recursively expand Circuit composites and IS_TRANSPARENT
        components (connectors) into their leaf sub-components, so the
        toposort operates at pin-and-cell granularity.

        Without this, multi-pin parts (a chip with gates on both sides
        of a downstream latch, or a connector with pins flowing in both
        directions through a board) appear as single nodes in the
        dependency graph and form false cycles.  Real EDA tools flatten
        the netlist; this is the framework's equivalent.
        """
        flat: list[FactorNode] = []
        for fn in factor_nodes:
            if isinstance(fn, Circuit):
                flat.extend(self._flatten_for_toposort(fn._factor_nodes))
            elif getattr(fn, 'IS_TRANSPARENT', False):
                flat.extend(getattr(fn, '_pins', ()))
            else:
                flat.append(fn)
        return flat

    def _topological_sort(self, factor_nodes: list[FactorNode]) -> list[FactorNode]:
        # Flatten transparent composites (connectors) and Circuit
        # composites (chips, boards) into their leaf sub-components so
        # the dependency graph operates at pin-and-cell granularity.
        factor_nodes = self._flatten_for_toposort(factor_nodes)
        fn_by_id = {id(fn): fn for fn in factor_nodes}

        g = nx.DiGraph()
        g.add_nodes_from(id(fn) for fn in factor_nodes)

        # Per node: collect OUT, BIDIR, IN port owners.
        # The owner recorded is the factor_node from `factor_nodes` (Pin /
        # cell / passive); Pins' ports back-reference their owning Pin
        # via Port._owner.
        node_index: dict[int, list[tuple[FactorNode, Port]]] = {}
        node_outs:   dict[int, set[int]] = {}
        node_bidirs: dict[int, list[tuple[FactorNode, Port]]] = {}
        node_ins:    dict[int, set[int]] = {}
        for fn in factor_nodes:
            for port in fn.ports.values():
                if port.node is None:
                    continue
                nid = id(port.node)
                node_index.setdefault(nid, []).append((fn, port))
                if port.direction is Direction.OUT:
                    node_outs.setdefault(nid, set()).add(id(fn))
                elif port.direction is Direction.BIDIR:
                    node_bidirs.setdefault(nid, []).append((fn, port))
                else:
                    node_ins.setdefault(nid, set()).add(id(fn))

        def conductor_role(start_port: Port, source_owner: FactorNode) -> str:
            """Walk through conductor chains from `start_port` to find
            the closest non-conductor port and classify the original
            position as 'writer' (downstream of an OUT) or 'reader'
            (upstream of an IN).

            Used only to break direction ambiguity on multi-BIDIR
            conductor nodes (mated connector pins).
            """
            if start_port.node is None:
                return 'unknown'
            visited: set[int] = {id(start_port.node)}
            frontier: list[tuple[Port, FactorNode]] = [(start_port, source_owner)]
            while frontier:
                face, prev_owner = frontier.pop()
                for next_owner, next_port in node_index.get(id(face.node), []):
                    if next_owner is prev_owner:
                        continue
                    if getattr(next_owner, 'IS_CONDUCTOR', False):
                        deeper = next_owner.other_face(next_port)
                        if deeper.node is None:
                            continue
                        dnid = id(deeper.node)
                        if dnid in visited:
                            continue
                        visited.add(dnid)
                        frontier.append((deeper, next_owner))
                    else:
                        if next_port.direction is Direction.OUT:
                            return 'writer'
                        if next_port.direction is Direction.IN:
                            return 'reader'
                        # Non-conductor BIDIR (resistor terminal): treat
                        # as passive — no direction signal.
            return 'unknown'

        # Resolve writer/reader role per node and add toposort edges.
        for nid in set(node_outs) | set(node_bidirs) | set(node_ins):
            outs        = node_outs.get(nid, set())
            bidir_pairs = node_bidirs.get(nid, [])
            ins         = node_ins.get(nid, set())
            bidirs      = {id(fn) for fn, _ in bidir_pairs}
            if outs:
                writers = outs
                readers = ins | bidirs
            elif len(bidir_pairs) > 1:
                # No OUT, multiple BIDIR ports on the same node.  This is
                # typical of mated connector pins: signals flow through
                # via conductor relays.  Classify each BIDIR by walking
                # through it to find the real driver / reader on either
                # side of the chain.
                writers = set()
                readers = set()
                for fn, port in bidir_pairs:
                    owner = port._owner if port._owner is not None else fn
                    if isinstance(owner, Pin):
                        # Walk through the conductor to the far side.
                        far_face = owner.other_face(port)
                        role = conductor_role(far_face, owner)
                        on_external = port is owner._external
                        if role == 'writer':
                            writers.add(id(fn))
                            # Pin is feeding the shared node
                            # (signal flows internal → external).
                            owner._effective_role = (
                                Direction.OUT if on_external else Direction.IN
                            )
                        elif role == 'reader':
                            readers.add(id(fn))
                            # Pin reads from the shared node
                            # (signal flows external → internal).
                            owner._effective_role = (
                                Direction.IN if on_external else Direction.OUT
                            )
                        else:
                            # 'unknown' — no real driver/reader on the
                            # internal side (e.g. an unused mated pin
                            # on the controller side of the connector).
                            # Treat as IN so its evaluate unconditionally
                            # relays external → internal; the internal
                            # face is a dangling node nobody else reads.
                            owner._effective_role = (
                                Direction.IN if on_external else Direction.OUT
                            )
                            # No toposort edge: no ordering constraint.
                    else:
                        # A non-conductor BIDIR (resistor terminal).
                        # Treat as passive — both writer and reader.
                        writers.add(id(fn))
                        readers.add(id(fn))
                readers |= ins
            else:
                # No OUT, one BIDIR — it's the only writer.
                writers = bidirs
                readers = ins
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
