"""Datasheet pin-number assertions for every chip in the codebase.

For each chip class, walk its factor nodes, filter to Pin instances,
and check that the (number, name) pairs match the manufacturer's
datasheet pinout per docs/pin-id-spec.md §7.x.
"""
from __future__ import annotations

import pytest

from framework.pin import Pin, PinId
from components.chips.sn74hc04 import SN74HC04
from components.chips.cd4069 import CD4069
from components.chips.lm393 import LM393
from components.chips.cd4043 import CD4043
from components.chips.uln2003a import ULN2003A


def _pin_set(chip) -> set[tuple[int, str]]:
    return {
        (fn.id.number, fn.id.name)
        for fn in chip._factor_nodes
        if isinstance(fn, Pin)
    }


# --- §7.1 SN74HC04 — 14-pin DIP, hex inverter ---

def test_sn74hc04_pin_numbers_match_datasheet():
    chip = SN74HC04(refdes_number=1)
    expected = {
        (1, 'a_1'), (2, 'y_1'),
        (3, 'a_2'), (4, 'y_2'),
        (5, 'a_3'), (6, 'y_3'),
        (8, 'y_4'), (9, 'a_4'),
        (10, 'y_5'), (11, 'a_5'),
        (12, 'y_6'), (13, 'a_6'),
    }
    assert _pin_set(chip) == expected


# --- §7.2 CD4069 — same DIP layout ---

def test_cd4069_pin_numbers_match_datasheet():
    chip = CD4069(refdes_number=1)
    expected = {
        (1, 'a_1'), (2, 'y_1'),
        (3, 'a_2'), (4, 'y_2'),
        (5, 'a_3'), (6, 'y_3'),
        (8, 'y_4'), (9, 'a_4'),
        (10, 'y_5'), (11, 'a_5'),
        (12, 'y_6'), (13, 'a_6'),
    }
    assert _pin_set(chip) == expected


# --- §7.3 LM393 — 8-pin DIP, dual comparator ---

def test_lm393_pin_numbers_match_datasheet():
    chip = LM393(refdes_number=1)
    expected = {
        (1, 'out_1'),
        (2, 'v_minus_1'),
        (3, 'v_plus_1'),
        (5, 'v_plus_2'),
        (6, 'v_minus_2'),
        (7, 'out_2'),
    }
    assert _pin_set(chip) == expected


# --- §7.4 CD4043 — 16-pin DIP, quad NOR latch ---

def test_cd4043_pin_numbers_match_datasheet():
    chip = CD4043(refdes_number=1)
    expected = {
        (1, 'q_1'), (2, 'r_1'), (3, 's_1'),
        (4, 'q_2'), (5, 's_2'), (6, 'r_2'),
        (7, 'oe'),
        (9, 'r_3'), (10, 's_3'), (11, 'q_3'),
        (12, 's_4'), (13, 'r_4'), (14, 'q_4'),
    }
    assert _pin_set(chip) == expected


# --- §7.5 ULN2003A — 16-pin DIP, Darlington array ---

def test_uln2003a_pin_numbers_match_datasheet():
    chip = ULN2003A(refdes_number=1)
    # in_i at pin i; out_i at pin (17 - i) — outputs reversed.
    expected = {
        (1, 'in_1'), (2, 'in_2'), (3, 'in_3'), (4, 'in_4'),
        (5, 'in_5'), (6, 'in_6'), (7, 'in_7'),
        (16, 'out_1'), (15, 'out_2'), (14, 'out_3'), (13, 'out_4'),
        (12, 'out_5'), (11, 'out_6'), (10, 'out_7'),
    }
    assert _pin_set(chip) == expected


# --- Universal: pin numbers within a chip are unique ---

@pytest.mark.parametrize("chip_cls", [SN74HC04, CD4069, LM393, CD4043, ULN2003A])
def test_pin_numbers_are_unique_within_a_chip(chip_cls):
    chip = chip_cls(refdes_number=1)
    numbers = [fn.id.number for fn in chip._factor_nodes if isinstance(fn, Pin)]
    assert len(numbers) == len(set(numbers)), \
        f"{chip_cls.__name__} has duplicate pin numbers: {numbers}"
