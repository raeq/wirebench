"""SPICE adapter.

Renders a `.circuitry` design to a SPICE deck (.cir). Importing this
package executes the @register_renderer decorators in `renderers.py`,
making them discoverable through the framework registry.

Adapter entry point: `render(design, ctx)` — called by the top-level
`export()` API.
"""
from __future__ import annotations

from datetime import datetime

from framework.circuit import Circuit
from framework.factor import FactorNode

from framework.export.base import (
    ExporterContext, SpiceExportConfig, lookup_renderer,
)
from framework.export.spice import renderers as _renderers  # noqa: F401
from framework.export.spice.models import format_models_section


def _spice_config(ctx: ExporterContext) -> SpiceExportConfig:
    """Promote a plain ExportConfig to SpiceExportConfig defaults."""
    cfg = ctx._config
    if isinstance(cfg, SpiceExportConfig):
        return cfg
    return SpiceExportConfig(**cfg.model_dump())


def render(design: FactorNode, ctx: ExporterContext) -> str:
    """Assemble a complete SPICE deck for `design`."""
    cfg = _spice_config(ctx)

    if cfg.include_header_comment:
        ctx.emit(f"* Exported from circuitry — {datetime.now().isoformat(timespec='seconds')}")

    name = getattr(design, 'name', None) or type(design).__name__
    ctx.emit(f".TITLE {name}")

    # Top-level body: every direct child of the design, dispatched to
    # its registered renderer. Boards emit .SUBCKT blocks inline; chips
    # emit X instances and rely on .SUBCKT defs in the model library.
    children = (
        list(design._factor_nodes) if isinstance(design, Circuit) else [design]
    )
    for fn in children:
        try:
            renderer = lookup_renderer(type(fn), 'spice')
        except KeyError:
            # Re-raise with a clearer top-level message.
            raise
        out = renderer(fn, ctx)
        if out:
            ctx.emit(out)

    # Models: either include the library or inline the model bodies.
    if ctx.models_used:
        if cfg.emit_models_inline:
            ctx.emit(format_models_section(ctx.models_used))
        else:
            ctx.emit(f".LIB {cfg.model_library_path}")

    ctx.emit(".END")
    return ctx.output()
