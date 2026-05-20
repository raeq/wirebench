"""Per-component Mermaid node-declaration renderers."""
from __future__ import annotations

from framework.board import Board
from framework.chip import Chip
from framework.connector import Connector
from framework.diode import Diode
from framework.part import Part
from framework.transistor import Transistor

from framework.export.base import ExporterContext, register_renderer

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


def _mm_label(text: str) -> str:
    """Mermaid labels: quote the entire string and escape `"`."""
    return text.replace('"', '&quot;')


@register_renderer(Resistor, format='mermaid')
def render_resistor(r: Resistor, ctx: ExporterContext) -> str:
    label = f"{r.refdes}<br/>{float(r.ohms):g}Ω"
    return f'{r.refdes}["{_mm_label(label)}"]'


@register_renderer(Capacitor, format='mermaid')
def render_capacitor(c: Capacitor, ctx: ExporterContext) -> str:
    label = f"{c.refdes}<br/>{float(c.farads):g}F"
    return f'{c.refdes}["{_mm_label(label)}"]'


@register_renderer(Inductor, format='mermaid')
def render_inductor(l: Inductor, ctx: ExporterContext) -> str:
    label = f"{l.refdes}<br/>{float(l.henries):g}H"
    return f'{l.refdes}["{_mm_label(label)}"]'


@register_renderer(Photoresistor, format='mermaid')
def render_photoresistor(p: Photoresistor, ctx: ExporterContext) -> str:
    label = f"{p.refdes}<br/>LDR"
    return f'{p.refdes}["{_mm_label(label)}"]'


@register_renderer(Speaker, format='mermaid')
def render_speaker(s: Speaker, ctx: ExporterContext) -> str:
    label = f"{s.refdes}<br/>{float(s.impedance_ohms):g}Ω spkr"
    return f'{s.refdes}["{_mm_label(label)}"]'


@register_renderer(CrystalEarpiece, format='mermaid')
def render_crystal_earpiece(e: CrystalEarpiece, ctx: ExporterContext) -> str:
    label = f"{e.refdes}<br/>crystal"
    return f'{e.refdes}["{_mm_label(label)}"]'


@register_renderer(VariableCapacitor, format='mermaid')
def render_variable_capacitor(vc: VariableCapacitor, ctx: ExporterContext) -> str:
    label = f"{vc.refdes}<br/>{float(vc.min_farads):g}–{float(vc.max_farads):g}F"
    return f'{vc.refdes}["{_mm_label(label)}"]'


@register_renderer(FerriteAerial, format='mermaid')
def render_ferrite_aerial(fa: FerriteAerial, ctx: ExporterContext) -> str:
    label = f"{fa.refdes}<br/>{float(fa.henries):g}H aerial"
    return f'{fa.refdes}["{_mm_label(label)}"]'


@register_renderer(Antenna, format='mermaid')
def render_antenna(a: Antenna, ctx: ExporterContext) -> str:
    label = f"{a.refdes}<br/>Antenna"
    return f'{a.refdes}["{_mm_label(label)}"]'


@register_renderer(Earth, format='mermaid')
def render_earth(e: Earth, ctx: ExporterContext) -> str:
    label = f"{e.refdes}<br/>Earth"
    return f'{e.refdes}["{_mm_label(label)}"]'


@register_renderer(Relay_SPDT, format='mermaid')
def render_relay_spdt(k: Relay_SPDT, ctx: ExporterContext) -> str:
    label = f"{k.refdes}<br/>Relay_SPDT"
    return f'{k.refdes}["{_mm_label(label)}"]'


@register_renderer(LED, format='mermaid')
def render_led(d: LED, ctx: ExporterContext) -> str:
    label = f"{d.refdes}<br/>{d.color} LED"
    return f'{d.refdes}["{_mm_label(label)}"]'


@register_renderer(Chip, format='mermaid')
def render_chip(u: Chip, ctx: ExporterContext) -> str:
    label = f"{u.refdes}<br/>{type(u).__name__}"
    return f'{u.refdes}["{_mm_label(label)}"]'


@register_renderer(Rail, format='mermaid')
def render_rail(r: Rail, ctx: ExporterContext) -> str:
    return ""   # rails inline into vcc/gnd net names


@register_renderer(Cell, format='mermaid')
def render_cell(bt: Cell, ctx: ExporterContext) -> str:
    label = f"{bt.refdes}<br/>Li-Ion 1S"
    return f'{bt.refdes}["{_mm_label(label)}"]'


@register_renderer(Board, format='mermaid')
def render_board(b: Board, ctx: ExporterContext) -> str:
    # Boards become subgraph blocks in the adapter's top level
    # (see mermaid/__init__.py). No node declaration here.
    return ""


@register_renderer(Connector, format='mermaid')
def render_connector(j: Connector, ctx: ExporterContext) -> str:
    # Connectors are conductors and emit nothing in netlist-style
    # exports. Keep a stub for MRO coverage but return empty.
    return ""


@register_renderer(Transistor, format='mermaid')
def render_transistor(t: Transistor, ctx: ExporterContext) -> str:
    label = f"{t.refdes}<br/>{type(t).__name__}"
    return f'{t.refdes}["{_mm_label(label)}"]'


@register_renderer(Diode, format='mermaid')
def render_diode(d: Diode, ctx: ExporterContext) -> str:
    label = f"{d.refdes}<br/>{type(d).__name__}"
    return f'{d.refdes}["{_mm_label(label)}"]'


@register_renderer(Part, format='mermaid')
def render_part(fn: Part, ctx: ExporterContext) -> str:
    return ""   # concept cells: no graph node, no BOM line
