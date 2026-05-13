"""Assembly-guide Markdown adapter.

Emits a recipe-style Markdown document describing how to build the
design on a standard 830-pin solderless breadboard.  The output has
four sections per spec §5.1 / §6:

  - Title and one-line blurb (from the design's class docstring).
  - **Parts** — table of refdes-bearing parts plus free-form
    prose listing non-electronic items (breadboard, jumpers, supply).
  - **Method** — numbered build steps, one per part placement and
    one per jumper wire, plus a final "verify and power on" step.
  - **Notes & Gotchas** — universal bench warnings, then unique
    per-component warnings collected from each part's `GOTCHAS`
    class attribute.

Refusal: the adapter raises `BreadboardIncompatibleError` for any
design containing SMD parts, or whose top-level design is a `Board` /
multi-board assembly (per spec §10 — multi-board designs aren't
usefully built on a single breadboard).

This adapter is unusual among the export formats in that it produces a
single self-contained Markdown document, not a netlist or schematic
graph.  It uses the same `register_net_namer` plumbing as every other
adapter for consistency, but doesn't reference net names in its
output."""
from __future__ import annotations

from framework.part import Part

from framework.export.base import ExporterContext, register_net_namer
from framework.export.nets import LogicalNet
from framework.export.assembly_guide.recipe import build_recipe


def name_assembly_guide_net(net: LogicalNet, ctx: ExporterContext) -> str:
    """Net names are not referenced by the Markdown output; emit a
    deterministic placeholder so the registry's net-namer contract is
    satisfied."""
    return f"net_{net.id}"


register_net_namer('assembly_guide', name_assembly_guide_net)


def render(design: Part, ctx: ExporterContext) -> str:
    """Produce the full assembly-guide Markdown for `design`."""
    return build_recipe(design)
