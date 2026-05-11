"""Per-component SPICE renderers.

Each renderer is registered via `@register_renderer(<class>, format='spice')`
and takes `(component, ctx)` returning the SPICE text fragment for that
instance.

Renderers are looked up MRO-aware, so a Connector-base-class renderer
handles every concrete connector subclass automatically.
"""
from __future__ import annotations

from framework.board import Board
from framework.chip import Chip
from framework.circuit import Circuit
from framework.connector import Connector
from framework.factor import FactorNode

from framework.export.base import (
    ExporterContext, SpiceExportConfig, lookup_renderer, register_renderer,
)

from components.chips.cd4043 import CD4043
from components.chips.cd4069 import CD4069
from components.chips.lm393 import LM393
from components.chips.sn74hc04 import SN74HC04
from components.chips.uln2003a import ULN2003A
from components.passives.led import LED
from components.passives.rail import Rail
from components.passives.resistor import Resistor


# ---------------------------------------------------------------------------
# Passives
# ---------------------------------------------------------------------------

@register_renderer(Resistor, format='spice')
def render_resistor(r: Resistor, ctx: ExporterContext) -> str:
    n1 = ctx.net_name(r.ports['t1'])
    n2 = ctx.net_name(r.ports['t2'])
    return f"{r.refdes} {n1} {n2} {float(r.ohms)}"


@register_renderer(LED, format='spice')
def render_led(d: LED, ctx: ExporterContext) -> str:
    anode = ctx.net_name(d.ports['anode'])
    cathode = ctx.net_name(d.ports['cathode'])
    ctx.register_model('D_LED')
    return f"{d.refdes} {anode} {cathode} D_LED"


@register_renderer(Rail, format='spice')
def render_rail(r: Rail, ctx: ExporterContext) -> str:
    # Rail(False) is a passive marker that pins its net to SPICE '0';
    # no source emitted.  Rail(True) emits a DC supply.
    if r.level is False:
        return ""
    cfg = ctx.config
    volts = (
        cfg.default_supply_voltage if isinstance(cfg, SpiceExportConfig) else 5.0
    )
    net = ctx.net_name(r.ports['out'])
    return f"V_{ctx.refdes_of(r)} {net} 0 DC {volts}"


# ---------------------------------------------------------------------------
# Chips — each one emits an X-instance referencing a .SUBCKT in the lib.
# Pins are listed in datasheet pin-number order; the model library must
# declare its .SUBCKT with the same pin list in the same order.
# ---------------------------------------------------------------------------

def _render_chip_xinstance(u, ctx: ExporterContext, model_name: str) -> str:
    nets = [
        ctx.net_name(pin.external)
        for pin in sorted(u.pins, key=lambda p: p.id.number)
    ]
    ctx.register_model(model_name)
    return f"{u.refdes} {' '.join(nets)} {model_name}"


@register_renderer(SN74HC04, format='spice')
def render_sn74hc04(u: SN74HC04, ctx: ExporterContext) -> str:
    return _render_chip_xinstance(u, ctx, 'SN74HC04')


@register_renderer(CD4069, format='spice')
def render_cd4069(u: CD4069, ctx: ExporterContext) -> str:
    return _render_chip_xinstance(u, ctx, 'CD4069')


@register_renderer(LM393, format='spice')
def render_lm393(u: LM393, ctx: ExporterContext) -> str:
    return _render_chip_xinstance(u, ctx, 'LM393')


@register_renderer(CD4043, format='spice')
def render_cd4043(u: CD4043, ctx: ExporterContext) -> str:
    return _render_chip_xinstance(u, ctx, 'CD4043')


@register_renderer(ULN2003A, format='spice')
def render_uln2003a(u: ULN2003A, ctx: ExporterContext) -> str:
    return _render_chip_xinstance(u, ctx, 'ULN2003A')


# ---------------------------------------------------------------------------
# Connectors — transparent to netlist export. The IS_CONDUCTOR walker
# has already collapsed each connector pin into its logical net. One
# registration on the Connector base class handles every subclass via
# MRO lookup.
# ---------------------------------------------------------------------------

@register_renderer(Connector, format='spice')
def render_connector(c: Connector, ctx: ExporterContext) -> str:
    return ""


# ---------------------------------------------------------------------------
# Boards — emit a .SUBCKT definition + an X-instance from the parent.
# Registered on the Board base class so any user Board subclass works.
# ---------------------------------------------------------------------------

@register_renderer(Board, format='spice')
def render_board(b: Board, ctx: ExporterContext) -> str:
    subckt_name = f"{b.refdes}_SUBCKT"
    # Surface pin order: sorted by port name for deterministic emission.
    surface_items = sorted(b.ports.items())
    surface_nets = [ctx.net_name(p) for _, p in surface_items]
    surface_str = ' '.join(surface_nets)

    body: list[str] = [f".SUBCKT {subckt_name} {surface_str}"]
    for child in b._factor_nodes:
        if isinstance(child, Board):
            # Nested board — recurse via its renderer (rare).
            body.append(render_board(child, ctx))
            continue
        try:
            child_renderer = lookup_renderer(type(child), 'spice')
        except KeyError:
            raise
        out = child_renderer(child, ctx)
        if out:
            body.append(out)
    body.append(f".ENDS {subckt_name}")

    instance = f"X{b.refdes} {surface_str} {subckt_name}"
    return instance + "\n" + "\n".join(body)
