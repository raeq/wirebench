"""Tiny recursive-descent parser for KiCad's `.net` S-expression format.

The parser is deliberately narrow — it doesn't understand every KiCad
construct, just enough of the netlist export shape (`(components ...)`
and `(nets ...)`) to feed the resolver and net reconstructor.  Other
sections (`design`, `sheetpath`, `tstamps`, `libparts`) are tokenised
but left as raw structure.

Input is a single text string; output is a nested Python structure:

    Atom = str
    SExpr = list[Atom | SExpr]
"""
from __future__ import annotations

from typing import Union

from framework.errors import LoadError


Atom = str
SExpr = list[Union[Atom, "SExpr"]]


def parse(text: str) -> SExpr:
    """Parse a full netlist text into one nested list.  Raises
    `LoadError` on malformed input (unbalanced parens, unterminated
    string, etc.)."""
    tokens = _tokenise(text)
    pos = 0

    def read_expr() -> SExpr:
        nonlocal pos
        if pos >= len(tokens):
            raise LoadError("unexpected end of input while reading S-expression")
        tok = tokens[pos]
        if tok != '(':
            raise LoadError(f"expected '(' at token {pos}, got {tok!r}")
        pos += 1
        node: SExpr = []
        while pos < len(tokens):
            tok = tokens[pos]
            if tok == ')':
                pos += 1
                return node
            if tok == '(':
                node.append(read_expr())
            else:
                node.append(tok)
                pos += 1
        raise LoadError("unbalanced parens — '(' without matching ')'")

    result = read_expr()
    if pos != len(tokens):
        raise LoadError(
            f"trailing tokens after top-level S-expression "
            f"({len(tokens) - pos} tokens remain)"
        )
    return result


def _tokenise(text: str) -> list[str]:
    """Lex into a flat token stream of `(`, `)`, and atoms.

    Atoms are either bare-word identifiers (`comp`, `ref`, `U1`) or
    quoted strings (`"LM7805"`).  Quoted strings are unwrapped — the
    `"` characters are stripped so the parser sees the contents.
    Newlines and inter-token whitespace are skipped."""
    tokens: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
            continue
        if c == '(' or c == ')':
            tokens.append(c)
            i += 1
            continue
        if c == '"':
            end = i + 1
            while end < n and text[end] != '"':
                # Backslash escapes — pass through the next char.
                if text[end] == '\\' and end + 1 < n:
                    end += 2
                    continue
                end += 1
            if end >= n:
                raise LoadError(
                    f"unterminated quoted string starting at byte {i}"
                )
            raw = text[i + 1:end]
            tokens.append(_unescape(raw))
            i = end + 1
            continue
        # Bare-word: read until whitespace or paren.
        end = i
        while end < n and not text[end].isspace() and text[end] not in '()':
            end += 1
        tokens.append(text[i:end])
        i = end
    return tokens


def _unescape(raw: str) -> str:
    """Resolve the small subset of backslash escapes KiCad emits."""
    out: list[str] = []
    i = 0
    while i < len(raw):
        if raw[i] == '\\' and i + 1 < len(raw):
            nxt = raw[i + 1]
            if nxt in ('"', '\\'):
                out.append(nxt)
            elif nxt == 'n':
                out.append('\n')
            elif nxt == 't':
                out.append('\t')
            else:
                out.append(nxt)
            i += 2
        else:
            out.append(raw[i])
            i += 1
    return ''.join(out)


# --------------------------------------------------------------- accessors


def head(expr: SExpr) -> str:
    """Return the first atom (tag) of an S-expression."""
    if not expr:
        raise LoadError("empty S-expression has no head")
    first = expr[0]
    if not isinstance(first, str):
        raise LoadError(f"S-expression head must be an atom, got {type(first)}")
    return first


def field(expr: SExpr, tag: str) -> SExpr | None:
    """Find the first child S-expression whose head equals `tag`,
    or None.  Used to pluck named fields out of a node."""
    for child in expr[1:]:
        if isinstance(child, list) and child and child[0] == tag:
            return child
    return None


def field_value(expr: SExpr, tag: str, default: str | None = None) -> str | None:
    """Read `(tag value)` and return the atom-typed value.  None if
    the field is absent or has no atom payload."""
    found = field(expr, tag)
    if found is None or len(found) < 2:
        return default
    value = found[1]
    if isinstance(value, str):
        return value
    return default


def children(expr: SExpr, tag: str) -> list[SExpr]:
    """All child S-expressions whose head equals `tag`."""
    out: list[SExpr] = []
    for child in expr[1:]:
        if isinstance(child, list) and child and child[0] == tag:
            out.append(child)
    return out
