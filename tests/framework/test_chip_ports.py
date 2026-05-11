"""Contract tests for Chip's two-view port surface.

`chip.ports_by_number` is the canonical lookup (datasheet pin number →
external Port).  `chip.ports[name]` is the name-keyed convenience view
that raises on ambiguity when multiple pins share a name.  Iteration
over `chip.ports` visits every pin exactly once: unique-name pins via
their canonical name, duplicated names via `<name>_<ordinal>` where
ordinal is the 1-indexed position among same-named siblings sorted
ascending by pin number.
"""
from __future__ import annotations

from collections.abc import Mapping

import pytest

from components.chips import ATmega2560, SN74HC00
from framework.port_map import PortMap


def test_ports_is_a_portmap_and_a_mapping():
    ic = SN74HC00(refdes_number=1)
    assert isinstance(ic.ports, PortMap)
    assert isinstance(ic.ports, Mapping)


# ----- ports_by_number is canonical ----------------------------------

def test_ports_by_number_lookup():
    mcu = ATmega2560(refdes_number=1)
    assert mcu.ports_by_number[1] is not None
    assert mcu.ports_by_number[10] is not None  # VCC (first)
    assert sorted(mcu.ports_by_number) == list(range(1, 101))


def test_ports_by_number_returns_external_port():
    ic = SN74HC00(refdes_number=1)
    assert ic.ports_by_number[1] is ic.ports['1A']


# ----- ports[name] convenience view ----------------------------------

def test_unique_name_lookup():
    mcu = ATmega2560(refdes_number=1)
    # XTAL1 (pin 34) is unique on this chip — direct access works.
    assert mcu.ports['XTAL1'] is mcu.ports_by_number[34]


def test_ambiguous_name_lookup_raises_clearly():
    mcu = ATmega2560(refdes_number=1)
    with pytest.raises(KeyError) as excinfo:
        _ = mcu.ports['VCC']
    msg = str(excinfo.value)
    assert 'Ambiguous' in msg
    assert "'VCC'" in msg
    for ordinal, pin in [(1, 10), (2, 31), (3, 61), (4, 80)]:
        assert f'VCC_{ordinal} (pin {pin})' in msg
    assert 'ports_by_number' in msg


def test_disambiguated_name_lookup_works():
    mcu = ATmega2560(refdes_number=1)
    # 4 VCC pins at 10, 31, 61, 80 — ordinal-suffixed in ascending order.
    assert mcu.ports['VCC_1'] is mcu.ports_by_number[10]
    assert mcu.ports['VCC_2'] is mcu.ports_by_number[31]
    assert mcu.ports['VCC_3'] is mcu.ports_by_number[61]
    assert mcu.ports['VCC_4'] is mcu.ports_by_number[80]


def test_pin_number_is_canonical_reference():
    mcu = ATmega2560(refdes_number=1)
    assert mcu.ports_by_number[10] is mcu.ports['VCC_1']
    assert mcu.ports_by_number[11] is mcu.ports['GND_1']


# ----- iteration semantics -------------------------------------------

def test_iteration_yields_all_pins_exactly_once():
    mcu = ATmega2560(refdes_number=1)
    keys = list(mcu.ports)
    assert len(keys) == 100
    assert len(set(keys)) == 100


def test_len_returns_pin_count():
    assert len(SN74HC00(refdes_number=1).ports) == 14
    assert len(ATmega2560(refdes_number=1).ports) == 100


def test_iteration_uses_disambiguated_form_for_duplicates():
    mcu = ATmega2560(refdes_number=1)
    keys = set(mcu.ports.keys())
    assert 'VCC' not in keys
    assert {'VCC_1', 'VCC_2', 'VCC_3', 'VCC_4'} <= keys


def test_iteration_uses_canonical_form_for_unique_names():
    mcu = ATmega2560(refdes_number=1)
    keys = set(mcu.ports.keys())
    assert {'XTAL1', 'AVCC', 'AREF'} <= keys


# ----- __contains__ semantics ----------------------------------------

def test_contains():
    mcu = ATmega2560(refdes_number=1)
    assert 'VCC' in mcu.ports          # ambiguous canonical: True
    assert 'VCC_1' in mcu.ports        # disambiguated: True
    assert 'XTAL1' in mcu.ports        # unique: True
    assert 'NONEXISTENT' not in mcu.ports
