"""The scaffold's test stub must pass against the scaffold's own class
output — *no manual edit needed* to make the construction /
port-shape / signal-type assertions pass.

We invoke the generated test functions directly rather than spawning
a pytest subprocess: the stub's tests are simple `def test_*()` shapes
with no fixtures, so calling them in-process is faster and equivalent.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from ._scaffold_harness import (
    chip_spec,
    materialise_and_load,
    passive_spec,
)


def _run_every_test(test_module) -> int:
    """Call each `test_*` function in `test_module` and count how many
    ran.  Any failed assertion bubbles up as a `pytest.fail`-equivalent
    AssertionError, surfacing in the surrounding test's report."""
    count = 0
    for name in sorted(dir(test_module)):
        if not name.startswith('test_'):
            continue
        fn = getattr(test_module, name)
        if not callable(fn):
            continue
        fn()
        count += 1
    return count


def test_passive_scaffold_test_stub_passes(tmp_path: Path) -> None:
    """The two-terminal passive's scaffolded test stub must pass
    against the scaffolded class — the regression boundary for
    *the boilerplate is correct by construction*."""
    spec = passive_spec()
    _, _, test_module = materialise_and_load(spec, tmp_path)
    ran = _run_every_test(test_module)
    assert ran >= 3, (
        f"Expected at least construction, port_shape, and "
        f"port_directions tests; only {ran} ran."
    )


def test_chip_scaffold_test_stub_passes(tmp_path: Path) -> None:
    """The chip-with-OUT-pin scaffolded test stub must also pass
    without contributor edits."""
    spec = chip_spec()
    _, _, test_module = materialise_and_load(spec, tmp_path)
    ran = _run_every_test(test_module)
    assert ran >= 3


@pytest.mark.parametrize(
    'spec_factory',
    [passive_spec, chip_spec],
    ids=['passive', 'chip'],
)
def test_test_stub_asserts_each_pin(
    tmp_path: Path, spec_factory,
) -> None:
    """Every declared pin gets a direction + signal_type assertion in
    the stub — the contributor sees one line per pin so renaming or
    redirecting a pin doesn't go silently."""
    spec = spec_factory()
    paths, _, _ = materialise_and_load(spec, tmp_path)
    text = paths['test'].read_text()
    for pin in spec.pins:
        assert f"part.ports['{pin.name}'].direction" in text, (
            f"Test stub missing direction assertion for pin "
            f"{pin.name!r}."
        )
        assert f"part.ports['{pin.name}'].signal_type" in text, (
            f"Test stub missing signal_type assertion for pin "
            f"{pin.name!r}."
        )
