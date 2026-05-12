"""Export every (class, format) pair end-to-end against a one-
component circuit, asserting the export runs to completion and yields
a str.  Complements `test_format_coverage` (which only checks the MRO
lookup succeeds): this exercises the renderer body so branch coverage
sees the actual code paths.

Some classes / formats require setup that this uniform sweep can't
provide (LED's KiCad renderer needs a Board path; etc.).  Those
(class, format) pairs are explicitly listed in `_SKIP_PAIRS` with a
documented reason."""
from __future__ import annotations

import warnings

import pytest

# Trigger registration.
import components.chips        # noqa: F401
import components.connectors   # noqa: F401
import components.diodes       # noqa: F401
import components.passives     # noqa: F401
import components.transistors  # noqa: F401
import framework.board         # noqa: F401
import framework.export.bom      # noqa: F401
import framework.export.dot      # noqa: F401
import framework.export.kicad    # noqa: F401
import framework.export.mermaid  # noqa: F401
import framework.export.spice    # noqa: F401
import framework.export.yosys    # noqa: F401

from framework.circuit import Circuit
from framework.export import export_to_string
from framework.registry import lookup, registered_names


def _passive(name, **kw):
    return lambda n: lookup(name)(refdes_number=n, **kw)


_OVERRIDES = {
    'Resistor':   _passive('Resistor',  ohms=330),
    'Capacitor':  _passive('Capacitor', farads=100e-9),
    'Inductor':   _passive('Inductor',  henries=100e-6),
    'LED':        _passive('LED',       color='red'),
    'Relay_SPDT': lambda n: lookup('Relay_SPDT')(refdes_number=n),
    'Rail':       lambda n: lookup('Rail')(level=True),
    'Header1xNFemale':    lambda n: lookup('Header1xNFemale')(refdes_number=n, pin_count=4, pitch_mm=2.54),
    'Header1xNMale':      lambda n: lookup('Header1xNMale')(refdes_number=n, pin_count=4, pitch_mm=2.54),
    'Header2xNFemale':    lambda n: lookup('Header2xNFemale')(refdes_number=n, pin_count=4, pitch_mm=2.54),
    'Header2xNMale':      lambda n: lookup('Header2xNMale')(refdes_number=n, pin_count=4, pitch_mm=2.54),
    'IDC2xNMale':         lambda n: lookup('IDC2xNMale')(refdes_number=n, pin_count=10, pitch_mm=2.54),
    'IDC2xNSocket':       lambda n: lookup('IDC2xNSocket')(refdes_number=n, pin_count=10, pitch_mm=2.54),
    'ScrewTerminalBlock': lambda n: lookup('ScrewTerminalBlock')(refdes_number=n, pin_count=4, pitch_mm=5.08),
    'JSTPHBoardSide':     lambda n: lookup('JSTPHBoardSide')(refdes_number=n, pin_count=4),
    'JSTPHCableHousing':  lambda n: lookup('JSTPHCableHousing')(refdes_number=n, pin_count=4),
    'JSTXHBoardSide':     lambda n: lookup('JSTXHBoardSide')(refdes_number=n, pin_count=4),
    'JSTXHCableHousing':  lambda n: lookup('JSTXHCableHousing')(refdes_number=n, pin_count=4),
    'JSTSHBoardSide':     lambda n: lookup('JSTSHBoardSide')(refdes_number=n, pin_count=4),
    'JSTSHCableHousing':  lambda n: lookup('JSTSHCableHousing')(refdes_number=n, pin_count=4),
    'JSTGHBoardSide':     lambda n: lookup('JSTGHBoardSide')(refdes_number=n, pin_count=4),
    'JSTGHCableHousing':  lambda n: lookup('JSTGHCableHousing')(refdes_number=n, pin_count=4),
}

_SKIP_CLASSES = {'Board'}


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


@pytest.mark.parametrize('fmt', ['bom', 'dot', 'kicad', 'mermaid', 'spice', 'yosys'])
@pytest.mark.parametrize('name', sorted(set(registered_names()) - _SKIP_CLASSES))
def test_export_runs_to_completion(name, fmt):
    factory = _OVERRIDES.get(name, lambda n: lookup(name)(refdes_number=n))
    part = factory(1)
    wrapper = Circuit(factor_nodes=[part], ports=dict(part.ports))
    out = _silently(export_to_string, wrapper, fmt)
    assert isinstance(out, str)


# Some renderers (Rail/Board/Connector stubs for non-netlist formats)
# are registered for MRO coverage but the format adapter never invokes
# them — rails inline into net names, boards become subgraph clusters,
# connectors are conductors.  Call those renderers directly to keep
# their bodies covered: a future regression that breaks the stub would
# fire when the framework starts using them.

from framework.export.base import (    # noqa: E402
    ExporterContext, lookup_renderer,
)


@pytest.mark.parametrize('fmt', ['bom', 'dot', 'kicad', 'mermaid', 'spice', 'yosys'])
@pytest.mark.parametrize('name', sorted(set(registered_names()) - _SKIP_CLASSES))
def test_renderer_direct_call_runs_to_completion(name, fmt):
    factory = _OVERRIDES.get(name, lambda n: lookup(name)(refdes_number=n))
    part = factory(1)
    wrapper = Circuit(factor_nodes=[part], ports=dict(part.ports))
    ctx = ExporterContext(design=wrapper, format=fmt)
    renderer = lookup_renderer(type(part), fmt)
    # Per-format invocation signature:
    #   bom:   (component, ctx, parent='')
    #   kicad: (component, ctx, qrd, names, tstamps)
    #   others: (component, ctx)
    if fmt == 'bom':
        out = renderer(part, ctx, '')
    elif fmt == 'kicad':
        out = renderer(part, ctx, 'X1', '/', 'tstamp')
    else:
        out = renderer(part, ctx)
    assert isinstance(out, str)
