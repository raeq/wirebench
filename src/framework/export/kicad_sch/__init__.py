"""KiCad schematic adapter (format `kicad_sch`).

Emits a `.kicad_sch` document (KiCad 9, format version 20240618).

Phase 2.5a: syntactic emitter with naive grid placement.
Connectivity is expressed via global labels at pin stubs.
"""
from __future__ import annotations

__all__ = ['render']

from framework.part import Part
from framework.export.base import ExporterContext, register_net_namer
from framework.export.nets import LogicalNet

from framework.export.kicad_sch.renderer import render  # noqa: F401


def _name_kicad_sch_net(net: LogicalNet, ctx: ExporterContext) -> str:
    """Net-naming hook for the kicad_sch format.

    Delegates to the renderer's label logic so the ctx.net_name() API
    returns the same strings the renderer uses for labels.
    """
    from framework.export.kicad_sch.renderer import _label_for_net
    return _label_for_net(net)


register_net_namer('kicad_sch', _name_kicad_sch_net)
