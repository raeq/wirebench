"""Markdown rendering for the domain report.

One section per `GroundDomain` declared in the design.  For each
domain: every refdes-bearing surface part with a port in that domain,
plus any nets whose ports span more than one domain (handled by
isolator chips with ports in both).
"""
from __future__ import annotations

from framework.export.base import ExporterContext
from framework.export.nets import LogicalNet
from framework.export.reports_common import (
    collect_surface_parts,
    domain_label,
    part_description,
    refdes_or_class,
)
from framework.part import Part


def build_report(design: Part, ctx: ExporterContext) -> str:
    nets = ctx.logical_nets
    surface = collect_surface_parts(design)
    parts_by_domain = _index_parts_by_domain(surface)
    domain_names = sorted(parts_by_domain.keys())

    crossings = _detect_crossings(nets, surface)
    title = type(design).__name__

    lines: list[str] = [
        f"# Domain Report — {title}",
        "",
        f"{len(domain_names)} ground domain(s): "
        f"{', '.join(domain_names) or '—'}.",
        "",
    ]
    for name in domain_names:
        lines.extend(_render_domain(name, parts_by_domain[name], nets, crossings))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _index_parts_by_domain(surface: list[Part]) -> dict[str, list[Part]]:
    """Group surface parts by the domain(s) of their ports.  A part
    with ports in two domains (e.g. an isolator chip) appears in both
    groups."""
    out: dict[str, list[Part]] = {}
    for part in surface:
        domains = {domain_label(p.domain) for p in part.ports.values()}
        for d in sorted(domains):
            out.setdefault(d, []).append(part)
    return out


def _detect_crossings(
    nets: list[LogicalNet], surface: list[Part],
) -> dict[tuple[str, str], list[Part]]:
    """Identify parts whose ports span multiple ground domains —
    `wire()` refuses to cross domains, so the only legal way a design
    bridges two domains is a part (isolator chip, opto-coupler, etc.)
    with ports in each.

    Returns a map from `(domain_a, domain_b)` (sorted) → list of
    parts that bridge them."""
    crossings: dict[tuple[str, str], list[Part]] = {}
    for part in surface:
        domains = sorted({domain_label(p.domain) for p in part.ports.values()})
        if len(domains) < 2:
            continue
        for i in range(len(domains)):
            for j in range(i + 1, len(domains)):
                key = (domains[i], domains[j])
                crossings.setdefault(key, []).append(part)
    return crossings


def _render_domain(
    name: str,
    parts: list[Part],
    nets: list[LogicalNet],
    crossings: dict[tuple[str, str], list[Part]],
) -> list[str]:
    refdes_parts = sorted(
        (p for p in parts if getattr(p, 'refdes', None)),
        key=lambda p: str(p.refdes),
    )
    lines = [
        f"## Domain `{name}`",
        "",
        f"Parts in this domain ({len(refdes_parts)}):",
    ]
    for part in refdes_parts:
        lines.append(f"- {part.refdes} (`{part_description(part)}`)")
    lines.append("")

    boundary_keys = [k for k in crossings if name in k]
    boundary_part_ids = {
        id(p) for k in boundary_keys for p in crossings[k]
    }

    # Net classification:
    #   * within  = nets entirely within this domain, untouched by isolators.
    #   * adjacent = nets in this domain that touch an isolator (the
    #     domain-D side of a bridged crossing).  `wire()` refuses real
    #     cross-domain nets, so these are the analogue of the spec's
    #     "nets crossing the boundary".
    within = 0
    adjacent = 0
    for net in nets:
        if not net.ports:
            continue
        domains_on_net = {domain_label(p.domain) for _, p in net.ports}
        if name not in domains_on_net:
            continue
        touches_boundary = any(
            id(owner) in boundary_part_ids for owner, _ in net.ports
        )
        if touches_boundary:
            adjacent += 1
        else:
            within += 1

    if boundary_keys:
        lines.append(f"Boundaries to other domains ({len(boundary_keys)}):")
        for key in sorted(boundary_keys):
            other = key[1] if key[0] == name else key[0]
            isolators = ', '.join(
                f"{p.refdes} (`{type(p).__name__}`)"
                for p in crossings[key] if getattr(p, 'refdes', None)
            )
            lines.append(f"- {other} — crossed via {isolators}")
    else:
        lines.append("Boundaries to other domains: None — single-domain design.")
    lines.append("")

    lines.append(f"Nets entirely within this domain: {within}")
    if adjacent:
        lines.append(
            f"Nets adjacent to this domain's boundary: {adjacent} "
            f"(handled by isolators above)"
        )
    return lines
