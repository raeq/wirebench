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
from framework.diode import Diode
from framework.factor import FactorNode
from framework.transistor import Transistor

from framework.export.base import (
    ExporterContext, SpiceExportConfig, lookup_renderer, register_renderer,
)

from components.passives.capacitor import Capacitor
from components.passives.inductor import Inductor
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


@register_renderer(Capacitor, format='spice')
def render_capacitor(c: Capacitor, ctx: ExporterContext) -> str:
    n1 = ctx.net_name(c.ports['t1'])
    n2 = ctx.net_name(c.ports['t2'])
    return f"{c.refdes} {n1} {n2} {float(c.farads)}"


@register_renderer(Inductor, format='spice')
def render_inductor(l: Inductor, ctx: ExporterContext) -> str:
    n1 = ctx.net_name(l.ports['t1'])
    n2 = ctx.net_name(l.ports['t2'])
    return f"{l.refdes} {n1} {n2} {float(l.henries)}"


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
# Chips — one MRO-dispatched renderer at the Chip base class covers every
# concrete subclass. Each emits an X-instance referencing a .SUBCKT in the
# model library; pins are listed in datasheet pin-number order and the
# .SUBCKT must declare the same pin list in the same order. The model name
# is the chip's class name.
# ---------------------------------------------------------------------------

@register_renderer(Chip, format='spice')
def render_chip(u: Chip, ctx: ExporterContext) -> str:
    model_name = type(u).__name__
    nets = [
        ctx.net_name(pin.external)
        for pin in sorted(u.pins, key=lambda p: p.id.number)
    ]
    ctx.register_model(model_name)
    return f"{u.refdes} {' '.join(nets)} {model_name}"


# ---------------------------------------------------------------------------
# Discretes — transistors (BJT/MOSFET) and diodes.  One MRO-dispatched
# renderer per family; SPICE element prefix and terminal order come from
# the Transistor subclass attributes.  Model name = class name.
# ---------------------------------------------------------------------------

@register_renderer(Transistor, format='spice')
def render_transistor(t: Transistor, ctx: ExporterContext) -> str:
    model_name = type(t).__name__
    nets = [ctx.net_name(t.ports[name]) for name in t._SPICE_PIN_ORDER]
    ctx.register_model(model_name)
    return f"{t._SPICE_PREFIX}{t.refdes_number} {' '.join(nets)} {model_name}"


@register_renderer(Diode, format='spice')
def render_diode(d: Diode, ctx: ExporterContext) -> str:
    model_name = type(d).__name__
    anode = ctx.net_name(d.ports['anode'])
    cathode = ctx.net_name(d.ports['cathode'])
    ctx.register_model(model_name)
    return f"{d.refdes} {anode} {cathode} {model_name}"


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
