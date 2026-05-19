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
    # Resistor → LED chain with explicit power and ground nets. LED's
    # anode and cathode are both mandatory (a real LED with a floating
    # cathode doesn't light), so the importer must land both on driven
    # nets for the resulting circuit to pass ERC.
    text = """
    (export (version "E")
      (components
        (comp (ref "R1") (value "330")
          (libsource (lib "Device") (part "R")))
        (comp (ref "D1") (value "red")
          (libsource (lib "Device") (part "LED"))))
      (nets
        (net (code "1") (name "+5V")
          (node (ref "R1") (pin "1")))
        (net (code "2") (name "Net-(R1-Pad2)")
          (node (ref "R1") (pin "2"))
          (node (ref "D1") (pin "1")))
        (net (code "3") (name "GND")
          (node (ref "D1") (pin "2")))))
    """
    ast = parse(text)
    circuit, report = import_from_ast(ast)
    assert {p.refdes for p in report.parts} == {'R1', 'D1'}
    # The R1↔D1 net is the one "two-pin" net this test asserts about;
    # the two single-node power/ground nets exist only to satisfy
    # mandatory-port wiring.
    two_pin = [n for n in report.nets if len(n.nodes) == 2]
    assert len(two_pin) == 1


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


def test_unknown_placeholder_carries_pin_specs_from_nets():
    """The netlist's `(nets ...)` section is the only place pin
    numbers/names show up; without back-filling them onto each
    KiCadComponent, UnknownPart placeholders would be minted with
    zero pins and any `(node)` referencing them would be silently
    dropped."""
    text = """
    (export (version "E")
      (components
        (comp (ref "U99") (value "MysteryChip")
          (libsource (lib "X") (part "MysteryChip"))))
      (nets
        (net (code "1") (name "data")
          (node (ref "U99") (pin "3") (pinfunction "OUT"))
          (node (ref "U99") (pin "5") (pinfunction "IN")))))
    """
    ast = parse(text)
    circuit, report = import_from_ast(ast)
    placeholder = report.parts[0]
    assert placeholder.is_unknown_placeholder
    # Both pin numbers from the net section should land on the part.
    assert placeholder.pin_specs == ((3, 'OUT'), (5, 'IN'))
    part = next(p for p in circuit.parts if type(p).__name__ == placeholder.klass.__name__)
    pin_numbers = sorted(getattr(part, 'ports_by_number', {}).keys())
    assert pin_numbers == [3, 5]


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
