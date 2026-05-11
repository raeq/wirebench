"""SPICE .MODEL / .SUBCKT emission helpers.

The shipped `spice-models.lib` contains the canonical text. When
`emit_models_inline=True` is configured, this module produces the
equivalent text inline at the top of the deck so the output is
self-contained.
"""
from __future__ import annotations

from pathlib import Path


_LIB_PATH = Path(__file__).parent / 'spice-models.lib'


def _read_library() -> str:
    return _LIB_PATH.read_text()


def _extract_block(library_text: str, model_name: str) -> str | None:
    """Return the .MODEL or .SUBCKT block for `model_name`, or None if
    not present. A model block is delimited by `.MODEL <name>` on one
    line, or by `.SUBCKT <name>` / `.ENDS <name>` brackets."""
    lines = library_text.splitlines()
    out: list[str] = []
    in_subckt = False
    for line in lines:
        stripped = line.strip()
        if not in_subckt:
            if stripped.upper().startswith('.MODEL'):
                # Single-line model directive.
                tokens = stripped.split()
                if len(tokens) >= 2 and tokens[1] == model_name:
                    return line
            elif stripped.upper().startswith('.SUBCKT'):
                tokens = stripped.split()
                if len(tokens) >= 2 and tokens[1] == model_name:
                    in_subckt = True
                    out.append(line)
        else:
            out.append(line)
            if stripped.upper().startswith('.ENDS'):
                return '\n'.join(out)
    return '\n'.join(out) if out else None


def format_models_section(models_used: frozenset[str]) -> str:
    """Return inline-model text for the requested models.

    Models present in the shipped library are inlined verbatim; unknown
    models become a placeholder comment so the user sees what's
    missing rather than getting a silently-broken deck.
    """
    library = _read_library()
    parts: list[str] = []
    for name in sorted(models_used):
        block = _extract_block(library, name)
        if block:
            parts.append(block)
        else:
            parts.append(f"* TODO: model {name} not found in spice-models.lib")
    return '\n'.join(parts)
