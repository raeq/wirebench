"""Markdown rendering for the net report.

One section per logical net.  Header for the document gives summary
counts; each section enumerates the net's drivers, readers, and other
ports, plus a best-effort pull-up annotation when a Resistor on the
same net bridges through to a + Rail.
"""
from __future__ import annotations

from components.passives.rail import Rail
from components.passives.resistor import Resistor
from framework.export.base import ExporterContext
from framework.export.nets import LogicalNet
from framework.export.reports_common import (
    classify_ports,
    collect_surface_parts,
    domain_label,
    port_descriptor,
    port_qualifier,
    refdes_or_class,
    surface_ports_on_net,
)
from framework.part import Part
from framework.port import Port


def build_report(design: Part, ctx: ExporterContext) -> str:
    nets = ctx.logical_nets
    surface = collect_surface_parts(design)
    surface_views = [
        (net, surface_ports_on_net(surface, net.nodes)) for net in nets
    ]
    # Skip nets with no external surface ports — they're internal to a
    # chip's cell mesh and the report's scope is the external view.
    surface_views = [(n, ports) for n, ports in surface_views if ports]
    port_to_net = _build_port_index(surface_views)

    domains = sorted({_first_domain(ports) for _, ports in surface_views})
    title = type(design).__name__
    lines: list[str] = [
        f"# Net Report — {title}",
        "",
        f"{len(surface_views)} logical net(s) across "
        f"{len(domains)} ground domain(s): {', '.join(domains) or '—'}.",
        "",
    ]
    for net, ports in surface_views:
        lines.extend(_render_net(net, ports, port_to_net))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _first_domain(ports: list[tuple[Part, Port]]) -> str:
    for _, port in ports:
        return domain_label(port.domain)
    return domain_label('electrical')


def _build_port_index(
    surface_views: list[tuple[LogicalNet, list[tuple[Part, Port]]]],
) -> dict[int, LogicalNet]:
    """Map `id(port)` → the LogicalNet that port belongs to (external
    surface only).  Used by the pull-up detector to find the net at
    the *other* end of a Resistor without re-walking the design."""
    index: dict[int, LogicalNet] = {}
    for net, ports in surface_views:
        for _, port in ports:
            index[id(port)] = net
    return index


def _render_net(
    net: LogicalNet,
    ports: list[tuple[Part, Port]],
    port_to_net: dict[int, LogicalNet],
) -> list[str]:
    header = f"## Net N{net.id}"
    rail_label = _rail_label(ports)
    if rail_label:
        header = f"{header} — {rail_label}"
    lines = [header, "", f"Domain: {_first_domain(ports)}", ""]

    drivers, readers, bidirs = classify_ports(ports)
    lines.extend(_render_bucket("Drivers", drivers))
    lines.extend(_render_bucket("Readers", readers))
    lines.extend(_render_bucket("Other ports on this net", bidirs))

    pull_up = _detect_pull_up(ports, port_to_net)
    if pull_up is not None:
        lines.append(f"Pull-up path: {pull_up}")
    return lines


def _render_bucket(label: str, items: list[tuple[Part, Port]]) -> list[str]:
    """Markdown for one direction bucket.  Empty buckets are omitted
    so the report doesn't carry a wall of `Readers (0):` headings."""
    if not items:
        return []
    lines = [f"{label} ({len(items)}):"]
    for owner, port in items:
        lines.append(f"- {port_descriptor(owner, port)}")
    lines.append("")
    return lines


def _rail_label(ports: list[tuple[Part, Port]]) -> str | None:
    """If exactly one Rail touches this net, surface its polarity
    (`+ rail` / `− rail`) as part of the section header.  Multiple
    rails on a net is a wiring error the framework would already have
    refused; the report doesn't need to handle that case."""
    rails = [owner for owner, _ in ports if isinstance(owner, Rail)]
    if len(rails) != 1:
        return None
    rail = rails[0]
    level = getattr(rail, 'level', None)
    if level is True:
        return "+ rail"
    if level is False:
        return "− rail"
    return None


def _detect_pull_up(
    ports: list[tuple[Part, Port]],
    port_to_net: dict[int, LogicalNet],
) -> str | None:
    """Best-effort one-hop walk: if this net touches a Resistor whose
    other terminal sits on a net with a Rail(True) (+ rail), the
    Resistor is a pull-up to the supply.  Returns a human-readable
    description, or None if no such path exists."""
    for owner, port in ports:
        if not isinstance(owner, Resistor):
            continue
        other_name = 't2' if port.name == 't1' else 't1'
        other_port = owner.ports.get(other_name)
        if other_port is None:
            continue
        other_net = port_to_net.get(id(other_port))
        if other_net is None:
            continue
        if _other_net_has_high_rail(other_net, owner):
            ohms = getattr(owner, 'ohms', None)
            value = f" ({float(ohms):g} Ω)" if ohms is not None else ""
            return (
                f"{port_qualifier(owner, other_port)} → + rail "
                f"via {refdes_or_class(owner)}{value}"
            )
    return None


def _other_net_has_high_rail(net: LogicalNet, exclude: Part) -> bool:
    return any(
        isinstance(owner, Rail) and owner.level is True
        for owner, _ in net.ports
        if owner is not exclude
    )
