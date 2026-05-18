"""Unit tests for the S-expression parser."""
from __future__ import annotations

import pytest

from framework.errors import LoadError
from framework.import_kicad.parser import (
    children, field, field_value, head, parse,
)


def test_parse_minimal_expression():
    ast = parse('(export (version "E"))')
    assert head(ast) == 'export'
    version = field(ast, 'version')
    assert version is not None
    assert version[1] == 'E'


def test_parse_handles_nested_blocks():
    ast = parse('''
        (export
          (components
            (comp (ref "U1") (value "LM7805"))
            (comp (ref "R1") (value "330"))))
    ''')
    comps = field(ast, 'components')
    assert comps is not None
    rows = children(comps, 'comp')
    assert len(rows) == 2
    assert [field_value(r, 'ref') for r in rows] == ['U1', 'R1']


def test_parse_handles_escaped_quotes():
    ast = parse(r'(comp (description "a \"name\" with quotes"))')
    assert field_value(ast, 'description') == 'a "name" with quotes'


def test_parse_unbalanced_parens_raises_load_error():
    with pytest.raises(LoadError):
        parse('(export (version "E")')


def test_parse_trailing_tokens_raises_load_error():
    with pytest.raises(LoadError):
        parse('(export) extra-token')


def test_parse_unterminated_string_raises_load_error():
    with pytest.raises(LoadError):
        parse('(comp (value "lm7805')


def test_field_value_falls_back_to_default():
    ast = parse('(comp (ref "U1"))')
    assert field_value(ast, 'value', default='?') == '?'


def test_children_returns_only_named_blocks():
    ast = parse('(nets (net (code "1")) (net (code "2")) (other (code "3")))')
    nets = children(ast, 'net')
    assert len(nets) == 2
    assert [field_value(n, 'code') for n in nets] == ['1', '2']
