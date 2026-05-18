"""Integration tests for the kicad_sch renderer.

Uses the same S-expression micro-parser as the kicad netlist tests.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / 'src'))
for _d in sorted((_REPO / 'demos').iterdir()):
    if _d.is_dir():
        sys.path.insert(0, str(_d))

import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import components.diodes    # noqa: F401
import framework.export.kicad_sch  # noqa: F401

from framework.export import export_to_string


# ---------------------------------------------------------------------------
# Minimal S-expression parser (from kicad test suite)
# ---------------------------------------------------------------------------

def _tokenise(text: str):
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in ' \t\n\r':
            i += 1; continue
        if c in '()':
            yield c; i += 1; continue
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == '\\' else 1
            yield text[i:j + 1]
            i = j + 1; continue
        j = i
        while j < n and text[j] not in ' \t\n\r()':
            j += 1
        yield text[i:j]; i = j


def _parse(text: str):
    tokens = list(_tokenise(text))
    pos = [0]

    def parse_one():
        if pos[0] >= len(tokens):
            raise ValueError("unexpected EOF")
        tok = tokens[pos[0]]
        pos[0] += 1
        if tok == '(':
            out = []
            while pos[0] < len(tokens) and tokens[pos[0]] != ')':
                out.append(parse_one())
            if pos[0] >= len(tokens):
                raise ValueError("missing closing paren")
            pos[0] += 1
            return out
        if tok == ')':
            raise ValueError("unexpected ')'")
        return tok

    result = parse_one()
    if pos[0] != len(tokens):
        raise ValueError(f"trailing tokens: {tokens[pos[0]:]}")
    return result


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _blocks(tree, name: str) -> list:
    return [b for b in tree if isinstance(b, list) and b and b[0] == name]


def _all_atoms(tree) -> list[str]:
    """Flatten all atoms from a nested list structure."""
    out = []
    if isinstance(tree, str):
        out.append(tree)
    elif isinstance(tree, list):
        for item in tree:
            out.extend(_all_atoms(item))
    return out


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_hello_led_parses_as_valid_sexpr():
    from hello_led import HelloLED
    text = export_to_string(_silently(HelloLED), 'kicad_sch')
    tree = _parse(text)
    assert isinstance(tree, list)
    assert tree[0] == 'kicad_sch'


def test_hello_led_has_required_sections():
    from hello_led import HelloLED
    text = export_to_string(_silently(HelloLED), 'kicad_sch')
    tree = _parse(text)
    block_names = {b[0] for b in tree[1:] if isinstance(b, list) and b}
    assert 'lib_symbols' in block_names
    assert 'sheet_instances' in block_names


def test_hello_led_has_resistor_and_led_instances():
    from hello_led import HelloLED
    text = export_to_string(_silently(HelloLED), 'kicad_sch')
    tree = _parse(text)
    symbol_blocks = _blocks(tree, 'symbol')
    lib_ids = []
    for block in symbol_blocks:
        for item in block:
            if isinstance(item, list) and item and item[0] == 'lib_id':
                lib_ids.append(item[1].strip('"'))
    assert 'Device:R' in lib_ids
    assert 'Device:LED' in lib_ids


def test_hello_led_lib_symbols_contains_device_r():
    from hello_led import HelloLED
    text = export_to_string(_silently(HelloLED), 'kicad_sch')
    tree = _parse(text)
    lib_syms = _blocks(tree, 'lib_symbols')
    assert lib_syms, "No lib_symbols block"
    inner = lib_syms[0][1:]  # contents of (lib_symbols ...)
    sym_names = {b[1].strip('"') for b in inner if isinstance(b, list) and b and b[0] == 'symbol'}
    assert 'Device:R' in sym_names


def test_hello_led_has_power_symbols_for_gnd_and_vcc():
    from hello_led import HelloLED
    text = export_to_string(_silently(HelloLED), 'kicad_sch')
    tree = _parse(text)
    symbol_blocks = _blocks(tree, 'symbol')
    lib_ids = []
    for block in symbol_blocks:
        for item in block:
            if isinstance(item, list) and item and item[0] == 'lib_id':
                lib_ids.append(item[1].strip('"'))
    assert 'power:GND' in lib_ids
    assert 'power:VCC' in lib_ids


def test_hello_led_has_global_labels_for_inner_net():
    from hello_led import HelloLED
    text = export_to_string(_silently(HelloLED), 'kicad_sch')
    tree = _parse(text)
    labels = _blocks(tree, 'global_label')
    label_names = [b[1].strip('"') for b in labels if len(b) > 1]
    # The anode-side net should appear as a global label
    assert any('D1' in name or 'R1' in name for name in label_names), \
        f"Expected a net label referencing D1 or R1; got: {label_names}"


def test_hello_led_net_label_appears_twice():
    """The anode net must appear on both R1-pin-2 stub and D1-pin-1 stub."""
    from hello_led import HelloLED
    text = export_to_string(_silently(HelloLED), 'kicad_sch')
    tree = _parse(text)
    labels = _blocks(tree, 'global_label')
    label_names = [b[1].strip('"') for b in labels if len(b) > 1]
    from collections import Counter
    counts = Counter(label_names)
    # Exactly one net name should appear exactly twice (both sides of the connection)
    double_labels = [name for name, count in counts.items() if count == 2]
    assert double_labels, f"No net label appears twice; labels: {label_names}"


def test_hello_led_output_is_deterministic():
    """Render twice; output must be byte-identical."""
    from hello_led import HelloLED
    t1 = export_to_string(_silently(HelloLED), 'kicad_sch')
    t2 = export_to_string(_silently(HelloLED), 'kicad_sch')
    assert t1 == t2


def test_hello_led_contains_no_double_parens():
    from hello_led import HelloLED
    text = export_to_string(_silently(HelloLED), 'kicad_sch')
    assert '((effects' not in text, "Double-parenthesis around effects found"


def test_version_field_present():
    from hello_led import HelloLED
    text = export_to_string(_silently(HelloLED), 'kicad_sch')
    tree = _parse(text)
    versions = [b for b in tree if isinstance(b, list) and b and b[0] == 'version']
    assert versions, "No (version ...) field"
    assert versions[0][1] == str(20240618)
