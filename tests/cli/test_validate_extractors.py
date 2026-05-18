"""Unit tests for the per-error-class regex extractors.

These exercise the extractor functions on raw message strings — no
subprocess, no framework imports — so a regression in the regex layer
points straight at the offending pattern.
"""
from __future__ import annotations

from cli.validate_extractors import empty_details, extract


def test_empty_details_schema() -> None:
    d = empty_details()
    assert set(d.keys()) == {
        'refdes', 'pin', 'pins', 'parts', 'nets', 'domain', 'pin_number',
    }
    assert d['refdes']     is None
    assert d['pin']        is None
    assert d['pins']       == []
    assert d['parts']      == []
    assert d['nets']       == []
    assert d['domain']     is None
    assert d['pin_number'] is None


# ---------------------------------------------------------- ShortCircuit


def test_short_circuit_from_wire() -> None:
    msg = "wire() has multiple drivers ('y_1', 'y_2') — short circuit"
    d = extract('ShortCircuitError', msg)
    assert d['pins'] == ['y_1', 'y_2']


def test_short_circuit_from_circuit_validate() -> None:
    msg = "Short circuit on logical net — multiple drivers: 'Rail.out', 'SN74HC04.y_1'"
    d = extract('ShortCircuitError', msg)
    assert d['parts'] == ['Rail', 'SN74HC04']
    assert d['pins']  == ['out', 'y_1']


# ---------------------------------------------------------- FloatingNet


def test_floating_net_extracts_parts_and_pins() -> None:
    msg = (
        "Floating logical net — multiple passive BIDIRs with no driver: "
        "'LM7805.INPUT', 'Header2xNMale.p1'"
    )
    d = extract('FloatingNetError', msg)
    assert d['parts'] == ['LM7805', 'Header2xNMale']
    assert d['pins']  == ['INPUT', 'p1']


# ---------------------------------------------------------- IncompatibleMate


def test_incompatible_mate() -> None:
    msg = 'Header2xNMale mates with Header2xNFemale, not JSTPHCableHousing'
    d = extract('IncompatibleMateError', msg)
    assert d['parts'] == ['Header2xNMale', 'JSTPHCableHousing']


# ---------------------------------------------------------- PartConfiguration


def test_part_config_out_no_cell() -> None:
    msg = (
        "SN74HC04 declares pin 'OUTPUT' (pin 2) as Direction.OUT but no "
        "behavioural cell drives its internal face."
    )
    d = extract('PartConfigurationError', msg)
    assert d['parts']      == ['SN74HC04']
    assert d['pin']        == 'OUTPUT'
    assert d['pin_number'] == 2


def test_part_config_drive_wrong_direction() -> None:
    msg = "LM393 declares pin 'OUT1' as 'open_collector' but its direction is 'in'"
    d = extract('PartConfigurationError', msg)
    assert d['parts'] == ['LM393']
    assert d['pin']   == 'OUT1'


def test_part_config_typo_entry() -> None:
    msg = (
        "LM393 declares PIN_DRIVE_TYPES entry 'OUTT'='open_collector' "
        "but no pin has that name on this chip."
    )
    d = extract('PartConfigurationError', msg)
    assert d['parts'] == ['LM393']
    assert d['pin']   == 'OUTT'


# ---------------------------------------------------------- PartParameter


def test_part_parameter_pin_function() -> None:
    msg = (
        "pin 5 (RESET) has pin function 'reset' but signal_type is "
        "Analog; reset pins must be Digital."
    )
    d = extract('PartParameterError', msg)
    assert d['pin_number'] == 5
    assert d['pin']        == 'RESET'


# ---------------------------------------------------------- DomainCrossing


def test_domain_crossing_extracts_pins_and_domain() -> None:
    msg = "Cannot wire ports across ground domains: 'a' (electrical), 'b' (ISOLATED_A)"
    d = extract('DomainCrossingError', msg)
    assert d['pins']   == ['a', 'b']
    assert d['domain'] == 'ISOLATED_A'


# ---------------------------------------------------------- BreadboardIncompatible


def test_breadboard_incompatible_single_bullet() -> None:
    msg = (
        "Chips have unwired supply pins — the assembled circuit won't power up. "
        "Wire each pin below to its rail in the design source:\n"
        "  - U1 pin 14 (VCC) [power] — wire to the + rail"
    )
    d = extract('BreadboardIncompatibleError', msg)
    assert d['parts'] == ['U1']
    assert d['pins']  == ['VCC']


def test_breadboard_incompatible_multi_bullet() -> None:
    msg = (
        "Chips have unwired supply pins — the assembled circuit won't power up. "
        "Wire each pin below to its rail in the design source:\n"
        "  - U1 pin 7 (GND) [ground] — wire to the − rail\n"
        "  - U2 pin 14 (VCC) [power] — wire to the + rail"
    )
    d = extract('BreadboardIncompatibleError', msg)
    assert d['parts'] == ['U1', 'U2']
    assert d['pins']  == ['GND', 'VCC']


# ---------------------------------------------------------- unknown class


def test_unknown_error_class_returns_defaults() -> None:
    d = extract('SomeNewError', 'a message we cannot parse')
    assert d == empty_details()


def test_unmatched_message_returns_defaults() -> None:
    # Same class, but message doesn't fit any pattern.
    d = extract('ShortCircuitError', 'a message in a bottle')
    assert d == empty_details()
