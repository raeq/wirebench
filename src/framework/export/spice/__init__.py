"""SPICE adapter.

Renders a `.wirebench` design to a SPICE deck (.cir). Importing this
package executes the @register_renderer decorators in `renderers.py`,
making them discoverable through the framework registry.

Adapter entry point: `render(design, ctx)` — called by the top-level
`export()` API.
"""
from __future__ import annotations

__all__ = ['render', 'name_spice_net']

from framework.circuit import Circuit
from framework.part import Part

from framework.export.base import (
    ExporterContext, SpiceExportConfig, lookup_renderer, register_net_namer,
)
from framework.export.nets import LogicalNet
from framework.export.spice import renderers as _renderers  # noqa: F401
from framework.export.spice.models import format_models_section


# --- SPICE net naming ------------------------------------------------
# Moved out of framework/export/base.py per §6.6. SPICE's conventions:
#   - Rail(False) net → "0" (the SPICE ground convention)
#   - Rail(True)  net → "vcc"
#   - everything else → "net_<n>" (or styled per ExportConfig)
def name_spice_net(net: LogicalNet, ctx: ExporterContext) -> str:
    from components.passives.rail import Rail
    has_gnd = any(
        isinstance(o, Rail) and o.level is False for o, _ in net.ports
    )
    has_vcc = any(
        isinstance(o, Rail) and o.level is True for o, _ in net.ports
    )
    if has_gnd:
        return '0'
    if has_vcc:
        return 'vcc'
    style = ctx.config.net_name_style
    if style == 'qualified' and net.ports:
        owner, port = net.ports[0]
        refdes = getattr(owner, 'refdes', type(owner).__name__)
        return f"{refdes}_{port.name}"
    if style == 'short_hash':
        return f"n{net.id:04x}"
    return f"net_{net.id}"


register_net_namer('spice', name_spice_net)


def _spice_config(ctx: ExporterContext) -> SpiceExportConfig:
    """Promote a plain ExportConfig to SpiceExportConfig defaults."""
    cfg = ctx._config
    if isinstance(cfg, SpiceExportConfig):
        return cfg
    return SpiceExportConfig(**cfg.model_dump())


def render(design: Part, ctx: ExporterContext) -> str:
    """Assemble a complete SPICE deck for `design`."""
    cfg = _spice_config(ctx)

    if cfg.include_header_comment:
        # Per §6.7: deterministic content only — no wall-clock timestamp.
        # Design name is stable; tools can correlate without a date.
        title = getattr(design, 'name', None) or type(design).__name__
        ctx.emit(f"* Exported from wirebench — {title}")

    name = getattr(design, 'name', None) or type(design).__name__
    ctx.emit(f".TITLE {name}")

    # Top-level body: every direct child of the design, dispatched to
    # its registered renderer. Boards emit .SUBCKT blocks inline; chips
    # emit X instances and rely on .SUBCKT defs in the model library.
    children = (
        list(design.parts) if isinstance(design, Circuit) else [design]
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
