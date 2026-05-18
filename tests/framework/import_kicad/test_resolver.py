"""Unit tests for the KiCad → wirebench part resolver."""
from __future__ import annotations

import pytest

from framework.chip import Chip
from framework.errors import UnknownPartError
from framework.import_kicad.resolver import (
    KiCadComponent, resolve_part_class,
)


def _kc(value='', lib=None, part=None, ref='U1', footprint=None, pins=()):
    return KiCadComponent(
        ref=ref, value=value, footprint=footprint,
        libsource_lib=lib, libsource_part=part,
        pin_specs=tuple(pins),
    )


def test_exact_value_match_against_registry():
    cls = resolve_part_class(_kc(value='LM7805'))
    assert cls.__name__ == 'LM7805'


def test_case_insensitive_value_match():
    cls = resolve_part_class(_kc(value='lm7805'))
    assert cls.__name__ == 'LM7805'


def test_suffix_stripping_match():
    cls = resolve_part_class(_kc(value='LM7805_TO220'))
    assert cls.__name__ == 'LM7805'


def test_libsource_map_resistor():
    cls = resolve_part_class(_kc(value='330', lib='Device', part='R'))
    assert cls.__name__ == 'Resistor'


def test_libsource_map_diode_default():
    cls = resolve_part_class(_kc(value='', lib='Device', part='D'))
    assert cls.__name__ == 'D1N4148'


def test_value_map_fallback_resistor():
    cls = resolve_part_class(_kc(value='R'))
    assert cls.__name__ == 'Resistor'


def test_unknown_part_strict_raises():
    with pytest.raises(UnknownPartError, match=r"Could not resolve"):
        resolve_part_class(
            _kc(value='SomeMysteriousChip_X9000', lib='X', part='X'),
            strict=True,
        )


def test_unknown_part_non_strict_returns_placeholder():
    cls = resolve_part_class(
        _kc(
            value='SomeMysteriousChip_X9000',
            ref='U99',
            pins=((1, 'A'), (2, 'B'), (3, 'C')),
        ),
        strict=False,
    )
    assert issubclass(cls, Chip)
    assert getattr(cls, 'IMPORTED_FROM_KICAD', False)
    assert getattr(cls, 'BARE_FIRMWARE_DRIVEN', False)
    assert cls.__name__.startswith('UnknownPart_')


def test_unknown_part_cache_reuses_class():
    cache: dict = {}
    a = resolve_part_class(
        _kc(value='MysteryX', pins=((1, 'A'), (2, 'B'))), unknown_cache=cache,
    )
    b = resolve_part_class(
        _kc(value='MysteryX', pins=((1, 'A'), (2, 'B'))), unknown_cache=cache,
    )
    assert a is b
