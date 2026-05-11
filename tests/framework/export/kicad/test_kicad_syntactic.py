"""S-expression syntactic validation for KiCad output.

Uses a small recursive-descent parser (~40 lines) — no external
dependency. Verifies parenthesis balance and basic structure.

If a test fails because a renderer is missing or incorrect, the fix
is to add or correct the renderer — not to lower the assertion bar.
"""
from __future__ import annotations

import warnings

import pytest

import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.export.kicad  # noqa: F401

from framework.export import export_to_string

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


# ---- Minimal S-expression parser -------------------------------------

def _tokenise(text: str):
    """Yield tokens: '(', ')', or strings/atoms. Quoted strings are
    returned with surrounding quotes preserved."""
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in ' \t\n\r':
            i += 1
            continue
        if c in '()':
            yield c
            i += 1
            continue
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                if text[j] == '\\':
                    j += 2
                else:
                    j += 1
            yield text[i:j + 1]
            i = j + 1
            continue
        # atom
        j = i
        while j < n and text[j] not in ' \t\n\r()':
            j += 1
        yield text[i:j]
        i = j


def _parse(text: str):
    """Return a nested list reflecting the S-expression. Raises on
    mismatched parens or trailing garbage."""
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
            pos[0] += 1  # consume ')'
            return out
        if tok == ')':
            raise ValueError("unexpected ')'")
        return tok

    result = parse_one()
    if pos[0] != len(tokens):
        raise ValueError(f"trailing tokens: {tokens[pos[0]:]}")
    return result


# ---- The tests -------------------------------------------------------

@pytest.mark.parametrize("factory", [
    WaterAlarm, WaterAlarmAssembly,
], ids=['WaterAlarm', 'WaterAlarmAssembly'])
def test_kicad_output_parses_as_sexpr(factory):
    text = export_to_string(_silently(factory), 'kicad')
    tree = _parse(text)
    # Top-level must be (export ...).
    assert tree[0] == 'export'
    # Must contain (design ...) (components ...) (nets ...) blocks.
    block_names = [b[0] for b in tree[1:] if isinstance(b, list)]
    for required in ('design', 'components', 'nets'):
        assert required in block_names, \
            f"Missing required block '{required}' in {factory.__name__}"
