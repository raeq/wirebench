"""Interface-report Markdown adapter.

Emits one Markdown section per `Board` subclass in the design.  Each
section lists the board's public connectors and a per-pin table of
direction, internal connections, and any role hints derivable from
drive-type or rail context.
"""
from __future__ import annotations

__all__ = ['render', 'name_interface_report_net']

from framework.part import Part

from framework.export.base import ExporterContext, register_net_namer
from framework.export.nets import LogicalNet
from framework.export.interface_report.renderer import build_report


def name_interface_report_net(net: LogicalNet, ctx: ExporterContext) -> str:
    """The interface report doesn't reference net names directly;
    satisfy the registry contract with a deterministic placeholder."""
    return f"N{net.id}"


register_net_namer('interface_report', name_interface_report_net)


def render(design: Part, ctx: ExporterContext) -> str:
    return build_report(design, ctx)
