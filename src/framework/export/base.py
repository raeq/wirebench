"""Renderer registry + ExporterContext + ExportConfig.

A renderer is a function `(component, ctx) -> str` that takes one
FactorNode and returns the format-specific text fragment for that
instance.  Renderers are registered against (class, format) keys.

Lookup walks the class MRO so a renderer registered against a base
class (e.g. Connector) handles every subclass automatically — and a
more-specific subclass registration still wins.
"""
from __future__ import annotations

from typing import Any, Callable, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, PositiveFloat

from framework.factor import FactorNode
from framework.port import Port

from framework.export.nets import LogicalNet, compute_logical_nets


T = TypeVar('T', bound=FactorNode)
Renderer = Callable[[Any, 'ExporterContext'], str]


_RENDERERS: dict[tuple[type[FactorNode], str], Renderer] = {}


def register_renderer(
    component_class: type[T],
    *,
    format: str,
) -> Callable[[Renderer], Renderer]:
    """Decorator: register `fn` as the renderer for instances of
    `component_class` in the given `format`.

    Lookup is MRO-aware: a renderer registered against a base class
    handles every subclass that doesn't have its own renderer.
    """
    def decorator(fn: Renderer) -> Renderer:
        key = (component_class, format)
        if key in _RENDERERS:
            raise ValueError(
                f"Renderer for {component_class.__name__} in format "
                f"{format!r} already registered."
            )
        _RENDERERS[key] = fn
        return fn
    return decorator


def lookup_renderer(
    component_class: type[FactorNode],
    format: str,
) -> Renderer:
    """Return the renderer for `component_class` in `format`.

    Walks `component_class.__mro__` so a renderer registered on a base
    class (e.g. Connector) is found for every subclass that doesn't
    have its own.
    """
    for cls in component_class.__mro__:
        key = (cls, format)
        if key in _RENDERERS:
            return _RENDERERS[key]
    available = sorted({
        f for (c, f) in _RENDERERS
        if c in component_class.__mro__
    })
    raise KeyError(
        f"No {format!r} renderer for {component_class.__name__}. "
        f"Available formats for this class: {available or '(none)'}."
    )


def _registered_keys() -> list[tuple[type[FactorNode], str]]:
    """Internal: snapshot of registered keys, for test inspection."""
    return list(_RENDERERS.keys())


class ExportConfig(BaseModel):
    """Common export configuration.  Adapters subclass this to add
    format-specific fields (see `SpiceExportConfig`)."""
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)

    include_header_comment: bool = True
    net_name_style: Literal['numeric', 'qualified', 'short_hash'] = 'numeric'
    include_unused_pins: bool = False


class SpiceExportConfig(ExportConfig):
    """SPICE-specific tuning."""
    default_supply_voltage: PositiveFloat = 5.0
    model_library_path: str = 'spice-models.lib'
    emit_models_inline: bool = False


class ExporterContext:
    """Per-export shared state: logical nets, net naming, output
    accumulation, and adapter-specific configuration."""

    __slots__ = (
        '_design', '_format', '_logical_nets', '_net_name_by_node',
        '_lines', '_config', '_models_used', '_synth_counter',
        '_synth_names',
    )

    def __init__(
        self,
        design: FactorNode,
        format: str,
        config: ExportConfig | None = None,
    ) -> None:
        self._design = design
        self._format = format
        self._logical_nets = compute_logical_nets(design)
        self._config = config or ExportConfig()
        self._lines: list[str] = []
        self._models_used: set[str] = set()
        self._synth_counter: dict[str, int] = {}
        self._synth_names: dict[int, str] = {}
        self._net_name_by_node = self._assign_net_names()

    @property
    def design(self) -> FactorNode:
        return self._design

    @property
    def format(self) -> str:
        return self._format

    @property
    def config(self) -> ExportConfig:
        return self._config

    @property
    def logical_nets(self) -> list[LogicalNet]:
        return self._logical_nets

    @property
    def models_used(self) -> frozenset[str]:
        return frozenset(self._models_used)

    def _assign_net_names(self) -> dict[int, str]:
        """Compute per-Node net names. Resolved here rather than in
        adapters so that two ports on the same net always render to the
        same name regardless of which adapter looks first."""
        from components.passives.rail import Rail

        names: dict[int, str] = {}
        for net in self._logical_nets:
            has_gnd = any(
                isinstance(o, Rail) and o.level is False
                for o, _ in net.ports
            )
            has_vcc = any(
                isinstance(o, Rail) and o.level is True
                for o, _ in net.ports
            )
            if has_gnd:
                name = '0'
            elif has_vcc:
                name = 'vcc'
            else:
                name = self._stylise_net_name(net)
            for nid in net.nodes:
                names[nid] = name
        return names

    def _stylise_net_name(self, net: LogicalNet) -> str:
        style = self._config.net_name_style
        if style == 'numeric':
            return f"net_{net.id}"
        if style == 'qualified':
            if net.ports:
                owner, port = net.ports[0]
                refdes = getattr(owner, 'refdes', type(owner).__name__)
                return f"{refdes}_{port.name}"
            return f"net_{net.id}"
        # short_hash
        return f"n{net.id:04x}"

    def net_name(self, port: Port) -> str:
        """Return the format-specific name for the net containing this
        port. Unconnected ports get a unique synthetic name."""
        if port.node is None:
            key = id(port)
            if key not in self._synth_names:
                self._synth_names[key] = self._next_synth('nc')
            return self._synth_names[key]
        return self._net_name_by_node.get(id(port.node), f"net_?_{id(port.node)}")

    def _next_synth(self, prefix: str) -> str:
        n = self._synth_counter.get(prefix, 0)
        self._synth_counter[prefix] = n + 1
        return f"{prefix}_{n}"

    def refdes_of(self, component: FactorNode) -> str:
        """Return the refdes for refdes-bearing components, or a
        synthesised id for those that don't carry one."""
        rd = getattr(component, 'refdes', None)
        if rd:
            return rd
        key = id(component)
        if key in self._synth_names:
            return self._synth_names[key]
        synth = self._next_synth(type(component).__name__)
        self._synth_names[key] = synth
        return synth

    def emit(self, text: str) -> None:
        """Append a line or multi-line block to the output."""
        if text:
            self._lines.append(text)

    def register_model(self, model_name: str) -> None:
        """Note that this run uses the named model. Used by SPICE to
        emit only the needed `.MODEL` / `.LIB` directives."""
        self._models_used.add(model_name)

    def output(self) -> str:
        return '\n'.join(self._lines) + '\n'
