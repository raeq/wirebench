"""Extract and transform symbol definitions from vendored KiCad symbol files.

Provides two public interfaces:
- `get_pin_defs(lib, name)` — pin geometry needed for stub-wire placement.
- `collect_lib_symbols(used)` — fully-qualified symbol text blocks for
  embedding in the schematic's `(lib_symbols ...)` section.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_VENDORED = Path(__file__).parent / 'vendored_symbols'
_KNOWN_LIBS = frozenset({
    'Device', 'Diode', 'Regulator_Linear', '74xx', '4xxx',
    'Connector_Generic', 'power',
})


@dataclass(frozen=True, slots=True)
class PinDef:
    """One pin's connection geometry in symbol-local coordinates (mm)."""
    number: str
    x: float
    y: float
    angle: float


@lru_cache(maxsize=len(_KNOWN_LIBS))
def _lib_text(lib: str) -> str:
    path = _VENDORED / f'{lib}.kicad_sym'
    if not path.exists():
        return ''
    return path.read_text(encoding='utf-8')


def _extract_block(lib_text: str, sym_name: str) -> str | None:
    """Return the raw `(symbol "sym_name" ...)` block, or None."""
    marker = f'\t(symbol "{sym_name}"'
    start = lib_text.find(marker)
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(lib_text[start:]):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                return lib_text[start: start + i + 1]
    return None


def _extends_parent(sym_text: str) -> str | None:
    """Return the name of the parent symbol if `sym_text` uses (extends ...)."""
    m = re.search(r'\(extends\s+"([^"]+)"', sym_text)
    return m.group(1) if m else None


def _parse_pins(sym_text: str) -> list[PinDef]:
    pins: list[PinDef] = []
    for m in re.finditer(
        r'\(pin\s+\w+\s+\w+\s*\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)',
        sym_text,
    ):
        x, y, angle = float(m.group(1)), float(m.group(2)), float(m.group(3))
        tail = sym_text[m.start(): m.start() + 400]
        nm = re.search(r'\(number\s+"([^"]+)"', tail)
        number = nm.group(1) if nm else '?'
        pins.append(PinDef(number=number, x=x, y=y, angle=angle))
    return pins


def get_pin_defs(lib: str, name: str) -> list[PinDef]:
    """Pin geometry for `lib:name`, resolving (extends ...) if needed."""
    text = _lib_text(lib)
    block = _extract_block(text, name)
    if block is None:
        return []
    pins = _parse_pins(block)
    if not pins:
        parent = _extends_parent(block)
        if parent:
            return get_pin_defs(lib, parent)
    return pins


def _qualify_names(sym_text: str, lib: str, sym_name: str) -> str:
    """Add the `lib:` prefix to every internal name reference.

    Uses callable replacements to avoid treating the lib name as a
    backreference string (e.g. '74xx' would otherwise confuse re.sub).
    """
    esc = re.escape(sym_name)
    prefix = f'{lib}:'

    def _qualify_symbol(m: re.Match[str]) -> str:
        return m.group(1) + prefix + m.group(2)

    result = re.sub(
        r'(\(symbol\s+")(' + esc + r')',
        _qualify_symbol,
        sym_text,
    )

    def _qualify_extends(m: re.Match[str]) -> str:
        return m.group(1) + prefix

    result = re.sub(
        r'(\(extends\s+")',
        _qualify_extends,
        result,
    )
    return result


def collect_lib_symbols(
    used: list[tuple[str, str]],
) -> dict[str, str]:
    """Return {qualified_name: qualified_text} for embedding in lib_symbols.

    Resolves `(extends ...)` chains automatically — the parent is added
    to the result if it isn't already present.
    """
    result: dict[str, str] = {}
    pending = list(used)
    while pending:
        lib, name = pending.pop()
        qname = f'{lib}:{name}'
        if qname in result:
            continue
        text = _lib_text(lib)
        block = _extract_block(text, name)
        if block is None:
            continue
        parent = _extends_parent(block)
        if parent:
            pending.append((lib, parent))
        result[qname] = _qualify_names(block, lib, name)
    return result
