import warnings

from pydantic import validate_call

from framework.errors import (
    DomainCrossingError, EmptyWireError, FloatingNetError, NodeMergeError,
    ShortCircuitError, SignalTypeMismatchError,
)
from framework.node import Node
from framework.port import Port, Direction


@validate_call(config={"arbitrary_types_allowed": True})
def wire(*ports: Port, dynamically_driven: bool = False) -> None:
    """Connect ports together, creating the junction node at their meeting point.

    Enforces:
    - all ports in the same ground domain
    - at most one OUT port; BIDIR ports may also act as drivers (passive elements)
    - at least one OUT or BIDIR (something must be able to drive the node)
    - all ports carry the same signal_type

    Set `dynamically_driven=True` to assert that this node is driven
    through the surrounding feedback loop (e.g. op-amp positive-feedback
    bias dividers, RC timing networks).  The assertion suppresses
    `Circuit._validate`'s multi-BIDIR-no-driver check on this net only.
    Promotion is one-way: once a node is annotated, subsequent wire()
    calls that omit the kwarg do not clear it.
    """
    if not ports:
        raise EmptyWireError("wire() requires at least one port")

    domains = {p.domain for p in ports}
    if len(domains) > 1:
        names = ', '.join(f"'{p.name}' ({p.domain.name})" for p in ports)
        raise DomainCrossingError(
            f"Cannot wire ports across ground domains: {names}"
        )

    out_ports   = [p for p in ports if p.direction is Direction.OUT]
    bidir_ports = [p for p in ports if p.direction is Direction.BIDIR]
    if len(out_ports) == 0 and len(bidir_ports) == 0:
        raise FloatingNetError(
            "wire() has no driver: all ports are IN — nothing drives the node"
        )
    if len(out_ports) > 1:
        names = ', '.join(f"'{p.name}'" for p in out_ports)
        raise ShortCircuitError(
            f"wire() has multiple drivers ({names}) — short circuit"
        )

    from framework.signals import Analog, Digital

    def _base(t: type) -> type:
        if issubclass(t, Digital): return Digital
        if t is Analog:            return Analog   # generic — wildcard for any Analog subtype
        if issubclass(t, Analog):  return t        # specific unit — must match exactly
        return t

    # A BIDIR port declared as the generic `Analog` base class is a
    # *conductor wildcard* — it represents a piece of copper (a chip
    # bond wire, a connector contact, a PCB trace) that carries
    # whatever signal the rest of the circuit puts on it.  When at
    # least one such wildcard is on the wire, we skip the type check
    # entirely: the conductor takes on the type imposed by the other
    # parties.
    has_conductor_wildcard = any(
        p.direction is Direction.BIDIR and p.signal_type is Analog
        for p in ports
    )

    # Bidirectional-only nets carry no committed direction yet, so we don't
    # enforce signal-type agreement on them — the type is settled once a
    # directional port joins the wire (or implicitly, by the components'
    # behavior at evaluation time).
    if not has_conductor_wildcard and any(p.direction is not Direction.BIDIR for p in ports):
        base_types = {_base(p.signal_type) for p in ports}
        # Analog (generic) is compatible with any specific Analog subtype.
        # After discarding the wildcard, all remaining specific types must agree.
        specific = base_types - {Analog}
        if len(specific) > 1 or (Digital in specific and len(base_types) > 1):
            details = ', '.join(f"'{p.name}': {p.signal_type.__name__}" for p in ports)
            raise SignalTypeMismatchError(
                f"Signal type mismatch in wire(): {details}"
            )

    # If any port is already on a node, extend that node (Kirchhoff junction).
    # This is what makes a composite's already-wired boundary port joinable by
    # a parent circuit. Two distinct existing nodes would have to merge — not
    # supported yet (would require rewriting node references on every joined
    # port).
    existing = {id(p.node): p.node for p in ports if p.node is not None}
    if len(existing) > 1:
        names = ', '.join(f"'{p.name}' on {p.node.name}" for p in ports if p.node is not None)
        raise NodeMergeError(
            f"wire() would merge two existing nodes — not supported: {names}"
        )

    domain = next(iter(domains))
    if existing:
        node = next(iter(existing.values()))
    else:
        name = '—'.join(p.name for p in ports)
        node = Node(name, domain)
    for p in ports:
        if p.node is None:
            p.connect(node)   # connect() registers the port with the node

    if dynamically_driven:
        # The annotation is meaningful only on nets the multi-BIDIR-
        # no-driver rule would have flagged.  If this net has an OUT
        # driver or fewer than two BIDIR ports, the annotation is
        # already a no-op — surface a hint so the designer can spot a
        # likely topology misunderstanding without blocking the build.
        if len(out_ports) > 0 or len(bidir_ports) < 2:
            names = ', '.join(f"'{p.name}'" for p in ports)
            # stacklevel=4 hops out through pydantic.validate_call's
            # internal frames so the warning points at the user's
            # wire(...) call site rather than inside this module —
            # matches the convention used by Circuit's feedback-loop
            # warning, which is wrapped the same way.
            warnings.warn(
                f"dynamically_driven=True on net carrying {names} — the "
                "annotation has no effect on this net (it already has a "
                "driver or fewer than two passive BIDIRs). This may "
                "indicate a misunderstanding of the topology.",
                UserWarning,
                stacklevel=4,
            )
        node.dynamically_driven = True
