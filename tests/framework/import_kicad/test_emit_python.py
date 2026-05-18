"""Tests for the Python source generator."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from framework.import_kicad import import_kicad_netlist
from framework.import_kicad.emit_python import emit


REPO = Path(__file__).resolve().parents[3]


def test_generated_source_runs_and_constructs_a_circuit(tmp_path):
    _, report = import_kicad_netlist(
        REPO / 'demos' / 'hello_led' / 'docs' / 'HelloLED.net'
    )
    source = emit(report, class_name='HelloLEDImported')
    target = tmp_path / 'imported.py'
    target.write_text(source)

    # Execute the generated source in a fresh namespace; the
    # `if __name__ == '__main__'` block instantiates the design.
    namespace: dict = {'__name__': '__main__'}
    exec(compile(source, str(target), 'exec'), namespace)
    assert 'HelloLEDImported' in namespace


def test_generated_source_contains_part_attributes():
    _, report = import_kicad_netlist(
        REPO / 'demos' / 'hello_led' / 'docs' / 'HelloLED.net'
    )
    source = emit(report, class_name='HelloLEDImported')
    # Expected attributes: self.d1, self.r1, plus the synthesised
    # self.gnd / self.vcc rails.
    assert 'self.d1 = LED' in source
    assert 'self.r1 = Resistor' in source
    assert 'self.vcc = Rail(True)' in source
    assert 'self.gnd = Rail(False)' in source


def test_generated_source_includes_source_path_comment(tmp_path):
    _, report = import_kicad_netlist(
        REPO / 'demos' / 'hello_led' / 'docs' / 'HelloLED.net'
    )
    source = emit(report, source_path='/tmp/test.net')
    assert 'Source: /tmp/test.net' in source


def test_unknown_placeholder_emits_helpful_comment(tmp_path):
    from framework.import_kicad import import_from_ast
    from framework.import_kicad.parser import parse

    ast = parse("""
        (export (version "E")
          (components
            (comp (ref "U1") (value "MysteryChip")
              (libsource (lib "X") (part "MysteryChip"))))
          (nets))
    """)
    _, report = import_from_ast(ast)
    source = emit(report)
    assert 'UnknownPart placeholders' in source
    assert 'make_unknown_part_class' in source
