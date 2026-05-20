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
from framework.part import Part
from framework.transistor import Transistor

from framework.export.base import (
    ExporterContext, SpiceExportConfig, lookup_renderer, register_renderer,
)

from framework.part import Part

from components.passives.capacitor import Capacitor
from components.passives.cell import Cell
from components.passives.inductor import Inductor
from components.passives.led import LED
from components.passives.ferrite_aerial import FerriteAerial
from components.passives.photoresistor import Photoresistor
from components.passives.variable_capacitor import VariableCapacitor
from components.transducers.antenna import Antenna
from components.transducers.crystal_earpiece import CrystalEarpiece
from components.transducers.earth import Earth
from components.transducers.speaker import Speaker
from components.passives.rail import Rail
from components.passives.resistor import Resistor
from components.relays.spdt import Relay_SPDT


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


@register_renderer(Photoresistor, format='spice')
def render_photoresistor(p: Photoresistor, ctx: ExporterContext) -> str:
    n1 = ctx.net_name(p.ports['t1'])
    n2 = ctx.net_name(p.ports['t2'])
    # Geometric mean of the dark/light values picks a sensible
    # mid-illumination operating point; real SPICE work uses a
    # voltage-controlled resistor with a light-intensity sweep.
    mid = (float(p.dark_ohms) * float(p.light_ohms)) ** 0.5
    return f"{p.refdes} {n1} {n2} {mid}"


@register_renderer(Speaker, format='spice')
def render_speaker(s: Speaker, ctx: ExporterContext) -> str:
    n1 = ctx.net_name(s.ports['t1'])
    n2 = ctx.net_name(s.ports['t2'])
    return f"R{s.refdes_number}_LS {n1} {n2} {float(s.impedance_ohms)}"


@register_renderer(CrystalEarpiece, format='spice')
def render_crystal_earpiece(e: CrystalEarpiece, ctx: ExporterContext) -> str:
    n1 = ctx.net_name(e.ports['t1'])
    n2 = ctx.net_name(e.ports['t2'])
    return f"R{e.refdes_number}_EARP {n1} {n2} {float(e.impedance_ohms)}"


@register_renderer(VariableCapacitor, format='spice')
def render_variable_capacitor(vc: VariableCapacitor, ctx: ExporterContext) -> str:
    n1 = ctx.net_name(vc.ports['t1'])
    n2 = ctx.net_name(vc.ports['t2'])
    # SPICE-side: pick the geometric mean of the tuning range as the
    # nominal operating value.  A real swept-tuning SPICE study uses
    # a parameter sweep across min/max.
    mid = (float(vc.min_farads) * float(vc.max_farads)) ** 0.5
    return f"C{vc.refdes_number}_VC {n1} {n2} {mid}"


@register_renderer(FerriteAerial, format='spice')
def render_ferrite_aerial(fa: FerriteAerial, ctx: ExporterContext) -> str:
    n1 = ctx.net_name(fa.ports['t1'])
    n2 = ctx.net_name(fa.ports['t2'])
    return f"{fa.refdes} {n1} {n2} {float(fa.henries)}"


@register_renderer(Antenna, format='spice')
def render_antenna(a: Antenna, ctx: ExporterContext) -> str:
    # SPICE-side: model the antenna as a small AC voltage source so
    # the surrounding tank network has something to resonate against.
    # Real RF-input SPICE work substitutes a full antenna model.
    net = ctx.net_name(a.ports['out'])
    return f"V_{ctx.refdes_of(a)} {net} 0 AC 1m"


@register_renderer(Earth, format='spice')
def render_earth(e: Earth, ctx: ExporterContext) -> str:
    # SPICE-side: tie the earth net to node 0 via an ideal 0 V
    # source.  Same shape as a Rail(False) but logically a different
    # network role.
    net = ctx.net_name(e.ports['out'])
    return f"V_{ctx.refdes_of(e)} {net} 0 DC 0"


@register_renderer(Relay_SPDT, format='spice')
def render_relay_spdt(k: Relay_SPDT, ctx: ExporterContext) -> str:
    # SPICE has no first-class electromechanical relay primitive; the
    # convention is to emit an X-instance referencing a behavioural
    # subcircuit named after the class.  Pin order matches the
    # Relay_SPDT.PIN_NUMBERS mapping (coil_plus, coil_minus, com, no, nc).
    nets = [
        ctx.net_name(k.ports[n])
        for n in ('coil_plus', 'coil_minus', 'com', 'no', 'nc')
    ]
    ctx.register_model('Relay_SPDT')
    return f"X{k.refdes_number} {' '.join(nets)} Relay_SPDT"


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


@register_renderer(Cell, format='spice')
def render_cell(bt: Cell, ctx: ExporterContext) -> str:
    # Single-cell Li-Ion: ideal DC voltage source between pos and neg
    # at the present open-circuit voltage.  No internal resistance —
    # the voltage-only graph can't carry current anyway.
    pos = ctx.net_name(bt.ports['pos'])
    neg = ctx.net_name(bt.ports['neg'])
    return f"V_{ctx.refdes_of(bt)} {pos} {neg} DC {float(bt.terminal_voltage)}"


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


@register_renderer(Part, format='spice')
def render_part(fn: Part, ctx: ExporterContext) -> str:
    # Concept cells (DiodeOR, FanController, etc.) hold Python-level
    # state without a SPICE primitive equivalent.  Catch-all on
    # Part keeps the netlist clean; specific renderers above
    # always win via MRO.
    return ""


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
    for child in b.parts:
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
