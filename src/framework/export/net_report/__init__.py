"""Net-report Markdown adapter.

Emits one Markdown section per logical net in the design — what
drives it, what reads it, the ground domain it lives in, and (where
detectable) the pull-up path that supplies its quiescent value.

The data source is `framework.export.nets.compute_logical_nets`; the
report is read-only over the existing model.
"""
from __future__ import annotations

__all__ = ['render', 'name_net_report_net']

from framework.part import Part

from framework.export.base import ExporterContext, register_net_namer
from framework.export.nets import LogicalNet
from framework.export.net_report.renderer import build_report


def name_net_report_net(net: LogicalNet, ctx: ExporterContext) -> str:
    """Net names are referenced in the report body via the synthesised
    `Net N{id}` form; the namer hook is satisfied with the same
    string so the registry contract is met."""
    return f"N{net.id}"


register_net_namer('net_report', name_net_report_net)


def render(design: Part, ctx: ExporterContext) -> str:
    """Produce the full net-report Markdown for `design`."""
    return build_report(design, ctx)
