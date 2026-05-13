"""Renderer registry + ExporterContext + ExportConfig.

A renderer is a function `(component, ctx) -> str` that takes one
Part and returns the format-specific text fragment for that
instance.  Renderers are registered against (class, format) keys.

Lookup walks the class MRO so a renderer registered against a base
class (e.g. Connector) handles every subclass automatically — and a
more-specific subclass registration still wins.
"""
from __future__ import annotations

from typing import Any, Callable, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, PositiveFloat

from framework.errors import DuplicateRendererError, RendererNotFoundError
from framework.part import Part
from framework.port import Port

from framework.export.nets import LogicalNet, compute_logical_nets


T = TypeVar('T', bound=Part)
# Renderers are typed as the most permissive Callable shape — different
# format adapters take different extra positional arguments (`bom` adds
# `parent_refdes`, `kicad` adds `qrd / names / tstamps`).  Using
# `Callable[..., str]` lets the registry accept any of them without
# fighting per-format signature variance.
Renderer = Callable[..., str]


# The registry's keys hold `type[Part]` so callers can register
# abstract bases (`Chip`, `Diode`, `Transistor`) whose subclasses inherit
# the renderer via MRO.  `mypy --strict` would flag `type[Diode]` as
# abstract; that's precisely the use-case we want, so the registry
# function uses `type[Part]` rather than a TypeVar bound to a
# concrete subclass.
_RENDERERS: dict[tuple[type[Part], str], Renderer] = {}


def register_renderer(
    component_class: type[Any],
    *,
    format: str,
) -> Callable[[Renderer], Renderer]:
    """Decorator: register `fn` as the renderer for instances of
    `component_class` in the given `format`.

    Lookup is MRO-aware: a renderer registered against a base class
    handles every subclass that doesn't have its own renderer.  Abstract
    bases like `Chip`, `Diode`, and `Transistor` are intentionally
    allowed here so a single renderer can cover every subclass — the
    parameter is annotated as `type[Any]` rather than `type[Part]`
    because mypy's `[type-abstract]` check would otherwise reject an
    abstract subclass even though that's exactly the use case.
    """
    def decorator(fn: Renderer) -> Renderer:
        key = (component_class, format)
        if key in _RENDERERS:
            raise DuplicateRendererError(
                f"Renderer for {component_class.__name__} in format "
                f"{format!r} already registered."
            )
        _RENDERERS[key] = fn
        return fn
    return decorator


def lookup_renderer(
    component_class: type[Part],
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
    raise RendererNotFoundError(
        f"No {format!r} renderer for {component_class.__name__}. "
        f"Available formats for this class: {available or '(none)'}."
    )


def _registered_keys() -> list[tuple[type[Part], str]]:
    """Internal: snapshot of registered keys, for test inspection."""
    return list(_RENDERERS.keys())


# ---------------------------------------------------------------------------
# Net-namer registry (per spec §6.6).  Each format adapter registers a
# function that maps a LogicalNet to a format-specific net name.  The
# framework's previous SPICE-hardcoded conventions live in the SPICE
# adapter; the framework itself stays format-agnostic.
# ---------------------------------------------------------------------------

NetNamer = Callable[['LogicalNet', 'ExporterContext'], str]
_NET_NAMERS: dict[str, NetNamer] = {}


def register_net_namer(format: str, namer: NetNamer) -> None:
    """Register a net-naming function for `format`. Called by each
    adapter's package `__init__.py`. Re-registering raises."""
    if format in _NET_NAMERS:
        raise DuplicateRendererError(
            f"Net namer for format {format!r} already registered."
        )
    _NET_NAMERS[format] = namer


def lookup_net_namer(format: str) -> NetNamer:
    """Return the namer registered for `format`. Raises KeyError if
    the adapter hasn't registered one."""
    try:
        return _NET_NAMERS[format]
    except KeyError:
        raise RendererNotFoundError(
            f"No net namer registered for format {format!r}. "
            f"Available: {sorted(_NET_NAMERS)}"
        )


def pin_number_of(component: Part, port_name: str) -> int | None:
    """The datasheet pin number for `port_name` on `component`,
    regardless of whether the component models its terminals as Pin
    instances (chips, connectors) or as raw Ports with PIN_NUMBERS
    metadata (passives). Returns None if the component declares no
    number for the requested port — adapters decide whether that's an
    error or a silently-omitted field."""
    for pin in getattr(component, 'pins', ()):
        if pin.id.name == port_name:
            return int(pin.id.number)
    n = getattr(type(component), 'PIN_NUMBERS', {}).get(port_name)
    return None if n is None else int(n)


class ExportConfig(BaseModel):
    """Common export configuration.  Adapters subclass this to add
    format-specific fields (see `SpiceExportConfig`, `KiCadExportConfig`, …)."""
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)

    # Per §6.7: default to False so golden-file tests run byte-stable
    # on the unconfigured `export()` call. When True, the header
    # carries deterministic content only (no wall-clock timestamps).
    include_header_comment: bool = False
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
        '_synth_names', '_namer',
    )

    def __init__(
        self,
        design: Part,
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
        # Look up the per-format namer. Adapters register one in
        # their package __init__; this is the framework's only
        # remaining net-naming hook.
        self._namer = lookup_net_namer(format)
        self._net_name_by_node = self._assign_net_names()

    @property
    def design(self) -> Part:
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
        """Compute per-Node net names by delegating to the
        format-specific namer (per §6.6). Two ports on the same net
        always resolve to the same name."""
        names: dict[int, str] = {}
        for net in self._logical_nets:
            name = self._namer(net, self)
            for nid in net.nodes:
                names[nid] = name
        return names

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

    def refdes_of(self, component: Part) -> str:
        """Return the refdes for refdes-bearing components, or a
        synthesised id for those that don't carry one."""
        rd = getattr(component, 'refdes', None)
        if rd:
            return str(rd)
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
