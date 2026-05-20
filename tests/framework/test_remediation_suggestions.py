"""Per-exception `suggested_remediation()` tests.

For each defect class with a high-confidence canonical shape, the
framework returns a teaching-toned hint.  For shapes where no single
fix dominates, the method returns `None` and lets the designer think
— *silent when confidence is low.*
"""
from __future__ import annotations

import pytest

from framework import errors as E


# ============================================================== positive
# Canonical high-confidence shapes — each class returns a non-empty
# teaching-toned remediation string.


def test_short_circuit_two_drivers_suggests_remove_or_series() -> None:
    e = E.ShortCircuitError(
        "wire() has multiple drivers ('y_1', 'y_2') — short circuit",
        drivers=('y_1', 'y_2'),
    )
    rem = e.suggested_remediation()
    assert rem is not None
    # Names both drivers; offers two alternatives ("OR").
    assert 'y_1' in rem and 'y_2' in rem
    assert ' OR ' in rem
    assert 'wire()' in rem
    assert 'series element' in rem


def test_floating_net_multi_bidir_suggests_rail_or_dynamically_driven() -> None:
    e = E.FloatingNetError(
        "Floating logical net — multiple passive BIDIRs with no driver",
        kind='multi_bidir',
        port_refs=('Resistor.t1', 'Capacitor.t1'),
    )
    rem = e.suggested_remediation()
    assert rem is not None
    assert 'Rail' in rem
    assert 'dynamically_driven=True' in rem
    assert ' OR ' in rem


def test_incompatible_mate_suggests_correct_partner() -> None:
    e = E.IncompatibleMateError(
        "USBAReceptacle mates with USBAPlug, not Audio3p5mmTRSJack",
        partner_class='USBAReceptacle',
        expected_class='USBAPlug',
        actual_class='Audio3p5mmTRSJack',
    )
    rem = e.suggested_remediation()
    assert rem is not None
    assert 'USBAPlug' in rem
    assert 'USBAReceptacle' in rem
    assert 'Audio3p5mmTRSJack' in rem


def test_forbidden_state_sr_latch_suggests_mutually_exclusive() -> None:
    e = E.ForbiddenStateError(
        "Invalid: S and R both active",
        state_signature='sr_latch_both_active',
        port_names=('s', 'r'),
    )
    rem = e.suggested_remediation()
    assert rem is not None
    assert 'mutually-exclusive' in rem
    assert 's' in rem and 'r' in rem
    # Offers an alternative latch type.
    assert ' OR ' in rem
    assert 'D-latch' in rem


def test_signal_type_mismatch_suggests_conversion_element() -> None:
    e = E.SignalTypeMismatchError(
        "Signal type mismatch in wire()",
        port_types=(('a', 'Analog'), ('b', 'Digital')),
    )
    rem = e.suggested_remediation()
    assert rem is not None
    # The three canonical conversion elements named in the spec.
    assert 'comparator' in rem
    assert 'ADC' in rem or 'level-shifter' in rem


def test_signal_type_mismatch_non_analog_digital_returns_none() -> None:
    """`SignalTypeMismatchError` also fires from `Port.drive()` when
    a runtime value can't be coerced to the port's signal_type — e.g.
    a string onto a numeric port.  The Analog↔Digital conversion
    advice doesn't fit that path; the fix there is to supply a
    correctly-typed value, which is design-intent territory.  Gate
    the remediation on the canonical Analog↔Digital shape."""
    # Port.drive() failure path: incoming value's type isn't a signal
    # type at all.
    e = E.SignalTypeMismatchError(
        "port 'in' expects Digital, got str",
        port_types=(('in', 'Digital'), ('<incoming>', 'str')),
    )
    assert e.suggested_remediation() is None

    # Two-Analog mismatch (e.g. Volts vs Amps) — not the canonical
    # Analog↔Digital shape either.
    e = E.SignalTypeMismatchError(
        "Volts vs Amps",
        port_types=(('a', 'Volts'), ('b', 'Amps')),
    )
    assert e.suggested_remediation() is None


def test_refdes_duplicate_suggests_unique_refdes_number() -> None:
    e = E.RefdesError(
        "Duplicate refdes: 'Resistor.R1' and 'Resistor.R1'",
        kind='duplicate',
        duplicate_refdes='R1',
    )
    rem = e.suggested_remediation()
    assert rem is not None
    assert 'refdes_number=' in rem
    assert 'R1' in rem


def test_domain_crossing_suggests_isolator() -> None:
    e = E.DomainCrossingError(
        "Cannot wire ports across ground domains",
        port_domains=(('a', 'electrical'), ('b', 'iso_secondary')),
    )
    rem = e.suggested_remediation()
    assert rem is not None
    assert 'Optocoupler' in rem
    assert 'transformer' in rem
    assert 'isolator' in rem.lower()


def test_unconnected_pin_single_port_suggests_wire_to_source() -> None:
    e = E.UnconnectedPinError(
        "Unconnected mandatory port(s): 'LM7805.in'",
        port_refs=('LM7805.in',),
    )
    rem = e.suggested_remediation()
    assert rem is not None
    assert 'LM7805.in' in rem
    assert 'mandatory' in rem


# ============================================================== negative
# Low-confidence shapes — the method returns None.


def test_short_circuit_three_drivers_returns_none() -> None:
    e = E.ShortCircuitError(
        "three-way short",
        drivers=('a', 'b', 'c'),
    )
    assert e.suggested_remediation() is None


def test_short_circuit_no_driver_data_returns_none() -> None:
    """Diagnostics raised without structured driver info shouldn't
    fabricate a remediation — no information, no suggestion."""
    e = E.ShortCircuitError("legacy short with no drivers attached")
    assert e.suggested_remediation() is None


def test_floating_net_all_in_returns_none() -> None:
    """The wire-time all-IN case isn't a canonical high-confidence
    fix — the user probably forgot a driver entirely, which is design
    intent territory."""
    e = E.FloatingNetError(
        "wire() has no driver: all ports are IN",
        kind='all_in',
        port_refs=('a', 'b'),
    )
    assert e.suggested_remediation() is None


def test_forbidden_state_unknown_signature_returns_none() -> None:
    e = E.ForbiddenStateError(
        "novel forbidden state",
        state_signature='',  # unknown / not catalogued
        port_names=('x', 'y'),
    )
    assert e.suggested_remediation() is None


def test_unconnected_pin_multiple_ports_returns_none() -> None:
    """Multi-port unconnected → the user has a systemic wiring gap; a
    single suggestion for one port would be incomplete."""
    e = E.UnconnectedPinError(
        "Unconnected mandatory port(s): 'A.in', 'B.in'",
        port_refs=('A.in', 'B.in'),
    )
    assert e.suggested_remediation() is None


def test_incompatible_mate_missing_class_info_returns_none() -> None:
    e = E.IncompatibleMateError("legacy bare-message error")
    assert e.suggested_remediation() is None


def test_refdes_unknown_prefix_returns_none() -> None:
    """Unknown-prefix and non-positive-number RefdesError variants have
    no canonical one-line fix — depend on the specific typo."""
    e = E.RefdesError("Unknown refdes prefix 'ZZ'; not in IEEE 315.")
    assert e.suggested_remediation() is None


def test_base_wirebench_error_returns_none() -> None:
    """Default contract on the base class — silence when no override."""
    e = E.WirebenchError("anything")
    assert e.suggested_remediation() is None


def test_unmateable_returns_none() -> None:
    """UnmateableError has no override — fix depends on whether the
    user wants to add a partner part or remove the mate() call."""
    e = E.UnmateableError("USB-A receptacle has no in-model mate")
    assert e.suggested_remediation() is None


# ====================================================== rendering / shape


def test_remediation_appears_as_try_line_in_str_output() -> None:
    """When `suggested_remediation()` returns non-None, `str(e)` ends
    with a `Try: …` paragraph (after Why and Wired at)."""
    e = E.ShortCircuitError(
        "wire() has multiple drivers ('y_1', 'y_2') — short circuit",
        drivers=('y_1', 'y_2'),
    )
    rendered = str(e)
    lines = rendered.splitlines()
    assert any(line.startswith('  Try: ') for line in lines)
    # Order: base → Why → (Wired at) → Try.
    try_idx = next(i for i, l in enumerate(lines) if l.startswith('  Try: '))
    why_idx = next(i for i, l in enumerate(lines) if l.startswith('  Why: '))
    assert why_idx < try_idx


def test_try_line_omitted_when_remediation_is_none() -> None:
    e = E.ShortCircuitError("legacy short")
    assert 'Try:' not in str(e)


# ============================================== discipline-preservation


_BANNED_PHRASES = [
    'bypass',
    'silence',
    'skip the check',
    'disable',
    'ignore the error',
    'except ValueError',
    'except Exception',
    'raise ValueError',
    'raise TypeError',
    '# type: ignore',
]


def _every_high_confidence_remediation() -> list[str]:
    """Build canonical-shape instances of every class with a
    high-confidence remediation and return their suggestion strings."""
    return [
        E.ShortCircuitError(
            "x", drivers=('a', 'b'),
        ).suggested_remediation() or '',
        E.FloatingNetError(
            "x", kind='multi_bidir', port_refs=('a', 'b'),
        ).suggested_remediation() or '',
        E.IncompatibleMateError(
            "x",
            partner_class='USBAReceptacle',
            expected_class='USBAPlug',
            actual_class='Audio3p5mmTRSJack',
        ).suggested_remediation() or '',
        E.ForbiddenStateError(
            "x", state_signature='sr_latch_both_active',
            port_names=('s', 'r'),
        ).suggested_remediation() or '',
        E.SignalTypeMismatchError(
            "x", port_types=(('a', 'Analog'), ('b', 'Digital')),
        ).suggested_remediation() or '',
        E.RefdesError(
            "x", kind='duplicate', duplicate_refdes='R1',
        ).suggested_remediation() or '',
        E.DomainCrossingError(
            "x", port_domains=(('a', 'electrical'), ('b', 'iso')),
        ).suggested_remediation() or '',
        E.UnconnectedPinError(
            "x", port_refs=('LM7805.in',),
        ).suggested_remediation() or '',
    ]


@pytest.mark.parametrize(
    'phrase', _BANNED_PHRASES,
)
def test_no_remediation_suggests_violating_framework_discipline(
    phrase: str,
) -> None:
    """The framework's strictness is the product.  A remediation that
    tells the user to bypass / silence / disable a check would erode
    that — every suggestion must keep the rules intact and propose a
    real circuit-level fix instead."""
    for suggestion in _every_high_confidence_remediation():
        assert phrase.lower() not in suggestion.lower(), (
            f"Remediation suggests violating discipline ({phrase!r} "
            f"present): {suggestion!r}"
        )


def test_every_high_confidence_remediation_is_teaching_toned() -> None:
    """Teaching-toned: explains *what* and offers an alternative when
    one exists, rather than barking imperatives."""
    for suggestion in _every_high_confidence_remediation():
        # Imperative-only language ("DO X." with no context) is bad.
        # We check the gentler shape: contains either a domain noun or
        # an alternative connector ("OR" / "Use …").
        assert any(
            marker in suggestion
            for marker in (' OR ', 'Use `', 'Insert ', 'Wire ', 'Change ', 'Drive ')
        ), f"Remediation isn't teaching-toned: {suggestion!r}"
        assert len(suggestion) > 40, (
            f"Remediation too terse to teach: {suggestion!r}"
        )
