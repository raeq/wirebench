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
    """A scaffolded chip with an OUT pin still constructs — `evaluate()`
    drives every OUT pin with a placeholder so the framework's
    OUT-pin-must-be-driven invariant passes by default."""
    spec = chip_spec()
    paths, component_module, _ = materialise_and_load(spec, tmp_path)
    cls = getattr(component_module, spec.class_name)
    instance = cls(refdes_number=1)
    assert instance.refdes == f"{spec.refdes_prefix}1"
    # OUT pin is driven by evaluate() — exercise that path too.
    instance.evaluate()
    assert instance.ports['out'].value is False  # placeholder for Digital OUT


def test_chip_scaffold_declares_chip_as_base(tmp_path: Path) -> None:
    """The chip kind inherits from `Chip`; the passive kind from
    `Part`.  Picking the right base class is the friction the scaffold
    machine-applies."""
    paths, component_module, _ = materialise_and_load(chip_spec(), tmp_path)
    text = paths['component'].read_text()
    assert 'from framework.chip import Chip' in text
    assert '(Chip)' in text


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
