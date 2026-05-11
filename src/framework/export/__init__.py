"""Generic export framework.

Format-agnostic machinery for walking a `.circuitry` design and emitting
it to industry-standard netlist or schematic formats. The framework
provides the shared mechanics — logical-net computation, hierarchical
walking, renderer registration; each format adapter (SPICE, KiCad, …)
plugs in per-component renderers and a deck-assembly function.

Top-level API:

    export(design, format, path)        - write to a file
    export_to_string(design, format)    - return the rendered text
    list_formats()                      - names of available adapters

Adapters live under `framework.export.<format>/` and self-register
their renderers when imported.
"""
from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

from pydantic import validate_call

from framework.factor import FactorNode

from framework.export.base import ExportConfig, ExporterContext
from framework.export.nets import LogicalNet, compute_logical_nets
from framework.export.walk import Path as HierPath, walk_hierarchy


__all__ = [
    'ExportConfig', 'ExporterContext',
    'LogicalNet', 'compute_logical_nets',
    'HierPath', 'walk_hierarchy',
    'export', 'export_to_string', 'list_formats',
]


def _load_adapter(format: str):
    """Import the adapter sub-package, raising on unknown name. The
    import triggers @register_renderer side effects."""
    try:
        return importlib.import_module(f'framework.export.{format}')
    except ImportError as e:
        raise ValueError(
            f"Unknown export format {format!r}. "
            f"Available: {list_formats()}"
        ) from e


@validate_call(config={'arbitrary_types_allowed': True})
def export(
    design: FactorNode,
    format: str,
    path: Path | str,
    config: ExportConfig | None = None,
) -> None:
    """Export `design` to `path` in the named `format`."""
    text = export_to_string(design, format, config)
    Path(path).write_text(text)


@validate_call(config={'arbitrary_types_allowed': True})
def export_to_string(
    design: FactorNode,
    format: str,
    config: ExportConfig | None = None,
) -> str:
    """Render `design` to a text string in the named `format`."""
    adapter = _load_adapter(format)
    ctx = ExporterContext(design, format, config=config)
    return adapter.render(design, ctx)


def list_formats() -> list[str]:
    """Names of every adapter sub-package found under framework.export/."""
    import framework.export as pkg
    return sorted(
        m.name for m in pkgutil.iter_modules(pkg.__path__)
        if m.ispkg
    )
