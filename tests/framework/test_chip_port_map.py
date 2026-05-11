"""Contract tests for Chip's two-view port surface.

`chip.ports_by_number` is the canonical lookup (datasheet pin number →
external Port).  `chip.ports[name]` is the name-keyed convenience view
that raises on ambiguity when multiple pins share a name.  Iteration
over `chip.ports` always visits every pin via an auto-disambiguated
key (`<name>_<pin_number>` for duplicates).
"""
from __future__ import annotations

import pytest

from components.chips import ATmega2560, RP2040, SN74HC00


# ----- ports_by_number is canonical ----------------------------------

def test_ports_by_number_addresses_every_pin():
    ic = SN74HC00(refdes_number=1)
    assert sorted(ic.ports_by_number) == list(range(1, 15))


def test_ports_by_number_returns_external_port():
    ic = SN74HC00(refdes_number=1)
    assert ic.ports_by_number[1] is ic.ports['1A']


def test_ports_by_number_disambiguates_duplicate_canonical_names():
    mcu = ATmega2560(refdes_number=1)
    # ATmega2560 has 5 VCC pins (10, 31, 61, 80) and AVCC at 100; the
    # number-keyed map resolves each unambiguously.
    vccs = [n for n, p in mcu.ports_by_number.items() if p.name == 'VCC']
    assert sorted(vccs) == [10, 31, 61, 80]


# ----- ports[name] convenience view ----------------------------------

def test_ports_name_lookup_works_for_unique_names():
    ic = SN74HC00(refdes_number=1)
    assert ic.ports['1A'] is ic.ports_by_number[1]
    assert ic.ports['VCC'] is ic.ports_by_number[14]


def test_ports_canonical_name_in_chip_with_no_duplicates():
    # SN74HC00 has unique pin names; canonical access works directly.
    ic = SN74HC00(refdes_number=1)
    for port in ic.ports.values():
        assert ic.ports[port.name] is port


def test_ports_ambiguous_name_raises_with_helpful_message():
    mcu = ATmega2560(refdes_number=1)
    with pytest.raises(KeyError) as excinfo:
        _ = mcu.ports['VCC']
    msg = str(excinfo.value)
    assert 'ambiguous' in msg
    assert 'ports_by_number' in msg
    # Lists the candidate pin numbers and disambiguated names.
    for n in (10, 31, 61, 80):
        assert str(n) in msg


def test_ports_disambiguated_name_resolves():
    mcu = ATmega2560(refdes_number=1)
    # Auto-disambiguated keys for the 4 VCC pins.
    assert mcu.ports['VCC_10'] is mcu.ports_by_number[10]
    assert mcu.ports['VCC_31'] is mcu.ports_by_number[31]


def test_contains_works_for_canonical_and_disambiguated_names():
    mcu = ATmega2560(refdes_number=1)
    assert 'VCC' in mcu.ports          # canonical (ambiguous) — True
    assert 'VCC_10' in mcu.ports       # disambiguated form — True
    assert 'AVCC' in mcu.ports         # unique name — True
    assert 'NOT_A_PIN' not in mcu.ports


def test_unknown_name_raises_plain_keyerror():
    ic = SN74HC00(refdes_number=1)
    with pytest.raises(KeyError):
        _ = ic.ports['NOT_A_REAL_PIN']


# ----- iteration semantics -------------------------------------------

def test_iteration_visits_every_pin_exactly_once():
    mcu = RP2040(refdes_number=1)
    keys = list(mcu.ports)
    assert len(keys) == len(mcu.pins)
    # Every key maps to a distinct Port instance.
    distinct_ports = {id(mcu.ports[k]) for k in keys}
    assert len(distinct_ports) == len(mcu.pins)


def test_iteration_uses_disambiguated_keys_for_duplicates():
    mcu = ATmega2560(refdes_number=1)
    keys = set(mcu.ports.keys())
    # 5 IOVDD-like power pin names are duplicated; canonical 'VCC'
    # never appears alone in keys.
    assert 'VCC' not in keys
    assert {'VCC_10', 'VCC_31', 'VCC_61', 'VCC_80'} <= keys
