"""Shared utilities for the scaffold tests.

Loading the scaffolded files via `importlib.util.spec_from_file_location`
keeps the real `components.passives.*` import namespace untouched —
otherwise a scaffold-generated module would shadow the project's
real components when other tests subsequently `from components.passives
import …`.  Each test gets a unique class name to avoid registry
collisions across runs.
"""
from __future__ import annotations

import importlib.util
import sys
import types
import uuid
from pathlib import Path

# Import the scaffold module so tests can call into it directly.
# pyproject.toml puts `scripts/` outside `pythonpath`; load it by
# absolute file path.
_SCAFFOLD_PATH = (
    Path(__file__).resolve().parents[2] / 'scripts' / 'scaffold_component.py'
)
_spec = importlib.util.spec_from_file_location(
    '_scaffold_component_under_test', _SCAFFOLD_PATH,
)
assert _spec is not None and _spec.loader is not None
scaffold_component = importlib.util.module_from_spec(_spec)
# Register in sys.modules *before* exec — dataclass(@frozen=True)
# inside scaffold_component reads `sys.modules[cls.__module__]` while
# constructing the dataclass, and would crash with AttributeError
# (None.__dict__) otherwise.
sys.modules['_scaffold_component_under_test'] = scaffold_component
_spec.loader.exec_module(scaffold_component)

# Re-export the public surface so tests can write
# `from ._scaffold_harness import ComponentSpec, …`.
ComponentSpec = scaffold_component.ComponentSpec
PinSpec = scaffold_component.PinSpec
write_scaffold = scaffold_component.write_scaffold
render_component = scaffold_component.render_component
render_test_stub = scaffold_component.render_test_stub
_snake_case = scaffold_component._snake_case


def unique_class_name(prefix: str = 'Scaffolded') -> str:
    """A CamelCase class name no other test or registry entry will collide with."""
    return f"{prefix}{uuid.uuid4().hex[:10].capitalize()}"


def passive_spec(class_name: str | None = None) -> ComponentSpec:
    """Canonical two-terminal passive — the shape contributors will
    scaffold most often (an LED, a resistor, a thermistor)."""
    return ComponentSpec(
        class_name=class_name or unique_class_name('PassiveSm'),
        kind='passive',
        refdes_prefix='R',
        footprint='Test_SMD:Test_0603',
        pins=(
            PinSpec(name='t1', direction='bidir', signal_type='Analog'),
            PinSpec(name='t2', direction='bidir', signal_type='Analog'),
        ),
        description='Scaffolded test passive — used by the contributor suite.',
    )


def chip_spec(class_name: str | None = None) -> ComponentSpec:
    """A minimal chip shape: power + ground + one digital input + one
    digital output.  Exercises the OUT-pin code path.

    Supply pins (`vcc`, `gnd`) are declared `Analog` because the
    framework's name-based pin-function inference classifies any
    `VCC` / `VDD` / `GND` / `VSS` (case-insensitive) as POWER /
    GROUND, and those functions require an `Analog` signal_type."""
    return ComponentSpec(
        class_name=class_name or unique_class_name('ChipSm'),
        kind='chip',
        refdes_prefix='U',
        footprint='Package_DIP:DIP-4_W7.62mm',
        pins=(
            PinSpec(name='vcc', direction='in',  signal_type='Analog'),
            PinSpec(name='gnd', direction='in',  signal_type='Analog'),
            PinSpec(name='in_', direction='in',  signal_type='Digital'),
            PinSpec(name='out', direction='out', signal_type='Digital'),
        ),
        description='Scaffolded test chip — used by the contributor suite.',
    )


def load_module_from_path(
    module_name: str,
    file_path: Path,
) -> types.ModuleType:
    """Load a Python file as a module under `module_name`, registering
    it in `sys.modules` so subsequent imports referencing that name
    resolve to this module (used so the scaffolded test stub's
    `from components.<kind>s.<snake> import <Class>` finds the loaded
    scaffold component instead of failing because the path was never
    on `sys.path`)."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {file_path} as {module_name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def materialise_and_load(
    spec: ComponentSpec, root: Path,
) -> tuple[dict[str, Path], types.ModuleType, types.ModuleType]:
    """Run the scaffold under `root`, then load both the generated
    component and its test stub, exposing them as live modules ready
    for assertion or test-function invocation.

    Returns (paths, component_module, test_module).
    """
    paths = write_scaffold(spec, root)
    snake = _snake_case(spec.class_name)
    component_module_name = f'components.{spec.kind}s.{snake}'
    component_module = load_module_from_path(
        component_module_name, paths['component'],
    )
    test_module_name = (
        f'_scaffold_test_stub.{spec.kind}.{snake}_{uuid.uuid4().hex[:6]}'
    )
    test_module = load_module_from_path(test_module_name, paths['test'])
    return paths, component_module, test_module
