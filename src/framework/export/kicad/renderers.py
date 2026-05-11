"""Per-component KiCad `(comp ...)` renderers.

Each renderer takes:
    (component, ctx, qualified_refdes, sheetpath_names, sheetpath_tstamps)
and returns a single `(comp ...)` S-expression block.

The board-stack qualification is computed in kicad/__init__.py and
passed in; renderers don't see the hierarchy.
"""
from __future__ import annotations

from framework.board import Board
from framework.chip import Chip
from framework.connector import Connector

from framework.export.base import ExporterContext, register_renderer

from components.passives.led import LED
from components.passives.rail import Rail
from components.passives.resistor import Resistor


def _esc(s: str) -> str:
    """Escape a string for KiCad S-expressions: backslash and quote."""
    return s.replace('\\', '\\\\').replace('"', '\\"')


def _footprint_field(comp) -> str:
    fp = getattr(comp, 'FOOTPRINT', None)
    if fp is None:
        return ''
    return f' (footprint "{_esc(fp)}")'


def _libsource(lib: str, part: str, description: str) -> str:
    return (
        f' (libsource (lib "{_esc(lib)}") (part "{_esc(part)}")'
        f' (description "{_esc(description)}"))'
    )


def _comp_block(qrd: str, value: str, footprint: str,
                libsource: str, names: str, tstamps: str) -> str:
    return (
        f'(comp (ref "{_esc(qrd)}")\n'
        f'      (value "{_esc(value)}"){footprint}{libsource}\n'
        f'      (sheetpath (names "{_esc(names)}") (tstamps "{_esc(tstamps)}")))'
    )


@register_renderer(Resistor, format='kicad')
def render_resistor(r: Resistor, ctx: ExporterContext, qrd: str,
                    names: str, tstamps: str) -> str:
    value = f"{float(r.ohms):g}"
    return _comp_block(
        qrd, value, _footprint_field(r),
        _libsource('Device', 'R', 'Resistor'),
        names, tstamps,
    )


@register_renderer(LED, format='kicad')
def render_led(d: LED, ctx: ExporterContext, qrd: str,
               names: str, tstamps: str) -> str:
    return _comp_block(
        qrd, d.color, _footprint_field(d),
        _libsource('Device', 'LED', 'Light-emitting diode'),
        names, tstamps,
    )


@register_renderer(Chip, format='kicad')
def render_chip(u: Chip, ctx: ExporterContext, qrd: str,
                names: str, tstamps: str) -> str:
    cls = type(u).__name__
    return _comp_block(
        qrd, cls, _footprint_field(u),
        _libsource('IC', cls, cls),
        names, tstamps,
    )


@register_renderer(Rail, format='kicad')
def render_rail(r: Rail, ctx: ExporterContext, qrd: str = '',
                names: str = '/', tstamps: str = '/') -> str:
    # Rails are not parts; their nets are named directly. No comp.
    return ""


@register_renderer(Board, format='kicad')
def render_board(b: Board, ctx: ExporterContext, qrd: str = '',
                 names: str = '/', tstamps: str = '/') -> str:
    # Boards contribute only the sheetpath segment that their
    # children inherit; the adapter handles the walk directly.
    return ""


@register_renderer(Connector, format='kicad')
def render_connector(j: Connector, ctx: ExporterContext, qrd: str,
                     names: str, tstamps: str) -> str:
    cls = type(j).__name__
    value = cls
    pin_count = getattr(j, 'pin_count', None)
    if pin_count is not None:
        value = f"{cls}_{pin_count}"
    return _comp_block(
        qrd, value, _footprint_field(j),
        _libsource('Connector', cls, cls),
        names, tstamps,
    )
