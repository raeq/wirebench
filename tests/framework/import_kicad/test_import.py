"""End-to-end import tests, plus round-trip against the demo exports."""
from __future__ import annotations

from pathlib import Path

import pytest

from framework.circuit import Circuit
from framework.errors import LoadError, UnknownPartError
from framework.import_kicad import import_kicad_netlist, import_from_ast
from framework.import_kicad.parser import parse


REPO = Path(__file__).resolve().parents[3]


# ----------------------------------------------------- demo round-trips


def test_imports_hello_led_demo_export():
    circuit, report = import_kicad_netlist(
        REPO / 'demos' / 'hello_led' / 'docs' / 'HelloLED.net'
    )
    refdes = {p.refdes for p in report.parts}
    assert refdes == {'D1', 'R1'}
    assert {p.klass.__name__ for p in report.parts} == {'LED', 'Resistor'}
    assert isinstance(circuit, Circuit)
    # Two synthesised Rails (one + and one −) plus the two real parts.
    kinds = sorted(type(p).__name__ for p in circuit.parts)
    assert kinds == ['LED', 'Rail', 'Rail', 'Resistor']
    assert not report.unresolved


def test_imports_water_alarm_demo_export():
    circuit, report = import_kicad_netlist(
        REPO / 'demos' / 'water_alarm' / 'docs' / 'WaterAlarm.net'
    )
    classes = {p.klass.__name__ for p in report.parts}
    assert {'SN74HC04', 'CD4069', 'CD4043', 'ULN2003A', 'LED', 'Resistor'} <= classes
    assert not report.unresolved


# ----------------------------------------------------- error paths


def test_minimal_netlist_with_one_two_pin_net():
    text = """
    (export (version "E")
      (components
        (comp (ref "R1") (value "330")
          (libsource (lib "Device") (part "R")))
        (comp (ref "D1") (value "red")
          (libsource (lib "Device") (part "LED"))))
      (nets
        (net (code "1") (name "Net-(R1-Pad1)")
          (node (ref "R1") (pin "1"))
          (node (ref "D1") (pin "1")))))
    """
    ast = parse(text)
    circuit, report = import_from_ast(ast)
    assert {p.refdes for p in report.parts} == {'R1', 'D1'}
    assert len([n for n in report.nets if n.nodes]) == 1


def test_strict_mode_raises_on_unmapped_value():
    text = """
    (export (version "E")
      (components
        (comp (ref "U1") (value "WeirdNonExistentChip")
          (libsource (lib "X") (part "WeirdNonExistentChip"))))
      (nets))
    """
    ast = parse(text)
    with pytest.raises(UnknownPartError):
        import_from_ast(ast, strict=True)


def test_non_strict_mode_substitutes_unknown_placeholder():
    text = """
    (export (version "E")
      (components
        (comp (ref "U1") (value "WeirdNonExistentChip")
          (libsource (lib "X") (part "WeirdNonExistentChip"))))
      (nets))
    """
    ast = parse(text)
    circuit, report = import_from_ast(ast, strict=False)
    assert report.unresolved == ['U1']
    assert report.parts[0].is_unknown_placeholder


def test_missing_components_section_raises_load_error():
    text = "(export (version \"E\") (nets))"
    ast = parse(text)
    with pytest.raises(LoadError, match=r"missing a top-level \(components"):
        import_from_ast(ast)


def test_missing_nets_section_raises_load_error():
    text = "(export (version \"E\") (components))"
    ast = parse(text)
    with pytest.raises(LoadError, match=r"missing a top-level \(nets"):
        import_from_ast(ast)
