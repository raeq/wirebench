"""Domain-report Markdown adapter.

Emits one Markdown section per `GroundDomain` in the design — the
parts that live in it, the net counts inside it, and any boundaries
to other domains (handled by isolators).
"""
from __future__ import annotations

__all__ = ['render', 'name_domain_report_net']

from framework.part import Part

from framework.export.base import ExporterContext, register_net_namer
from framework.export.nets import LogicalNet
from framework.export.domain_report.renderer import build_report


def name_domain_report_net(net: LogicalNet, ctx: ExporterContext) -> str:
    """The domain report doesn't reference net names; satisfy the
    registry contract with a deterministic placeholder."""
    return f"N{net.id}"


register_net_namer('domain_report', name_domain_report_net)


def render(design: Part, ctx: ExporterContext) -> str:
    return build_report(design, ctx)
