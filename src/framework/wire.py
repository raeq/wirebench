import os
import sys
import warnings
from collections.abc import Sequence
from types import FrameType

from pydantic import validate_call

from framework.errors import (
    DomainCrossingError, EmptyWireError, FloatingNetError, NodeMergeError,
    ShortCircuitError, SignalTypeMismatchError,
)
from framework.node import Node
from framework.port import Port, Direction


def _capture_user_call_site() -> tuple[str, int] | None:
    """Walk up the call stack from inside `wire()` to find the first
    frame that isn't inside pydantic's `validate_call` wrapper.

    Returns `(basename, lineno)` of the user's call site, or `None` if
    no caller frame is available or the stack walk fails.  Pydantic
    frames are identified by 'pydantic' appearing in the filename —
    robust across pydantic versions, where the number of wrapper
    frames varies.

    Filenames are normalised to `os.path.basename` so attribution stays
    portable: `.wirebench` files saved on one machine and loaded on
    another won't carry someone else's `/Users/...`/`/home/...`/`C:\\...`
    absolute paths.  Basename collisions across files in a project are
    rare in practice (one demo per file) and the trade-off is worth
    the portability.
    """
    try:
        frame: FrameType | None = sys._getframe(1)  # skip wire() itself
    except ValueError:
        # `sys._getframe` raises ValueError when called at a depth the
        # interpreter can't satisfy — vanishingly rare from inside a
        # real function, but documented behavior worth guarding.
        return None
    while frame is not None:
        filename = frame.f_code.co_filename
        if 'pydantic' not in filename and filename != __file__:
            return (os.path.basename(filename), frame.f_lineno)
        frame = frame.f_back
    return None


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

    The caller's `(filename, lineno)` is captured automatically and
    recorded on the resulting `Node`, then surfaced in framework error
    messages as a `Wired at:` line.  The `.wirebench` loader uses
    `_wire_with_attribution` directly so legacy files without a
    captured source stay unattributed across save → load → save.
    """
    _wire_with_attribution(
        list(ports),
        dynamically_driven=dynamically_driven,
        source_location=_capture_user_call_site(),
    )


def _wire_with_attribution(
    ports: Sequence[Port],
    *,
    dynamically_driven: bool,
    source_location: tuple[str, int] | None,
) -> None:
    """Internal wire-implementation that takes source attribution
    explicitly.  Pass `source_location=None` to mean *no attribution*:
    the resulting Node carries no `source_locations` entry, so
    diagnostics for that net stay free of a fabricated `Wired at:`
    line and the round-tripped `.wirebench` keeps the field omitted.

    Used by the `.wirebench` loader so reconstructed nodes carry the
    original user-source attribution (when present in the file) or
    stay unattributed (when the file pre-dates source-location
    capture).  Not part of the public API — user code should call
    `wire()` and let it auto-capture.
    """
    call_locs: list[tuple[str, int]] = (
        [source_location] if source_location is not None else []
    )

    if not ports:
        raise EmptyWireError(
            "wire() requires at least one port",
            source_locations=call_locs,
        )

    domains = {p.domain for p in ports}
    if len(domains) > 1:
        names = ', '.join(f"'{p.name}' ({p.domain.name})" for p in ports)
        raise DomainCrossingError(
            f"Cannot wire ports across ground domains: {names}",
            port_domains=tuple((p.name, p.domain.name) for p in ports),
            source_locations=call_locs,
        )

    out_ports   = [p for p in ports if p.direction is Direction.OUT]
    bidir_ports = [p for p in ports if p.direction is Direction.BIDIR]
    if len(out_ports) == 0 and len(bidir_ports) == 0:
        raise FloatingNetError(
            "wire() has no driver: all ports are IN — nothing drives the node",
            kind='all_in',
            port_refs=tuple(p.name for p in ports),
            source_locations=call_locs,
        )
    if len(out_ports) > 1:
        names = ', '.join(f"'{p.name}'" for p in out_ports)
        raise ShortCircuitError(
            f"wire() has multiple drivers ({names}) — short circuit",
            drivers=tuple(p.name for p in out_ports),
            source_locations=call_locs,
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
                f"Signal type mismatch in wire(): {details}",
                port_types=tuple(
                    (p.name, p.signal_type.__name__) for p in ports
                ),
                source_locations=call_locs,
            )

    # If any port is already on a node, extend that node (Kirchhoff junction).
    # This is what makes a composite's already-wired boundary port joinable by
    # a parent circuit. Two distinct existing nodes would have to merge — not
    # supported yet (would require rewriting node references on every joined
    # port).
    existing = {id(p.node): p.node for p in ports if p.node is not None}
    if len(existing) > 1:
        names = ', '.join(f"'{p.name}' on {p.node.name}" for p in ports if p.node is not None)
        # Both pre-existing nodes' source-locations help the designer
        # locate the two wire() calls whose nets the merge would join,
        # plus this call site itself.
        merge_locs: list[tuple[str, int]] = list(call_locs)
        for node in existing.values():
            for loc in node.source_locations:
                if loc not in merge_locs:
                    merge_locs.append(loc)
        raise NodeMergeError(
            f"wire() would merge two existing nodes — not supported: {names}",
            source_locations=merge_locs,
        )

    domain = next(iter(domains))
    if existing:
        node = next(iter(existing.values()))
    else:
        name = '—'.join(p.name for p in ports)
        node = Node(name, domain)
    if source_location is not None:
        node._add_source_location(source_location)
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
