"""End-to-end tests for `wirebench parts`.

Invokes the CLI as a subprocess so the contract is exercised exactly
as a downstream consumer would see it; structural assertions verify
that filters compose and the JSON schema matches §3 of the spec.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


_EXPECTED_KEYS = {
    'class_name', 'module', 'refdes_prefix', 'kind', 'description',
    'footprint', 'pin_count', 'pin_functions', 'has_behavioural_cell',
    'datasheet',
}


def _invoke(*args: str) -> tuple[int, str]:
    cmd = [sys.executable, '-m', 'cli.main', 'parts', *args]
    result = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True,
    )
    return result.returncode, result.stdout


def _invoke_json(*args: str) -> list[dict]:
    code, out = _invoke(*args, '--json')
    assert code == 0, f"exit {code}: {out}"
    return json.loads(out)


# ---------------------------------------------------------- text listing


def test_default_list_emits_text() -> None:
    code, out = _invoke()
    assert code == 0
    assert out.strip(), "default listing should not be empty"
    # Aligned four-column rows — each line has at least three runs of
    # whitespace separating columns.
    for line in out.splitlines()[:5]:
        assert '  ' in line


def test_list_subcommand_alias() -> None:
    code1, out1 = _invoke()
    code2, out2 = _invoke('list')
    assert code1 == code2 == 0
    assert out1 == out2


# ---------------------------------------------------------- JSON


def test_json_returns_array_of_descriptors() -> None:
    parts = _invoke_json()
    assert isinstance(parts, list)
    assert len(parts) > 50, (
        f"expected > 50 registered parts; got {len(parts)}"
    )
    for entry in parts:
        assert set(entry.keys()) == _EXPECTED_KEYS, (
            f"unexpected schema for {entry.get('class_name')}: "
            f"{set(entry.keys()) ^ _EXPECTED_KEYS}"
        )


def test_known_chips_present_in_json() -> None:
    """A handful of representative parts should always be in the catalogue."""
    parts = _invoke_json()
    names = {p['class_name'] for p in parts}
    for expected in ('LM7805', 'ATmega328P', 'SN74HC04', 'Resistor', 'LED'):
        assert expected in names


# ---------------------------------------------------------- filters


def test_filter_by_prefix() -> None:
    parts = _invoke_json('--prefix', 'R')
    assert parts
    assert all(p['refdes_prefix'] == 'R' for p in parts)


def test_filter_by_kind_chip() -> None:
    parts = _invoke_json('--kind', 'chip')
    assert parts
    assert all(p['kind'] == 'chip' for p in parts)


def test_filter_by_kind_connector() -> None:
    parts = _invoke_json('--kind', 'connector')
    assert parts
    assert all(p['kind'] == 'connector' for p in parts)


def test_filter_has_cell_returns_subset_of_chips() -> None:
    all_chips = _invoke_json('--kind', 'chip')
    behavioural = _invoke_json('--kind', 'chip', '--has-cell')
    assert len(behavioural) > 0
    assert len(behavioural) <= len(all_chips)
    assert all(p['has_behavioural_cell'] for p in behavioural)


def test_filter_has_footprint() -> None:
    parts = _invoke_json('--has-footprint')
    assert parts
    assert all(p['footprint'] for p in parts)


def test_filter_pin_function_power() -> None:
    parts = _invoke_json('--pin-function', 'POWER')
    assert parts
    for p in parts:
        functions = p['pin_functions'] or {}
        assert any(
            (f or '').lower() == 'power' for f in functions.values()
        ), f"{p['class_name']} has no POWER pin but matched filter"


def test_filters_compose_with_and() -> None:
    parts = _invoke_json('--kind', 'passive', '--prefix', 'R')
    assert parts
    assert all(p['kind'] == 'passive' and p['refdes_prefix'] == 'R'
               for p in parts)


# ---------------------------------------------------------- error paths


def test_unknown_kind_returns_usage_error() -> None:
    code, _ = _invoke('--kind', 'banana')
    assert code == 2


def test_unknown_pin_function_returns_usage_error() -> None:
    """A typo like `--pin-function PWOER` should fail loudly, not
    silently return an empty catalogue."""
    code, _ = _invoke('--pin-function', 'PWOER')
    assert code == 2


def test_pin_function_filter_is_case_insensitive() -> None:
    upper = _invoke_json('--pin-function', 'POWER')
    lower = _invoke_json('--pin-function', 'power')
    assert upper == lower


def test_unknown_subcommand_returns_usage_error() -> None:
    code, _ = _invoke('garbage')
    assert code == 2


# ---------------------------------------------------------- specific cases


def test_relay_kind_returns_relay_spdt() -> None:
    parts = _invoke_json('--kind', 'relay')
    assert parts
    assert any(p['class_name'] == 'Relay_SPDT' for p in parts)
    assert all(p['kind'] == 'relay' for p in parts)


def test_wrapped_docstring_joins_into_single_line_description() -> None:
    """BQ27546G1's first paragraph wraps across two source lines; the
    description should not be truncated at the first newline."""
    parts = _invoke_json()
    bq = next(p for p in parts if p['class_name'] == 'BQ27546G1')
    # The full first paragraph mentions 'pack-side integration', which
    # lives on the second physical line of the docstring.
    assert 'pack-side integration' in bq['description']


def test_black_box_sensor_is_not_behavioural() -> None:
    """BMP280 uses `cells=[]` explicitly — should NOT match --has-cell."""
    behavioural = _invoke_json('--has-cell')
    names = {p['class_name'] for p in behavioural}
    assert 'BMP280' not in names
    assert 'ATmega328P' not in names  # BARE_FIRMWARE_DRIVEN
    assert 'LM7805' in names           # real internal cell
