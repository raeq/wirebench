"""Regression tests for Bug 1: rail synthesis must not add a second driver
when a chip's OUT-direction pin already drives a named-rail net.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from framework.errors import ShortCircuitError
from framework.import_kicad import import_from_ast, import_kicad_netlist
from framework.import_kicad.emit_python import emit
from framework.import_kicad.parser import parse


FIXTURES = Path(__file__).parent / 'fixtures'


# ------------------------------------------------------------------ fixture


def test_lm7805_named_output_rail_imports_cleanly():
    """LM7805 OUTPUT (Direction.OUT) driving a +5V net must import without
    raising ShortCircuitError.  No positive Rail must be synthesised for the
    +5V net — only GND Rails are expected (Analog + Digital split)."""
    circuit, report = import_kicad_netlist(
        FIXTURES / 'regulator_with_named_rail.net'
    )
    # The +5V wire_group must have rail_polarity=None — it was wired directly
    # without a synthesised Rail because the LM7805 OUTPUT already drives it.
    plus5v_groups = [g for g in report.wire_groups if g.net_name == '+5V']
    assert plus5v_groups, "+5V net must appear in wire_groups"
    for g in plus5v_groups:
        assert g.rail_polarity is None, (
            f"+5V wire_group must have rail_polarity=None (chip-driven), "
            f"got {g.rail_polarity!r} — importer incorrectly synthesised a Rail."
        )


def test_lm7805_named_output_rail_emits_runnable_python(tmp_path):
    """The emitted Python for a LM7805 + named +5V net must execute without
    exception, proving the importer's wire-group record is consistent."""
    _, report = import_kicad_netlist(
        FIXTURES / 'regulator_with_named_rail.net'
    )
    source = emit(report, class_name='RegulatorImported')
    target = tmp_path / 'regulator.py'
    target.write_text(source)
    namespace: dict = {'__name__': '__main__'}
    exec(compile(source, str(target), 'exec'), namespace)
    assert 'RegulatorImported' in namespace


def test_real_short_still_caught():
    """Two OUT-direction pins on the same +5V net is a real short circuit.
    The fix must not suppress that; the framework should still raise."""
    two_regulators = """
    (export (version "E")
      (components
        (comp (ref "U1") (value "LM7805")
          (libsource (lib "Regulator_Linear") (part "LM7805")))
        (comp (ref "U2") (value "LM7805")
          (libsource (lib "Regulator_Linear") (part "LM7805")))
      )
      (nets
        (net (code "1") (name "+5V")
          (node (ref "U1") (pin "3") (pinfunction "OUTPUT"))
          (node (ref "U2") (pin "3") (pinfunction "OUTPUT"))
        )
      )
    )
    """
    with pytest.raises(ShortCircuitError):
        import_from_ast(parse(two_regulators))


def test_passive_only_named_rail_still_synthesises():
    """A +5V net with only passive (BIDIR) nodes must still get a Rail
    synthesised.  Original behaviour is preserved."""
    passive_only = """
    (export (version "E")
      (components
        (comp (ref "R1") (value "10k")
          (libsource (lib "Device") (part "R")))
        (comp (ref "C1") (value "100n")
          (libsource (lib "Device") (part "C")))
      )
      (nets
        (net (code "1") (name "+5V")
          (node (ref "R1") (pin "1"))
          (node (ref "C1") (pin "1"))
        )
        (net (code "2") (name "GND")
          (node (ref "R1") (pin "2"))
          (node (ref "C1") (pin "2"))
        )
      )
    )
    """
    circuit, report = import_from_ast(parse(passive_only))
    from components.passives.rail import Rail
    rails = [p for p in circuit.parts if isinstance(p, Rail)]
    # One high Rail (+5V) and one low Rail (GND).
    assert len(rails) == 2
    polarities = {g.rail_polarity for g in report.wire_groups}
    assert '+' in polarities
    assert '-' in polarities


def test_od_pin_on_vcc_still_gets_rail_pullup():
    """A BIDIR (open-drain/passive) pin on a vcc net must not suppress Rail
    synthesis.  Resistor terminals are Direction.BIDIR — they are not
    OUT-direction drivers, so already_driven stays False and a Rail is still
    synthesised to drive the net, matching real pull-up wiring behaviour."""
    bidir_on_vcc = """
    (export (version "E")
      (components
        (comp (ref "R1") (value "4k7")
          (libsource (lib "Device") (part "R")))
        (comp (ref "R2") (value "4k7")
          (libsource (lib "Device") (part "R")))
      )
      (nets
        (net (code "1") (name "vcc")
          (node (ref "R1") (pin "1"))
          (node (ref "R2") (pin "1"))
        )
        (net (code "2") (name "GND")
          (node (ref "R1") (pin "2"))
          (node (ref "R2") (pin "2"))
        )
      )
    )
    """
    circuit, report = import_from_ast(parse(bidir_on_vcc))
    from components.passives.rail import Rail
    rails = [p for p in circuit.parts if isinstance(p, Rail)]
    # Both vcc and GND are passive-only — two Rails must be synthesised.
    assert len(rails) == 2, (
        "BIDIR ports on named-rail nets must still get a Rail synthesised."
    )
