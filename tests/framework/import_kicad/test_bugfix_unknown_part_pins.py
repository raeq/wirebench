"""Regression tests for Bug 2: UnknownPart pin specs must survive the
Python-source emission path so that the generated source constructs
without KeyError on ports_by_number.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from framework.import_kicad import import_from_ast, import_kicad_netlist
from framework.import_kicad.emit_python import emit
from framework.import_kicad.parser import parse


FIXTURES = Path(__file__).parent / 'fixtures'
REPO = Path(__file__).resolve().parents[3]


# ------------------------------------------------------------------ fixture


def test_emit_python_preserves_unknown_part_pin_specs():
    """The emitted source must contain the pin_specs literal for an
    UnknownPart placeholder, not an empty list."""
    _, report = import_kicad_netlist(FIXTURES / 'unmapped_part.net')
    source = emit(report, class_name='UnmappedImported')
    # The fixture's U1 has pins 1 and 2 referenced in nets.
    assert '[(1,' in source or "[(1," in source
    assert 'make_unknown_part_class(' in source
    # Must NOT be the broken hardcoded empty list.
    assert 'make_unknown_part_class(\'MAGIC_THERMISTOR_3000\', [])' not in source
    assert 'make_unknown_part_class("MAGIC_THERMISTOR_3000", [])' not in source


def test_emitted_python_for_unknown_part_constructs(tmp_path):
    """Running the emitted Python source must not raise KeyError on
    ports_by_number — the generated make_unknown_part_class call must
    carry the real pin specs so the placeholder has those ports."""
    _, report = import_kicad_netlist(FIXTURES / 'unmapped_part.net')
    source = emit(report, class_name='UnmappedImported')
    target = tmp_path / 'unmapped.py'
    target.write_text(source)
    namespace: dict = {'__name__': '__main__'}
    exec(compile(source, str(target), 'exec'), namespace)
    assert 'UnmappedImported' in namespace


def test_unknown_part_pin_specs_byte_deterministic():
    """Running the emitter twice on the same report must produce identical
    source.  The pin_specs are sorted in _extract_pin_specs_from_nets so
    the repr() literal is stable across runs."""
    _, report = import_kicad_netlist(FIXTURES / 'unmapped_part.net')
    assert emit(report, class_name='C') == emit(report, class_name='C')


def test_non_placeholder_parts_unaffected():
    """The fix must not change the emitted source for netlists with no
    UnknownPart placeholders.  HelloLED output must be byte-identical
    before and after (regression guard for real-part constructors)."""
    _, report_a = import_kicad_netlist(
        REPO / 'demos' / 'hello_led' / 'docs' / 'HelloLED.net'
    )
    _, report_b = import_kicad_netlist(
        REPO / 'demos' / 'hello_led' / 'docs' / 'HelloLED.net'
    )
    assert emit(report_a, class_name='HelloLEDImported') == emit(
        report_b, class_name='HelloLEDImported'
    )
    # Confirm no make_unknown_part_class in the output at all.
    source = emit(report_a, class_name='HelloLEDImported')
    assert 'make_unknown_part_class' not in source


def test_inline_unknown_part_emit_contains_pin_specs():
    """Inline AST with an explicit unknown part verifies pin_specs flow
    end-to-end without requiring the fixture file.  Uses neutral pin names
    to avoid the PinFunction.POWER/GROUND signal_type constraint."""
    ast = parse("""
        (export (version "E")
          (components
            (comp (ref "U1") (value "WeirdSensor")
              (libsource (lib "X") (part "WeirdSensor"))))
          (nets
            (net (code "1") (name "Net-(U1-Pad1)")
              (node (ref "U1") (pin "1") (pinfunction "DATA")))
            (net (code "2") (name "Net-(U1-Pad2)")
              (node (ref "U1") (pin "2") (pinfunction "CLK")))
          ))
    """)
    _, report = import_from_ast(ast)
    source = emit(report)
    # Both pins must appear in the emitted literal.
    assert "(1, 'DATA')" in source
    assert "(2, 'CLK')" in source
