"""Renderer registry tests."""
import pytest

# Trigger SPICE renderer registration.
import framework.export.spice  # noqa: F401

from framework.connector import Connector
from framework.errors import DuplicateRendererError, RendererNotFoundError
from framework.factor import FactorNode
from framework.export.base import (
    lookup_renderer, register_renderer,
)
from framework.registry import registered_names, lookup as lookup_component

from components.passives.resistor import Resistor
from components.connectors.headers import Header2xNFemale


def test_lookup_renderer_returns_registered_function():
    fn = lookup_renderer(Resistor, 'spice')
    assert callable(fn)


def test_unknown_format_raises_with_hint():
    with pytest.raises(RendererNotFoundError, match='spice'):
        lookup_renderer(Resistor, 'nonexistent-format')


def test_duplicate_registration_raises():
    class _Dummy(FactorNode):
        __slots__ = ()
        def __init__(self): pass
        @property
        def ports(self): return {}
        def evaluate(self): pass

    @register_renderer(_Dummy, format='spice')
    def first(c, ctx): return ""

    with pytest.raises(DuplicateRendererError, match='already registered'):
        @register_renderer(_Dummy, format='spice')
        def second(c, ctx): return ""


def test_connector_lookup_uses_mro():
    """A renderer registered against the Connector base class is found
    for every concrete subclass via MRO walk."""
    # Resolves through Header2xNFemale.__mro__ to Connector.
    fn = lookup_renderer(Header2xNFemale, 'spice')
    assert callable(fn)


def test_every_registered_component_has_spice_renderer():
    """Walk the component registry and assert every class has a SPICE
    renderer (or inherits one via MRO)."""
    missing: list[str] = []
    for name in registered_names():
        cls = lookup_component(name)
        try:
            lookup_renderer(cls, 'spice')
        except KeyError:
            missing.append(name)
    assert not missing, f"Missing SPICE renderers: {missing}"
