"""Breadboard SVG visualiser (format `breadboard`).

Emits a self-contained `.breadboard.svg` document showing how a
wirebench design lays out on a standard 830-pin solderless breadboard.
Sibling of `assembly_guide` (Phase 2.1): the two artefacts share the
same placement layer so the positions named in the assembly guide's
step-by-step build instructions match the components' visible
positions in this SVG.

Refusal (acceptance criterion 7 in `.plans/phase-2.6-spec.md`):
  - SMD parts (`is_breadboard_compatible == False`)
  - Top-level `Board` (one populated PCB)
  - Multi-board designs (nested `Board`s — v1 defers; spec §12)
  - Designs whose placement exceeds 63 positions

Output is a single SVG per top-level `Circuit`. v1 does not produce a
composite multi-Board SVG — that's deferred to v2 per the locked
spec decision (`.plans/phase-2.6-spec.md` §12).
"""
from __future__ import annotations

__all__ = ['render']

from framework.export.base import ExporterContext, register_net_namer
from framework.export.nets import LogicalNet

from framework.export.breadboard.renderer import render  # noqa: F401


def _name_breadboard_net(net: LogicalNet, ctx: ExporterContext) -> str:
    """Net names aren't referenced by the SVG output — colours come
    from the routing layer's own hashing. Emit a deterministic
    placeholder so the registry's net-namer contract is satisfied."""
    return f"net_{net.id}"


register_net_namer('breadboard', _name_breadboard_net)
