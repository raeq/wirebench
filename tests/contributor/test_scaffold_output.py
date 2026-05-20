"""Static + import-time checks on the scaffold's component output.

A scaffolded component file must satisfy *every framework rule by
construction* — no manual edit required to make `__slots__`, the
required ClassVars, the port shape, the registry decoration, or the
refdes-bearing surface conform.  These tests are the regression
boundary: if a future refactor of the scaffold drops a ClassVar or
forgets `__slots__`, the breach is caught here.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ._scaffold_harness import (
    chip_spec,
    materialise_and_load,
    passive_spec,
    render_component,
    unique_class_name,
)


REQUIRED_CLASSVARS = (
    'REFDES_PREFIX',
    'FOOTPRINT',
    'PIN_NUMBERS',
    'LAYOUT',
    'VERIFY',
    'GOTCHAS',
)


# ============================================================ passive


def test_passive_scaffold_renders_parseable_python(tmp_path: Path) -> None:
    """`render_component` must produce valid Python — no syntax errors,
    no malformed f-strings.  Catches template-string regressions
    without running pytest in a subprocess."""
    text = render_component(passive_spec(unique_class_name('PassiveParse')))
    ast.parse(text)


def test_passive_scaffold_declares_slots(tmp_path: Path) -> None:
    paths, component_module, _ = materialise_and_load(
        passive_spec(), tmp_path,
    )
    text = paths['component'].read_text()
    assert "__slots__ = (" in text, (
        "Scaffolded component must declare __slots__ — physical "
        "components cannot grow attributes at runtime."
    )


@pytest.mark.parametrize('classvar', REQUIRED_CLASSVARS)
def test_passive_scaffold_declares_all_required_classvars(
    classvar: str, tmp_path: Path,
) -> None:
    """Every component must surface the six ClassVars the framework
    reads downstream (refdes prefix, footprint, pin numbers, layout,
    verify, gotchas) — the scaffold can't omit any."""
    paths, component_module, _ = materialise_and_load(
        passive_spec(), tmp_path,
    )
    text = paths['component'].read_text()
    assert f"{classvar}:" in text or f"{classvar} =" in text, (
        f"Scaffolded component is missing required ClassVar "
        f"{classvar!r}."
    )


def test_passive_scaffold_constructs_cleanly(tmp_path: Path) -> None:
    """Loading and instantiating the scaffolded class must succeed
    without manual edits — the framework's construction-time invariants
    pass by default."""
    spec = passive_spec()
    paths, component_module, _ = materialise_and_load(spec, tmp_path)
    cls = getattr(component_module, spec.class_name)
    instance = cls(refdes_number=1)
    assert instance.refdes == f"{spec.refdes_prefix}1"
    assert set(instance.ports) == {p.name for p in spec.pins}


def test_passive_scaffold_registers_with_framework_registry(
    tmp_path: Path,
) -> None:
    """The scaffold emits `@register('ClassName')` so the class shows up
    in the framework registry — required for `.wirebench` round-trip."""
    from framework.registry import is_registered
    spec = passive_spec()
    _, component_module, _ = materialise_and_load(spec, tmp_path)
    cls = getattr(component_module, spec.class_name)
    assert is_registered(cls), (
        f"{spec.class_name} did not land in the framework registry — "
        "`@register(...)` decoration is missing or broken."
    )


def test_passive_scaffold_updates_init_all(tmp_path: Path) -> None:
    """Re-export in the kind subpackage `__init__.py` so callers can
    do `from components.passives import ClassName`."""
    spec = passive_spec()
    paths, _, _ = materialise_and_load(spec, tmp_path)
    init_text = paths['init'].read_text()
    assert spec.class_name in init_text, (
        "Scaffolded class is not re-exported from the kind's "
        "__init__.py — `from components.passives import …` won't see "
        "it without manual editing."
    )


# =============================================================== chip


def test_chip_scaffold_constructs_cleanly(tmp_path: Path) -> None:
    """A scaffolded chip must construct without `PartConfigurationError`
    — `Chip.__init__` enforces *every OUT pin is internally driven*
    by a cell, and the scaffold satisfies that by wiring an
    `IdleDriver` to each OUT pin's internal face."""
    spec = chip_spec()
    paths, component_module, _ = materialise_and_load(spec, tmp_path)
    cls = getattr(component_module, spec.class_name)
    instance = cls(refdes_number=1)
    assert instance.refdes == f"{spec.refdes_prefix}1"
    # Every declared external pin surfaces on the chip's ports map.
    for pin in spec.pins:
        assert pin.name in instance.ports


def test_chip_scaffold_drives_every_out_pin_via_a_cell(
    tmp_path: Path,
) -> None:
    """`Chip._assert_every_out_pin_is_internally_driven` would refuse
    the scaffold's output if any OUT pin's internal face had no
    cell-side driver.  The scaffold passes this check by construction
    via an `IdleDriver` per OUT pin."""
    spec = chip_spec()
    _, component_module, _ = materialise_and_load(spec, tmp_path)
    cls = getattr(component_module, spec.class_name)
    # Construction would have raised PartConfigurationError if the
    # invariant didn't hold.
    instance = cls(refdes_number=1)
    # Driving the chip via __call__ + evaluate() should leave the OUT
    # pin at the IdleDriver's idle value (False for Digital).
    instance(in_=True)
    assert instance.ports['out'].value is False


def test_chip_scaffold_implements_concrete_call(tmp_path: Path) -> None:
    """`Chip.__call__` is abstract; a scaffold that didn't override it
    would fail at `cls(refdes_number=1)` with TypeError.  The chip
    template emits a concrete `__call__` that drives every IN/BIDIR
    pin from its argument."""
    spec = chip_spec()
    paths, component_module, _ = materialise_and_load(spec, tmp_path)
    text = paths['component'].read_text()
    assert "def __call__(" in text
    # The signature must mention the IN pin name (concrete, not abstract).
    assert "in_:" in text


def test_chip_scaffold_declares_chip_as_base(tmp_path: Path) -> None:
    """The chip kind inherits from `Chip`; the passive kind from
    `Part`.  Picking the right base class is the friction the scaffold
    machine-applies."""
    paths, component_module, _ = materialise_and_load(chip_spec(), tmp_path)
    text = paths['component'].read_text()
    assert 'from framework.chip import Chip' in text
    assert '(Chip)' in text
    assert 'super().__init__(' in text, (
        "Chip scaffold must call `super().__init__(pins=..., cells=...)` "
        "so `Chip.__init__` builds the port map and validates the "
        "OUT-pin invariant."
    )


# =============================================== name → filename mapping


@pytest.mark.parametrize(
    'class_name,expected_filename',
    [
        ('LM7806',    'lm7806'),
        ('SN74HC04',  'sn74hc04'),
        ('ATmega328P', 'atmega328p'),
        ('MyChip',    'my_chip'),
        ('HTTPServer', 'http_server'),
    ],
)
def test_class_name_to_filename_handles_acronyms(
    class_name: str, expected_filename: str,
) -> None:
    """Acronym-heavy part names map to the conventional Python
    file-naming style: `LM7806` → `lm7806.py`, not `l_m7806.py`;
    `SN74HC04` → `sn74hc04.py`, not `s_n74_h_c04.py`.  The wirebench
    catalogue's existing file naming is the reference (see
    `src/components/chips/atmega328p.py`, `sn74hc04.py`, etc.)."""
    from ._scaffold_harness import _snake_case
    assert _snake_case(class_name) == expected_filename


# =================================================== refused overwrite


def test_scaffold_refuses_to_overwrite_existing_component(
    tmp_path: Path,
) -> None:
    """A second scaffold call against the same name raises rather than
    silently clobbering existing work."""
    spec = passive_spec(unique_class_name('OverwriteGuard'))
    materialise_and_load(spec, tmp_path)
    with pytest.raises(SystemExit, match='Refusing to overwrite'):
        materialise_and_load(spec, tmp_path)
