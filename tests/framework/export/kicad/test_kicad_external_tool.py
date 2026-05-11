"""Optional external-tool test for KiCad netlist.

KiCad currently lacks a CLI gate for netlist import that exits
non-zero on parse errors (`kicad-cli sch import-netlist` is on the
roadmap). Until then this test simply asserts `kicad-cli` is invokable
when present; skip otherwise.

If a test fails because a renderer is missing or incorrect, the fix
is to add or correct the renderer — not to lower the assertion bar.
"""
from __future__ import annotations

import shutil
import subprocess

import pytest


@pytest.mark.skipif(not shutil.which('kicad-cli'), reason='kicad-cli not installed')
def test_kicad_cli_invokable():
    result = subprocess.run(
        ['kicad-cli', '--version'],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0
