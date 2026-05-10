from framework.node import Node
from framework.port import Port, Direction


def wire(*ports: Port) -> None:
    """Connect ports together, creating the junction node at their meeting point.

    Enforces:
    - all ports in the same ground domain
    - exactly one OUT port (the driver); multiple INs allowed, zero OUT is an error
    - all ports carry the same signal_type
    """
    if not ports:
        raise ValueError("wire() requires at least one port")

    domains = {p.domain for p in ports}
    if len(domains) > 1:
        names = ', '.join(f"'{p.name}' ({p.domain.name})" for p in ports)
        raise ValueError(f"Cannot wire ports across ground domains: {names}")

    out_ports = [p for p in ports if p.direction is Direction.OUT]
    if len(out_ports) == 0:
        raise ValueError(
            f"wire() has no driver: all ports are IN — nothing drives the node"
        )
    if len(out_ports) > 1:
        names = ', '.join(f"'{p.name}'" for p in out_ports)
        raise ValueError(f"wire() has multiple drivers ({names}) — short circuit")

    from framework.signals import Analog, Digital

    def _base(t: type) -> type:
        if issubclass(t, Digital): return Digital
        if t is Analog:            return Analog   # generic — wildcard for any Analog subtype
        if issubclass(t, Analog):  return t        # specific unit — must match exactly
        return t

    base_types = {_base(p.signal_type) for p in ports}
    # Analog (generic) is compatible with any specific Analog subtype.
    # After discarding the wildcard, all remaining specific types must agree.
    specific = base_types - {Analog}
    if len(specific) > 1 or (Digital in specific and len(base_types) > 1):
        details = ', '.join(f"'{p.name}': {p.signal_type.__name__}" for p in ports)
        raise ValueError(f"Signal type mismatch in wire(): {details}")

    domain = next(iter(domains))
    name = '—'.join(p.name for p in ports)
    node = Node(name, domain)
    for p in ports:
        p.connect(node)
