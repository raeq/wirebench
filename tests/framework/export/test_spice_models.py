"""Tests for the SPICE inline-model helper.

`format_models_section` is the public surface; the private helpers
`_read_library` and `_extract_block` are exercised through it but
also directly to verify edge cases (unknown model, single-line
`.MODEL`, multi-line `.SUBCKT`).
"""
from __future__ import annotations

from framework.export.spice.models import (
    _extract_block,
    _read_library,
    format_models_section,
)


def test_read_library_returns_non_empty_text():
    text = _read_library()
    assert isinstance(text, str)
    assert '.MODEL D_LED' in text
    assert '.SUBCKT SN74HC04' in text


def test_extract_block_finds_single_line_model():
    text = _read_library()
    block = _extract_block(text, 'D_LED')
    assert block is not None
    assert block.strip().upper().startswith('.MODEL D_LED')


def test_extract_block_finds_multi_line_subckt():
    text = _read_library()
    block = _extract_block(text, 'SN74HC04')
    assert block is not None
    assert '.SUBCKT SN74HC04' in block
    assert block.strip().endswith('.ENDS SN74HC04')


def test_extract_block_returns_none_for_unknown_model():
    text = _read_library()
    block = _extract_block(text, 'NOT_A_REAL_MODEL_NAME')
    assert block is None


def test_format_models_section_emits_present_models_verbatim():
    out = format_models_section(frozenset({'D_LED', 'SN74HC04'}))
    # Both blocks present; alphabetically sorted by model name.
    assert '.MODEL D_LED' in out
    assert '.SUBCKT SN74HC04' in out
    # D_LED comes before SN74HC04 in alphabetical order.
    assert out.index('D_LED') < out.index('SN74HC04')


def test_format_models_section_emits_placeholder_for_missing():
    out = format_models_section(frozenset({'NOT_A_MODEL'}))
    assert 'TODO' in out
    assert 'NOT_A_MODEL' in out
