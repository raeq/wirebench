from __future__ import annotations

import warnings
from collections.abc import Sequence

import networkx as nx  # type: ignore[import-untyped]

from pydantic import validate_call

from framework.errors import (
    CompositeShapeError, FloatingNetError, OrphanWireError, RefdesError,
    ShortCircuitError, UnconnectedPinError,
)
from framework.part import Part
from framework.pin import Pin
from framework.port import Direction, Port
from framework.refdes import RefdesBearing


class Circuit(Part):
    """A composite part: a set of parts wired together.

    Nodes are implicit — they are created by wire() when ports are connected.
    `ports` is the boundary surface: a single dict of name → Port. Each
    Port already declares its Direction (IN, OUT, BIDIR), so an explicit
    inputs/outputs split is redundant and is rejected.

    Evaluation propagates signals through the internal graph in topological order.
    Cycles (SCCs) fall back to the declared order — fixed-point iteration is a
    future extension.
    """

    __slots__ = ('_parts', '_ports', '_eval_order')

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        parts: list[Part] | None = None,
        ports: dict[str, Port] | None = None,
    ) -> None:
        # Auto-collect: if the subclass omits __slots__ and just assigns
        # parts to `self.x = Y(...)` in its __init__ before calling
        # super().__init__(), `parts=None` scans `self.__dict__`
        # for Part-typed values (one level of tuple / list / dict
        # unpacking, so a grouped `self.diodes = (d1, …, d6)` still
        # works).  Insertion order in the dict becomes the order in
        # `_parts`, which the topological-sort fallback relies
        # on when a circuit has a feedback cycle — assign parts in
        # dataflow order if you have one.
        # Distinguish "user asked for an empty circuit" (explicit []) from
        # "auto-collect ran and found nothing" (None → []).  Only the
        # second case triggers Rule 1; the first is a legitimate
        # opt-out used in framework-level tests.
        if parts is None:
            parts = self._auto_collect_parts()
            if not parts:
                raise CompositeShapeError(self._empty_circuit_message())
        if ports is None:
            ports = {}
        self._parts = parts
        self._ports        = ports
        self._validate(parts)
        # Rule 2 runs regardless of how parts was obtained: an
        # incomplete explicit list is just as wrong as a silently-empty
        # auto-collected one.
        self._validate_no_orphan_ports(parts)
        self._eval_order   = self._topological_sort(parts)

    @property
    def parts(self) -> tuple[Part, ...]:
        return tuple(self._parts)

    def _empty_circuit_message(self) -> str:
        """Teaching message for the empty-auto-collect (Rule 1) case."""
        cls = type(self).__name__
        return (
            f"{cls} has no parts after auto-collection. "
            f"Did you forget to store components as `self.<name>` "
            f"attributes? The canonical pattern is:\n\n"
            f"    class {cls}(Circuit):\n"
            f"        def __init__(self) -> None:\n"
            f"            self.r1 = Resistor(330, refdes_number=1)\n"
            f"            # …\n"
            f"            wire(self.r1.t1, …)\n"
            f"            super().__init__()\n\n"
            f"If you really wanted an empty circuit, pass "
            f"`parts=[]` explicitly."
        )

    @staticmethod
    def _collect_net_source_locations(
        net_ports: Sequence[tuple[Part, Port]],
    ) -> list[tuple[str, int]]:
        """Deduped source locations of every `wire()` call that touched
        any port on this net, preserving first-appearance order."""
        collected: list[tuple[str, int]] = []
        seen: set[tuple[str, int]] = set()
        for _, port in net_ports:
            if port.node is None:
                continue
            for loc in port.node.source_locations:
                if loc in seen:
                    continue
                seen.add(loc)
                collected.append(loc)
        return collected

    def _validate_no_orphan_ports(self, parts: list[Part]) -> None:
        """Rule 2: every port wired to a port we know about must itself
        belong to a part we know about.

        Catches the case where the developer used `self.x` for some
        components and local variables for others, leaving wires that
        span the framework's awareness boundary.  Runs whether
        `parts` was auto-collected or passed explicitly — an
        explicit-but-incomplete list is just as broken as a
        silently-incomplete auto-collected one.
        """
        # Collect every port the framework knows about, including each
        # Pin's external and internal faces (Pins live inside chips and
        # connectors, so a port we know about may belong to a Pin
        # transitively).
        known_ports: set[int] = set()
        for fn in parts:
            for port in fn.ports.values():
                known_ports.add(id(port))
            # Pin's external port is what user code sees; the internal
            # face is wired inside the chip and we know about it too.
            for pin in getattr(fn, 'pins', ()):
                known_ports.add(id(pin.external))
                known_ports.add(id(pin.internal))

        for fn in parts:
            for port_name, port in fn.ports.items():
                if port.node is None:
                    continue
                for sibling in port.node.ports:
                    if id(sibling) in known_ports:
                        continue
                    refdes = (getattr(fn, 'refdes', None)
                              or type(fn).__name__)
                    raise OrphanWireError(
                        f"Port '{sibling.name}' is wired into this "
                        f"{type(self).__name__} but its owning component "
                        f"is not in parts.  The wire joins this "
                        f"orphan to '{port_name}' on {refdes}.  Store "
                        f"the orphan as `self.<name> = …` so the "
                        f"framework auto-collects it, or pass "
                        f"`parts=[…]` explicitly listing every "
                        f"part.",
                        source_locations=port.node.source_locations,
                    )

    def _auto_collect_parts(self) -> list[Part]:
        """Collect Part-typed attributes from `self.__dict__`.

        Subclasses that omit `__slots__` can rely on this to populate
        `_parts` automatically.  Visits each instance attribute
        in insertion order: a Part value is added directly;
        tuples, lists, and dicts have their elements (or values for
        dicts) scanned one level deep so that grouped collections
        still contribute their parts.  Duplicates (same `id`) are
        kept only on first encounter.
        """
        try:
            instance_dict = self.__dict__
        except AttributeError:
            raise CompositeShapeError(
                f"{type(self).__name__}.__init__: parts=None "
                "requires an instance __dict__ — omit __slots__ on "
                "composite Circuit subclasses, or pass parts "
                "explicitly."
            )
        collected: list[Part] = []
        seen: set[int] = set()

        def _add(obj: object) -> None:
            if isinstance(obj, Part) and id(obj) not in seen:
                seen.add(id(obj))
                collected.append(obj)

        for value in instance_dict.values():
            if isinstance(value, Part):
                _add(value)
            elif isinstance(value, (list, tuple)):
                for item in value:
                    _add(item)
            elif isinstance(value, dict):
                for item in value.values():
                    _add(item)
            # Anything else (strings, ints, etc.) is silently ignored —
            # the type check is the filter.
        return collected

    # -----------------------------------------------------------------
    # Validation
    # -----------------------------------------------------------------

    def _validate(self, parts: list[Part]) -> None:
        boundary = set(id(p) for p in self._ports.values())

        # A6: mandatory ports must be connected (boundary ports are exempt).
        # Only direct parts — child Circuits validated their own
        # internals at construction.
        unconnected = [
            f"'{type(fn).__name__}.{name}'"
            for fn in parts
            for name, port in fn.ports.items()
            if port.mandatory and not port.connected and id(port) not in boundary
        ]
        if unconnected:
            raise UnconnectedPinError(
                f"Unconnected mandatory port(s): {', '.join(unconnected)}",
                port_refs=tuple(
                    ref.strip("'") for ref in unconnected
                ),
            )

        # Net-aware short-circuit / floating detection.  Delegated to
        # framework.export.nets — the canonical IS_CONDUCTOR walker.
        # Drivers and readers are counted only on real (non-conductor)
        # ports of each net — exactly the behaviour KiCad / Altium /
        # OrCAD ERC implement when reporting shorts across PCB
        # boundaries.
        from framework.export.nets import compute_logical_nets
        shorts: list[str] = []
        short_locations: list[tuple[str, int]] = []
        short_drivers: list[str] = []
        floats: list[str] = []
        float_locations: list[tuple[str, int]] = []
        float_port_refs: list[str] = []
        for net in compute_logical_nets(self):
            outs   = [(o, p) for (o, p) in net.ports if p.direction is Direction.OUT]
            bidirs = [(o, p) for (o, p) in net.ports if p.direction is Direction.BIDIR]

            if len(outs) > 1:
                shorts.append(', '.join(
                    f"'{type(o).__name__}.{p.name}'" for o, p in outs))
                for o, p in outs:
                    short_drivers.append(f"{type(o).__name__}.{p.name}")
                for loc in self._collect_net_source_locations(net.ports):
                    if loc not in short_locations:
                        short_locations.append(loc)
            elif (len(outs) == 0 and len(bidirs) > 1
                  and not net.dynamically_driven):
                # `dynamically_driven` is the designer's explicit
                # assertion that the net is driven through a feedback
                # loop (e.g. op-amp bias divider, RC timing network)
                # rather than statically by an OUT port.  Short-circuit
                # detection above stays strict regardless.
                floats.append(', '.join(
                    f"'{type(o).__name__}.{p.name}'" for o, p in bidirs))
                for o, p in bidirs:
                    float_port_refs.append(f"{type(o).__name__}.{p.name}")
                for loc in self._collect_net_source_locations(net.ports):
                    if loc not in float_locations:
                        float_locations.append(loc)

        if shorts:
            # Carry the structured driver list *only when one net is
            # shorted* — multi-net diagnostics would conflate drivers
            # from independent shorts, and the remediation only fires
            # at the two-driver canonical shape anyway.
            drivers: tuple[str, ...] = (
                tuple(short_drivers) if len(shorts) == 1 else ()
            )
            raise ShortCircuitError(
                "Short circuit on logical net — multiple drivers: "
                + '; '.join(shorts),
                drivers=drivers,
                source_locations=short_locations,
            )
        if floats:
            raise FloatingNetError(
                "Floating logical net — multiple passive BIDIRs with no driver: "
                + '; '.join(floats),
                kind='multi_bidir',
                port_refs=tuple(float_port_refs),
                source_locations=float_locations,
            )

        # Duplicate-refdes detection. Walks only refdes-bearing children
        # of the *direct* parts — child Boards/Circuits manage
        # their own internal refdes namespace.
        seen: dict[tuple[str, int], str] = {}
        collisions: list[str] = []
        for fn in parts:
            if not isinstance(fn, RefdesBearing):
                continue
            key = (fn.REFDES_PREFIX, fn.refdes_number)
            label = f"'{type(fn).__name__}.{fn.refdes}'"
            if key in seen:
                collisions.append(f"{seen[key]} and {label}")
            else:
                seen[key] = label
        if collisions:
            # Single canonical duplicate → carry the refdes string so
            # the remediation can name it.  Multi-collision diagnostics
            # are common enough that a generic suggestion would still
            # apply, but the framework names only the specific case it
            # can be confident about.
            duplicate_refdes = ''
            if len(collisions) == 1:
                # `collisions[0]` is "'X.Rn' and 'Y.Rn'" — extract the
                # shared refdes from the right-hand label.
                tail = collisions[0].rsplit('.', 1)[-1]
                duplicate_refdes = tail.rstrip("'")
            raise RefdesError(
                f"Duplicate refdes: {'; '.join(collisions)}",
                kind='duplicate',
                duplicate_refdes=duplicate_refdes,
            )

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    def evaluate(self) -> None:
        for fn in self._eval_order:
            fn.evaluate()

    def _flatten_for_toposort(self, parts: Sequence[Part]) -> list[Part]:
        """Recursively expand Circuit composites and IS_TRANSPARENT
        components (connectors) into their leaf sub-components, so the
        toposort operates at pin-and-cell granularity.

        Without this, multi-pin parts (a chip with gates on both sides
        of a downstream latch, or a connector with pins flowing in both
        directions through a board) appear as single nodes in the
        dependency graph and form false cycles.  Real EDA tools flatten
        the netlist; this is the framework's equivalent.
        """
        flat: list[Part] = []
        for fn in parts:
            if isinstance(fn, Circuit):
                flat.extend(self._flatten_for_toposort(fn.parts))
            elif getattr(fn, 'IS_TRANSPARENT', False):
                flat.extend(getattr(fn, '_pins', ()))
            else:
                flat.append(fn)
        return flat

    def _topological_sort(self, parts: list[Part]) -> list[Part]:
        # Flatten transparent composites (connectors) and Circuit
        # composites (chips, boards) into their leaf sub-components so
        # the dependency graph operates at pin-and-cell granularity.
        parts = self._flatten_for_toposort(parts)
        fn_by_id = {id(fn): fn for fn in parts}

        g = nx.DiGraph()
        g.add_nodes_from(id(fn) for fn in parts)

        # Per node: collect OUT, BIDIR, IN port owners.
        # The owner recorded is the part from `parts` (Pin /
        # cell / passive); Pins' ports back-reference their owning Pin
        # via Port._owner.
        node_index: dict[int, list[tuple[Part, Port]]] = {}
        node_outs:   dict[int, set[int]] = {}
        node_bidirs: dict[int, list[tuple[Part, Port]]] = {}
        node_ins:    dict[int, set[int]] = {}
        for fn in parts:
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

        def conductor_role(start_port: Port, source_owner: Part) -> str:
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
            frontier: list[tuple[Port, Part]] = [(start_port, source_owner)]
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
            return parts

        return [fn_by_id[fn_id] for fn_id in nx.topological_sort(g)]
